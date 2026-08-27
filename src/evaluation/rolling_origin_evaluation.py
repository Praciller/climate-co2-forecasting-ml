"""Generate governed rolling-origin and final-test interval evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.evaluation.intervals import (
    calibrate_residual_radius,
    evaluate_prediction_interval,
    symmetric_prediction_interval,
)
from src.evaluation.rolling_origin import (
    DEFAULT_BACKTEST_MODELS,
    RollingOriginBacktest,
    generate_expanding_folds,
    run_rolling_origin_backtest,
    select_robust_model,
)
from src.models.common import load_modeling_data
from src.utils.config import REPORTS_DIR, VALIDATION_END
from src.utils.io import write_json

ROLLING_ORIGIN_REPORT_PATH = REPORTS_DIR / "rolling_origin_evaluation.json"
ROLLING_ORIGIN_MARKDOWN_PATH = REPORTS_DIR / "rolling_origin_evaluation.md"
FORECAST_INTERVAL_REPORT_PATH = REPORTS_DIR / "forecast_interval_evaluation.json"
DEVELOPMENT_FOLD_HORIZON = 7


def build_development_backtest(
    monthly: pd.DataFrame,
    features: pd.DataFrame,
    *,
    horizon: int = DEVELOPMENT_FOLD_HORIZON,
) -> RollingOriginBacktest:
    """Run fixed-size, non-overlapping folds through validation only."""
    development_dates = features.index[features["split"].isin(["train", "validation"])]
    train_dates = features.index[features["split"] == "train"]
    folds = generate_expanding_folds(
        development_dates,
        development_end=VALIDATION_END,
        initial_train_size=len(train_dates),
        horizon=horizon,
        step_size=horizon,
    )
    return run_rolling_origin_backtest(
        monthly["co2"],
        folds,
        models=DEFAULT_BACKTEST_MODELS,
        development_end=VALIDATION_END,
    )


def build_rolling_origin_markdown(
    result: RollingOriginBacktest,
    selected_model: str,
) -> str:
    fold_horizon = result.folds[0]["horizon"]
    lines = [
        "# Rolling-Origin Evaluation",
        "",
        (
            "Development-only expanding-window backtesting uses chronological, "
            f"non-overlapping {fold_horizon}-month validation blocks. Each target is forecast "
            "one month after its permitted origin, then its actual value is appended "
            "to the next origin's history."
        ),
        "",
        f"- Fold count: **{len(result.folds)}**",
        f"- Development boundary: **{result.development_end.date()}**",
        f"- Models: {', '.join(result.models)}",
        f"- Robust development choice: **{selected_model}**",
        "- Selection key: mean fold MAE, mean fold RMSE, then simplicity",
        (
            "- Final governed/test rows are not used for folds, selection, or "
            "interval calibration."
        ),
        "",
        "## Temporal folds",
        "",
        "| Fold | Train range | Validation range | Horizon |",
        "|---:|---|---|---:|",
    ]
    for fold in result.folds:
        lines.append(
            f"| {fold['fold_id']} | {fold['train_start']} to "
            f"{fold['train_end']} | {fold['validation_start']} to "
            f"{fold['validation_end']} | {fold['horizon']} |"
        )
    lines.extend(
        [
            "",
            "## Aggregate metrics",
            "",
            (
                "Values are mean ± population standard deviation across folds; "
                "the median is retained in JSON for skewed fold distributions."
            ),
            "",
            "| Model | MAE | RMSE | sMAPE | MASE |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for model_name in sorted(
        result.aggregate,
        key=lambda name: result.aggregate[name]["mae"]["mean"],
    ):
        metrics = result.aggregate[model_name]
        lines.append(
            f"| {model_name} | {metrics['mae']['mean']:.3f} ± "
            f"{metrics['mae']['std']:.3f} | {metrics['rmse']['mean']:.3f} ± "
            f"{metrics['rmse']['std']:.3f} | {metrics['smape']['mean']:.3f}% ± "
            f"{metrics['smape']['std']:.3f} | {metrics['mase']['mean']:.3f} ± "
            f"{metrics['mase']['std']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation and limits",
            "",
            (
                f"**{selected_model}** has the lowest mean development-fold MAE in "
                "this bounded candidate set. This is robustness evidence for this "
                "historical series, not a universal model claim."
            ),
            "",
            (
                "The final governed/test period remains a one-time post-selection "
                "evaluation. Fold residuals are out-of-sample for their own origins, "
                "but temporal dependence and regime change mean formal exchangeable "
                "conformal guarantees should not be assumed."
            ),
        ]
    )
    return "\n".join(lines)


def evaluate_final_test_interval(
    result: RollingOriginBacktest,
    final_test: pd.DataFrame,
    selected_model: str,
    *,
    nominal_coverage: float,
) -> tuple[dict[str, Any], float]:
    """Calibrate from development folds and evaluate once on final test."""
    if selected_model not in result.predictions:
        raise ValueError(
            f"Selected model has no development residuals: {selected_model}."
        )
    if final_test.empty:
        raise ValueError("Final-test predictions must not be empty.")
    if not isinstance(final_test.index, pd.DatetimeIndex):
        raise TypeError("Final-test predictions must use a DatetimeIndex.")
    if final_test.index.min() <= result.development_end:
        raise ValueError("Final-test rows must be after the development boundary.")
    required = {"actual", "prediction"}
    if not required.issubset(final_test.columns):
        raise ValueError("Final-test predictions are missing actual or prediction.")

    calibration_residuals = result.residuals_for(selected_model)
    radius = calibrate_residual_radius(
        calibration_residuals,
        nominal_coverage,
        development_end=result.development_end,
    )
    lower, upper = symmetric_prediction_interval(
        final_test["prediction"].to_numpy(),
        radius,
    )
    evidence = evaluate_prediction_interval(
        final_test["actual"].to_numpy(),
        final_test["prediction"].to_numpy(),
        lower,
        upper,
        nominal_coverage=nominal_coverage,
    )
    report = {
        "method": "development rolling-origin absolute-residual quantile",
        "nominal_coverage": evidence["nominal_coverage"],
        "empirical_coverage": evidence["empirical_coverage"],
        "observed_test_coverage": evidence["empirical_coverage"],
        "covered_samples": evidence["covered_samples"],
        "calibration_split": "train/validation development folds",
        "calibration_end": result.development_end.date().isoformat(),
        "calibration_samples": len(calibration_residuals),
        "evaluation_split": "final_test",
        "evaluation_samples": evidence["samples"],
        "average_width_ppm": evidence["average_width"],
        "radius_ppm": radius,
        "horizon_behavior": {
            "1": {
                "samples": evidence["samples"],
                "empirical_coverage": evidence["empirical_coverage"],
                "average_width_ppm": evidence["average_width"],
            }
        },
        "limitations": (
            "This is a measured one-step prediction interval from development "
            "residuals. Fold residuals are time-dependent and may not be "
            "exchangeable; coverage is empirical for this historical final-test "
            "period and is not established for multi-step serving horizons."
        ),
    }
    return report, radius


def write_evaluation_reports(
    result: RollingOriginBacktest,
    interval_report: dict[str, Any],
    selected_model: str,
    *,
    rolling_origin_path: Path = ROLLING_ORIGIN_REPORT_PATH,
    rolling_origin_markdown_path: Path = ROLLING_ORIGIN_MARKDOWN_PATH,
    interval_path: Path = FORECAST_INTERVAL_REPORT_PATH,
) -> None:
    rolling_payload = result.as_dict()
    rolling_payload["selection"] = {
        "selected_model": selected_model,
        "metric": "mean fold MAE",
        "tie_break": "mean fold RMSE, then simplicity",
    }
    write_json(rolling_origin_path, rolling_payload)
    rolling_origin_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    rolling_origin_markdown_path.write_text(
        build_rolling_origin_markdown(result, selected_model),
        encoding="utf-8",
    )
    write_json(interval_path, interval_report)


def main() -> None:
    monthly, features = load_modeling_data()
    result = build_development_backtest(monthly, features)
    selected_model = select_robust_model(result.aggregate)
    test_path = (
        REPORTS_DIR
        / "predictions"
        / (selected_model.lower().replace(" ", "_") + ".csv")
    )
    final_test = pd.read_csv(test_path, parse_dates=["date"]).set_index("date")
    interval_report, _ = evaluate_final_test_interval(
        result,
        final_test,
        selected_model,
        nominal_coverage=0.90,
    )
    write_evaluation_reports(result, interval_report, selected_model)
    print(
        {
            "fold_count": len(result.folds),
            "selected_model": selected_model,
            "empirical_coverage": interval_report["empirical_coverage"],
        }
    )


if __name__ == "__main__":
    main()
