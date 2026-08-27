from __future__ import annotations

import json

import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.artifacts import refresh_manifest_artifact
from src.evaluation.evaluate_forecasts import conformal_radius
from src.models.common import PREDICTIONS_DIR, load_modeling_data, slugify_model_name
from src.utils.config import (
    ANOMALIES_PATH,
    FIGURES_DIR,
    FORECAST_METRICS_PATH,
    MODEL_MANIFEST_PATH,
    REPORTS_DIR,
)

ISOLATION_CONTAMINATION = 0.03
RESIDUAL_NOMINAL_COVERAGE = 0.99


def build_isolation_features(monthly: pd.DataFrame) -> pd.DataFrame:
    """Build bounded, forecast-time features without absolute level or year."""
    co2 = monthly["co2"]
    rolling_mean = co2.shift(1).rolling(12).mean()
    rolling_std = co2.shift(1).rolling(12).std(ddof=0)
    month_angle = 2 * np.pi * monthly.index.month / 12
    frame = pd.DataFrame(
        {
            "change_1": co2.diff(1),
            "change_12": co2.diff(12),
            "deviation_from_prior_mean": co2 - rolling_mean,
            "prior_rolling_std": rolling_std,
            "month_sin": np.sin(month_angle),
            "month_cos": np.cos(month_angle),
        },
        index=monthly.index,
    )
    return frame.replace([np.inf, -np.inf], np.nan).dropna()


def isolation_flags(
    development: pd.DataFrame,
    target: pd.DataFrame,
    *,
    contamination: float = ISOLATION_CONTAMINATION,
    seed: int = 42,
) -> tuple[pd.Series, pd.Series, float]:
    if not 0 < contamination < 0.5:
        raise ValueError("contamination must be between 0 and 0.5.")
    detector = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=seed,
    )
    detector.fit(development)
    development_scores = -detector.score_samples(development)
    threshold = float(
        np.quantile(development_scores, 1 - contamination, method="higher")
    )
    target_scores = pd.Series(
        -detector.score_samples(target),
        index=target.index,
        name="isolation_score",
    )
    return target_scores > threshold, target_scores, threshold


def main() -> None:
    monthly, features = load_modeling_data()
    metrics = json.loads(FORECAST_METRICS_PATH.read_text(encoding="utf-8"))
    selected_model = metrics["selection"]["selected_model"]
    slug = slugify_model_name(selected_model)
    validation = pd.read_csv(
        PREDICTIONS_DIR / "validation" / f"{slug}.csv",
        parse_dates=["date"],
    ).set_index("date")
    test = pd.read_csv(
        PREDICTIONS_DIR / f"{slug}.csv",
        parse_dates=["date"],
    ).set_index("date")

    validation_residuals = validation["actual"] - validation["prediction"]
    residual_threshold = conformal_radius(
        validation_residuals,
        RESIDUAL_NOMINAL_COVERAGE,
    )
    test_residuals = test["actual"] - test["prediction"]
    residual_flag = test_residuals.abs() > residual_threshold

    anomaly_features = build_isolation_features(monthly)
    development_index = features.index[
        features["split"].isin(["train", "validation"])
    ]
    test_index = features.index[features["split"] == "test"]
    development = anomaly_features.loc[
        anomaly_features.index.intersection(development_index)
    ]
    target = anomaly_features.loc[anomaly_features.index.intersection(test_index)]
    isolation_flag, scores, isolation_threshold = isolation_flags(
        development,
        target,
    )

    aligned = pd.DataFrame(index=test_index)
    aligned["co2"] = monthly.loc[test_index, "co2"]
    aligned["residual_ppm"] = test_residuals.reindex(test_index)
    aligned["residual_anomaly"] = residual_flag.reindex(
        test_index,
        fill_value=False,
    )
    aligned["isolation_score"] = scores.reindex(test_index)
    aligned["isolation_forest_anomaly"] = isolation_flag.reindex(
        test_index,
        fill_value=False,
    )
    aligned["is_anomaly"] = (
        aligned["residual_anomaly"] | aligned["isolation_forest_anomaly"]
    )
    anomalies = aligned[aligned["is_anomaly"]].copy()
    anomalies["methods"] = anomalies.apply(
        lambda row: "|".join(
            method
            for method, flagged in (
                ("Residual threshold", row["residual_anomaly"]),
                ("Isolation Forest", row["isolation_forest_anomaly"]),
            )
            if flagged
        ),
        axis=1,
    )
    anomalies.reset_index(names="date").to_csv(ANOMALIES_PATH, index=False)

    both = int(
        (
            aligned["residual_anomaly"]
            & aligned["isolation_forest_anomaly"]
        ).sum()
    )
    report = "\n".join(
        [
            "# Anomaly Signal Report",
            "",
            "These are exploratory statistical signals under selected methods "
            "and assumptions, not verified climate events.",
            "",
            "## Governed methods",
            "",
            f"- Residual source: {selected_model} rolling one-step forecasts",
            "- Residual threshold calibrated on validation only",
            f"- Residual threshold: {residual_threshold:.3f} ppm "
            f"({RESIDUAL_NOMINAL_COVERAGE:.0%} nominal)",
            "- Isolation Forest fit on train and validation only",
            "- Isolation features: changes, prior-window deviation/scale, and "
            "cyclical month; no absolute year or raw level",
            f"- Isolation contamination assumption: {ISOLATION_CONTAMINATION:.0%}",
            f"- Development-score threshold: {isolation_threshold:.6f}",
            "",
            "## Final-test signals",
            "",
            f"- Evaluated months: {len(aligned)}",
            f"- Residual signals: {int(aligned['residual_anomaly'].sum())}",
            f"- Isolation Forest signals: "
            f"{int(aligned['isolation_forest_anomaly'].sum())}",
            f"- Flagged by both methods: {both}",
            f"- Unique flagged months: {int(aligned['is_anomaly'].sum())}",
            "",
            "Method disagreement is preserved in the CSV rather than merged "
            "into a confidence claim.",
        ]
    )
    (REPORTS_DIR / "anomaly_report.md").write_text(report, encoding="utf-8")
    save_timeline(monthly["co2"], anomalies)
    refresh_manifest_artifact(
        MODEL_MANIFEST_PATH,
        "anomalies",
        ANOMALIES_PATH,
    )
    print(f"Saved {len(anomalies)} bounded exploratory signal rows.")


def save_timeline(series: pd.Series, anomalies: pd.DataFrame) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(series.index, series, color="#287eb8", linewidth=1.3, label="Monthly CO2")
    if not anomalies.empty:
        ax.scatter(
            anomalies.index,
            anomalies["co2"],
            color="#c77a24",
            edgecolor="#27364a",
            linewidth=0.5,
            s=42,
            label="Exploratory signal",
            zorder=3,
        )
    ax.axvspan(
        pd.Timestamp("1995-07-31"),
        pd.Timestamp("2001-12-31"),
        color="#68778b",
        alpha=0.08,
        label="Final-test signal window",
    )
    ax.set_title("Historical CO2 with bounded exploratory test-period signals")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "anomaly_timeline.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
