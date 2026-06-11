from __future__ import annotations

import json

import matplotlib
import pandas as pd
from sklearn.ensemble import IsolationForest

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.common import PREDICTIONS_DIR, feature_matrix, load_modeling_data
from src.models.common import slugify_model_name
from src.utils.config import ANOMALIES_PATH, FIGURES_DIR, REPORTS_DIR


def main() -> None:
    monthly, features = load_modeling_data()
    metrics_path = REPORTS_DIR / "forecast_metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(
            "Forecast metrics are missing. Run "
            "`python -m src.evaluation.evaluate_forecasts` first."
        )

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    best_model = metrics["best_model"]
    prediction_path = PREDICTIONS_DIR / f"{slugify_model_name(best_model)}.csv"
    forecast = pd.read_csv(prediction_path, parse_dates=["date"]).set_index("date")
    residuals = forecast["actual"] - forecast["prediction"]
    threshold = residuals.abs().mean() + 3 * residuals.std(ddof=0)
    residual_flags = residuals.abs() > threshold

    detector = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        random_state=42,
    )
    detector.fit(feature_matrix(features))
    isolation_flags = pd.Series(
        detector.predict(feature_matrix(features)) == -1,
        index=features.index,
    )

    aligned = pd.DataFrame(index=features.index)
    aligned["co2"] = monthly.loc[features.index, "co2"]
    aligned["residual_anomaly"] = residual_flags.reindex(
        features.index,
        fill_value=False,
    )
    aligned["isolation_forest_anomaly"] = isolation_flags
    aligned["is_anomaly"] = (
        aligned["residual_anomaly"] | aligned["isolation_forest_anomaly"]
    )
    anomalies = aligned[aligned["is_anomaly"]].copy()
    anomalies["methods"] = anomalies.apply(
        lambda row: "|".join(
            method
            for method, is_flagged in (
                ("Residual threshold", row["residual_anomaly"]),
                ("Isolation Forest", row["isolation_forest_anomaly"]),
            )
            if is_flagged
        ),
        axis=1,
    )
    anomalies.reset_index(names="date").to_csv(ANOMALIES_PATH, index=False)

    report = "\n".join(
        [
            "# Anomaly Detection Report",
            "",
            "These findings are exploratory signals, not verified climate events.",
            "",
            "## Methods",
            "",
            f"- Residual threshold using the best forecast model: **{best_model}**",
            f"- Residual threshold: **{threshold:.3f} ppm**",
            "- Isolation Forest using lag, rolling, and calendar features",
            "",
            "## Results",
            "",
            f"- Residual anomalies: {int(aligned['residual_anomaly'].sum())}",
            f"- Isolation Forest anomalies: {int(aligned['isolation_forest_anomaly'].sum())}",
            f"- Unique flagged months: {int(aligned['is_anomaly'].sum())}",
        ]
    )
    (REPORTS_DIR / "anomaly_report.md").write_text(report, encoding="utf-8")
    save_timeline(monthly["co2"], anomalies)
    print(f"Saved {len(anomalies)} exploratory anomaly rows.")


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
            label="Exploratory anomaly",
            zorder=3,
        )
    ax.set_title("Atmospheric CO2 with exploratory anomaly signals")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "anomaly_timeline.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
