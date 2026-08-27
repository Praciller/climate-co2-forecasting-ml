from __future__ import annotations

import json
import hashlib
import platform
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.artifacts import sha256_file, write_manifest
from src.evaluation.intervals import (
    calibrate_residual_radius,
    evaluate_prediction_interval,
    symmetric_prediction_interval,
)
from src.evaluation.metrics import calculate_metrics
from src.evaluation.rolling_origin_evaluation import (
    build_development_backtest,
    evaluate_final_test_interval,
    select_robust_model,
    write_evaluation_reports,
)
from src.evaluation.temporal_contract import validate_temporal_contract
from src.models.common import PREDICTIONS_DIR, load_modeling_data
from src.models.train_statistical import fit_exponential_smoothing, fit_sarima
from src.utils.config import (
    FEATURE_DATA_PATH,
    FIGURES_DIR,
    FORECAST_METRICS_PATH,
    INTERVAL_NOMINAL_COVERAGE,
    INTERVAL_REPORT_PATH,
    LIVE_FORECAST_PATH,
    MAX_FORECAST_HORIZON,
    MODEL_MANIFEST_PATH,
    MONTHLY_DATA_PATH,
    PREPROCESSING_VERSION,
    RAW_DATA_PATH,
    REPORTS_DIR,
    RESIDUAL_REPORT_PATH,
    SEASONAL_PERIOD,
    SPLIT_BOUNDARIES,
)
from src.utils.io import read_json, write_json


CANDIDATE_FILES = {
    "Naive": "naive.csv",
    "Moving Average": "moving_average.csv",
    "Seasonal Naive": "seasonal_naive.csv",
    "Exponential Smoothing": "exponential_smoothing.csv",
    "SARIMA": "sarima.csv",
    "Random Forest": "random_forest.csv",
    "Gradient Boosting": "gradient_boosting.csv",
}

MODEL_NOTES = {
    "Naive": "Observed value at the previous origin",
    "Moving Average": "Trailing 12-month observed mean",
    "Seasonal Naive": "Observed value 12 months before the origin",
    "Exponential Smoothing": "Additive trend and seasonality; refit each origin",
    "SARIMA": "Fixed parameters; state updated with each observation",
    "Random Forest": "One-step lag and rolling features; no extrapolation",
    "Gradient Boosting": "One-step lag and rolling features; no extrapolation",
}

# Used only after validation MAE and RMSE. It makes ties deterministic and
# explicitly prefers simpler, easier-to-audit models.
COMPLEXITY_ORDER = {
    "Naive": 0,
    "Seasonal Naive": 1,
    "Moving Average": 2,
    "Exponential Smoothing": 3,
    "SARIMA": 4,
    "Gradient Boosting": 5,
    "Random Forest": 6,
}


def load_predictions(evaluation_split: str) -> dict[str, pd.DataFrame]:
    directory = (
        PREDICTIONS_DIR
        if evaluation_split == "test"
        else PREDICTIONS_DIR / evaluation_split
    )
    predictions: dict[str, pd.DataFrame] = {}
    missing = []
    for model_name, filename in CANDIDATE_FILES.items():
        path = directory / filename
        if not path.exists():
            missing.append(path.as_posix())
            continue
        frame = pd.read_csv(
            path,
            parse_dates=["date", "origin_date"],
        ).set_index("date")
        predictions[model_name] = frame
    if missing:
        raise FileNotFoundError(
            "Missing prediction artifacts: "
            + ", ".join(missing)
            + ". Run the candidate trainers first."
        )
    verify_prediction_contract(predictions, evaluation_split)
    return predictions


def verify_prediction_contract(
    predictions: dict[str, pd.DataFrame],
    evaluation_split: str,
) -> pd.DatetimeIndex:
    reference_name = next(iter(predictions))
    reference = predictions[reference_name]
    required = {
        "origin_date",
        "horizon",
        "evaluation_split",
        "protocol",
        "refit_at_origin",
        "actual",
        "prediction",
    }
    if not required.issubset(reference.columns):
        raise ValueError("Prediction artifact is missing governed columns.")
    if reference.index.has_duplicates or not reference.index.is_monotonic_increasing:
        raise ValueError("Prediction dates must be unique and increasing.")
    for model_name, frame in predictions.items():
        if not reference.index.equals(frame.index):
            raise ValueError(f"{model_name} does not use the shared target dates.")
        if not np.allclose(reference["actual"], frame["actual"]):
            raise ValueError(f"{model_name} actual values do not match.")
        if not (frame["evaluation_split"] == evaluation_split).all():
            raise ValueError(f"{model_name} has the wrong evaluation split.")
        if not (frame["horizon"] == 1).all():
            raise ValueError(f"{model_name} is not a one-step artifact.")
        expected_origins = frame.index - pd.offsets.MonthEnd(1)
        if not pd.DatetimeIndex(frame["origin_date"]).equals(expected_origins):
            raise ValueError(f"{model_name} origin alignment is invalid.")
        if not np.isfinite(frame[["actual", "prediction"]]).all().all():
            raise ValueError(f"{model_name} contains non-finite values.")
    return reference.index


def metric_payload(
    predictions: dict[str, pd.DataFrame],
    training: pd.Series,
) -> dict[str, dict[str, float | None]]:
    return {
        model_name: calculate_metrics(
            frame["actual"].to_numpy(),
            frame["prediction"].to_numpy(),
            training.to_numpy(),
        )
        for model_name, frame in predictions.items()
    }


def select_model(
    validation_metrics: dict[str, dict[str, float | None]],
) -> str:
    return min(
        validation_metrics,
        key=lambda name: (
            float(validation_metrics[name]["mae"]),
            float(validation_metrics[name]["rmse"]),
            COMPLEXITY_ORDER[name],
        ),
    )


def conformal_radius(
    residuals: pd.Series,
    nominal_coverage: float,
) -> float:
    return calibrate_residual_radius(residuals, nominal_coverage)


def interval_evidence(
    validation: pd.DataFrame,
    test: pd.DataFrame,
    *,
    calibration_residuals: pd.Series | None = None,
    calibration_end: pd.Timestamp | None = None,
) -> tuple[dict[str, Any], float]:
    residuals = (
        validation["actual"] - validation["prediction"]
        if calibration_residuals is None
        else calibration_residuals
    )
    radius = calibrate_residual_radius(
        residuals,
        INTERVAL_NOMINAL_COVERAGE,
        development_end=calibration_end,
    )
    lower, upper = symmetric_prediction_interval(test["prediction"], radius)
    measured = evaluate_prediction_interval(
        test["actual"],
        test["prediction"],
        lower,
        upper,
        nominal_coverage=INTERVAL_NOMINAL_COVERAGE,
    )
    if calibration_end is not None and test.index.min() <= pd.Timestamp(
        calibration_end
    ):
        raise ValueError("Final-test rows must be after the calibration boundary.")
    report = {
        "method": (
            "development rolling-origin absolute-residual quantile"
            if calibration_residuals is not None
            else "split-conformal absolute validation residual"
        ),
        "nominal_coverage": INTERVAL_NOMINAL_COVERAGE,
        "calibration_split": (
            "train/validation development folds"
            if calibration_residuals is not None
            else "validation"
        ),
        "calibration_end": (
            None
            if calibration_end is None
            else pd.Timestamp(calibration_end).date().isoformat()
        ),
        "calibration_samples": len(residuals),
        "evaluation_split": "final_test",
        "evaluation_samples": len(test),
        "observed_test_coverage": measured["empirical_coverage"],
        "empirical_coverage": measured["empirical_coverage"],
        "average_test_width_ppm": measured["average_width"],
        "radius_ppm": radius,
        "horizon": 1,
        "limitations": (
            "Coverage is measured for rolling one-step forecasts only. "
            "The same development-derived radius is shown around fixed-origin "
            "multi-step API projections without a multi-horizon coverage claim."
        ),
    }
    return report, radius


def residual_evidence(frame: pd.DataFrame, model_name: str) -> dict[str, Any]:
    residuals = frame["actual"] - frame["prediction"]
    largest = residuals.abs().nlargest(5).index
    return {
        "model": model_name,
        "source": "final-test rolling-origin one-step forecasts",
        "samples": len(residuals),
        "mean_residual_ppm": float(residuals.mean()),
        "residual_std_ppm": float(residuals.std(ddof=0)),
        "lag_1_autocorrelation": (
            None if len(residuals) < 2 else float(residuals.autocorr(lag=1))
        ),
        "largest_absolute_errors": [
            {
                "date": timestamp.date().isoformat(),
                "residual_ppm": float(residuals.loc[timestamp]),
                "absolute_error_ppm": float(abs(residuals.loc[timestamp])),
            }
            for timestamp in largest
        ],
        "limitations": (
            "Diagnostics describe forecast errors on this historical test "
            "period; they are not causal or scientific event attribution."
        ),
    }


def forecast_selected(
    model_name: str,
    history: pd.Series,
    horizon: int,
) -> np.ndarray:
    if model_name == "Exponential Smoothing":
        return np.asarray(
            fit_exponential_smoothing(history).forecast(horizon),
            dtype=float,
        )
    if model_name == "SARIMA":
        return np.asarray(fit_sarima(history).forecast(horizon), dtype=float)
    if model_name == "Naive":
        return np.repeat(float(history.iloc[-1]), horizon)
    if model_name == "Moving Average":
        return np.repeat(float(history.iloc[-SEASONAL_PERIOD:].mean()), horizon)
    if model_name == "Seasonal Naive":
        values = history.iloc[-SEASONAL_PERIOD:].to_numpy(dtype=float)
        return np.resize(values, horizon)
    raise ValueError(
        f"{model_name} is not eligible for fixed-origin recursive serving."
    )


def save_live_forecast(
    model_name: str,
    history: pd.Series,
    radius: float,
    interval_report: dict[str, Any],
) -> None:
    predictions = forecast_selected(
        model_name,
        history,
        MAX_FORECAST_HORIZON,
    )
    dates = pd.date_range(
        history.index.max() + pd.offsets.MonthEnd(1),
        periods=MAX_FORECAST_HORIZON,
        freq="ME",
    )
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    write_json(
        LIVE_FORECAST_PATH,
        {
            "schema_version": "2.0.0",
            "model_name": model_name,
            "model_version": "governed-2026-07",
            "generated_at": generated_at,
            "forecast_origin": history.index.max().date().isoformat(),
            "training_rows": len(history),
            "training_end": history.index.max().date().isoformat(),
            "frequency": "month-end",
            "protocol": "fixed-origin multi-step forecast",
            "interval": {
                "method": interval_report["method"],
                "nominal_coverage": interval_report["nominal_coverage"],
                "radius_ppm": radius,
                "coverage_scope": "rolling one-step final test only",
            },
            "limitations": [
                "The historical packaged dataset ends in December 2001.",
                "Forecasts are educational projections, not current monitoring.",
                "Interval coverage is not established beyond one step.",
            ],
            "forecast": [
                {
                    "date": date.date().isoformat(),
                    "prediction": float(prediction),
                    "lower": float(prediction - radius),
                    "upper": float(prediction + radius),
                }
                for date, prediction in zip(dates, predictions, strict=True)
            ],
        },
    )


def build_comparison_markdown(
    selected_model: str,
    validation_metrics: dict[str, dict[str, float | None]],
    test_metrics: dict[str, dict[str, float | None]],
    interval_report: dict[str, Any],
    lstm_smoke: dict[str, Any],
) -> str:
    lines = [
        "# Model Comparison",
        "",
        "Candidate selection uses mean MAE across development rolling-origin "
        "folds. The "
        "selected model is then reported on the untouched final test period.",
        "",
        f"- Selected model: **{selected_model}**",
        "- Tie-break: mean fold RMSE, then explicit simplicity order",
        "- Detailed fold evidence: `rolling_origin_evaluation.md`",
        f"- Final-test interval coverage: "
        f"**{interval_report['observed_test_coverage']:.1%}** "
        f"at {interval_report['nominal_coverage']:.0%} nominal "
        f"({interval_report['evaluation_samples']} one-step forecasts)",
        "",
        "| Model | Validation MAE | Validation RMSE | Test MAE | Test RMSE | "
        "Test sMAPE | Test MASE | Notes |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for name in sorted(
        validation_metrics,
        key=lambda item: float(validation_metrics[item]["mae"]),
    ):
        validation = validation_metrics[name]
        test = test_metrics[name]
        selected = " **Selected**." if name == selected_model else ""
        lines.append(
            f"| {name} | {validation['mae']:.3f} | "
            f"{validation['rmse']:.3f} | {test['mae']:.3f} | "
            f"{test['rmse']:.3f} | {test['smape']:.3f}% | "
            f"{test['mase']:.3f} |{selected} {MODEL_NOTES[name]} |"
        )
    lines.extend(
        [
            "",
            "## Neural pipeline smoke",
            "",
            "The PyTorch LSTM is excluded from selection and the candidate table. "
            "Its bounded run verifies sequence construction, train-only scaling, "
            "validation monitoring, checkpoint restoration, and CPU execution.",
            "",
            f"- Evidence type: `{lstm_smoke.get('evidence_type', 'missing')}`",
            f"- Epochs completed: {lstm_smoke.get('epochs_completed', 'unknown')}",
            "- Ranking eligible: No",
        ]
    )
    return "\n".join(lines)


def save_evaluation_figures(
    predictions: dict[str, pd.DataFrame],
    selected_model: str,
) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    actual = next(iter(predictions.values()))["actual"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(actual.index, actual, color="#27364a", linewidth=2.2, label="Actual")
    for model_name, frame in predictions.items():
        ax.plot(frame.index, frame["prediction"], linewidth=1.15, label=model_name)
    ax.set_title("Rolling one-step candidate forecasts: final test period")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "forecast_comparison.png", dpi=160)
    plt.close(fig)

    residuals = actual - predictions[selected_model]["prediction"]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.axhline(0, color="#68778b", linewidth=1)
    ax.plot(residuals.index, residuals, color="#287eb8")
    ax.set_title(f"Out-of-sample one-step residuals: {selected_model}")
    ax.set_ylabel("Actual - prediction (ppm)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "residual_plot.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(residuals, bins=14, color="#287eb8", alpha=0.85)
    ax.set_title(f"Final-test error distribution: {selected_model}")
    ax.set_xlabel("Residual (ppm)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "error_distribution.png", dpi=160)
    plt.close(fig)


def git_identifier() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_worktree_dirty() -> bool | None:
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(output.strip())
    except (OSError, subprocess.CalledProcessError):
        return None


def source_tree_fingerprint() -> str:
    digest = hashlib.sha256()
    source_root = RAW_DATA_PATH.parents[2] / "src"
    for path in sorted(source_root.rglob("*.py")):
        digest.update(path.relative_to(source_root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> None:
    monthly, features = load_modeling_data()
    temporal_contract = validate_temporal_contract(monthly, features)
    validation_predictions = load_predictions("validation")
    test_predictions = load_predictions("test")
    validation_dates = verify_prediction_contract(
        validation_predictions,
        "validation",
    )
    test_dates = verify_prediction_contract(test_predictions, "test")

    train_history = monthly.loc[monthly.index < validation_dates.min(), "co2"]
    development_history = monthly.loc[monthly.index < test_dates.min(), "co2"]
    validation_metrics = metric_payload(validation_predictions, train_history)
    test_metrics = metric_payload(test_predictions, development_history)
    rolling_origin = build_development_backtest(monthly, features)
    selected_model = select_robust_model(rolling_origin.aggregate)
    selected_validation = validation_predictions[selected_model]
    selected_test = test_predictions[selected_model]

    interval_report, radius = interval_evidence(
        selected_validation,
        selected_test,
        calibration_residuals=rolling_origin.residuals_for(selected_model),
        calibration_end=rolling_origin.development_end,
    )
    rolling_interval_report, _ = evaluate_final_test_interval(
        rolling_origin,
        selected_test,
        selected_model,
        nominal_coverage=INTERVAL_NOMINAL_COVERAGE,
    )
    write_evaluation_reports(
        rolling_origin,
        rolling_interval_report,
        selected_model,
    )
    residual_report = residual_evidence(selected_test, selected_model)
    lstm_smoke = read_json(REPORTS_DIR / "lstm_metrics.json", {})

    metrics_payload = {
        "schema_version": "2.0.0",
        "protocol": {
            "name": "rolling-origin one-step-ahead",
            "training_window": "expanding observed history",
            "horizon": 1,
            "actual_previous_observations_available": True,
            "split_boundaries": SPLIT_BOUNDARIES,
        },
        "temporal_contract": temporal_contract,
        "selection": {
            "selected_model": selected_model,
            "metric": "mean rolling-origin development-fold MAE",
            "tie_break": "mean fold RMSE, then explicit simplicity order",
            "evidence_split": "train/validation development folds",
            "rationale": (
                f"{selected_model} had the lowest mean development-fold MAE "
                "among ranking-eligible candidates."
            ),
        },
        "validation": {
            "start": validation_dates.min().date().isoformat(),
            "end": validation_dates.max().date().isoformat(),
            "samples": len(validation_dates),
            "models": validation_metrics,
        },
        "final_test": {
            "start": test_dates.min().date().isoformat(),
            "end": test_dates.max().date().isoformat(),
            "samples": len(test_dates),
            "models": test_metrics,
        },
        "rolling_origin": rolling_origin.as_dict(),
        "smoke_evidence": {"PyTorch LSTM": lstm_smoke},
    }
    write_json(FORECAST_METRICS_PATH, metrics_payload)
    write_json(INTERVAL_REPORT_PATH, interval_report)
    write_json(RESIDUAL_REPORT_PATH, residual_report)
    save_live_forecast(
        selected_model,
        monthly["co2"],
        radius,
        interval_report,
    )
    (REPORTS_DIR / "model_comparison.md").write_text(
        build_comparison_markdown(
            selected_model,
            validation_metrics,
            test_metrics,
            interval_report,
            lstm_smoke,
        ),
        encoding="utf-8",
    )
    save_evaluation_figures(test_predictions, selected_model)

    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    raw = pd.read_csv(RAW_DATA_PATH, parse_dates=["date"])
    write_manifest(
        MODEL_MANIFEST_PATH,
        {
            "generated_at": generated_at,
            "code_commit": git_identifier(),
            "working_tree_dirty": git_worktree_dirty(),
            "source_tree_sha256": source_tree_fingerprint(),
            "dataset": {
                "name": "Mauna Loa Weekly Atmospheric CO2 Data",
                "source_module": "statsmodels.datasets.co2",
                "source_package_version": version("statsmodels"),
                "raw_sha256": sha256_file(RAW_DATA_PATH),
                "weekly_calendar_rows": len(raw),
                "observed_values": int(raw["co2"].notna().sum()),
                "missing_values": int(raw["co2"].isna().sum()),
                "period": (f"{raw['date'].min().date()} to {raw['date'].max().date()}"),
                "frequency": "weekly W-SAT",
                "unit": "ppmv",
                "historical_only": True,
            },
            "preprocessing": {
                "version": PREPROCESSING_VERSION,
                "monthly_aggregation": "month-end mean",
                "missing_month_strategy": "causal forward fill, maximum 3 months",
                "feature_contract": (
                    "lags and rolling statistics use only prior monthly values"
                ),
            },
            "split_boundaries": SPLIT_BOUNDARIES,
            "forecasting_protocol": metrics_payload["protocol"],
            "selected_model": metrics_payload["selection"],
            "interval": interval_report,
            "runtime": {
                "python": platform.python_version(),
                "pandas": version("pandas"),
                "numpy": version("numpy"),
                "statsmodels": version("statsmodels"),
                "scikit_learn": version("scikit-learn"),
            },
            "trusted_artifacts_only": True,
        },
        {
            "raw_data": RAW_DATA_PATH,
            "monthly_data": MONTHLY_DATA_PATH,
            "feature_data": FEATURE_DATA_PATH,
            "forecast_metrics": FORECAST_METRICS_PATH,
            "interval_report": INTERVAL_REPORT_PATH,
            "residual_report": RESIDUAL_REPORT_PATH,
            "live_forecast": LIVE_FORECAST_PATH,
        },
    )
    print(
        json.dumps(
            {
                "selected_model": selected_model,
                "validation_mae": validation_metrics[selected_model]["mae"],
                "final_test_mae": test_metrics[selected_model]["mae"],
                "test_interval_coverage": interval_report["observed_test_coverage"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
