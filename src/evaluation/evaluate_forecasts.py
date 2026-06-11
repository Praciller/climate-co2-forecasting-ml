from __future__ import annotations

import json

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.metrics import calculate_metrics
from src.models.common import PREDICTIONS_DIR, load_modeling_data
from src.utils.config import FIGURES_DIR, REPORTS_DIR
from src.utils.io import write_json


MODEL_FILES = {
    "Naive": "naive.csv",
    "Moving Average": "moving_average.csv",
    "Seasonal Naive": "seasonal_naive.csv",
    "Exponential Smoothing": "exponential_smoothing.csv",
    "SARIMA": "sarima.csv",
    "Random Forest": "random_forest.csv",
    "Gradient Boosting": "gradient_boosting.csv",
    "PyTorch LSTM": "pytorch_lstm.csv",
}

MODEL_NOTES = {
    "Naive": "One-step baseline",
    "Moving Average": "12-month mean",
    "Seasonal Naive": "Annual benchmark",
    "Exponential Smoothing": "Additive trend and seasonality",
    "SARIMA": "Seasonally differenced statistical model",
    "Random Forest": "Lag and rolling features",
    "Gradient Boosting": "Lag and rolling features",
    "PyTorch LSTM": "Current artifact uses debug training",
}


def load_predictions() -> dict[str, pd.DataFrame]:
    predictions = {}
    missing = []
    for model_name, filename in MODEL_FILES.items():
        path = PREDICTIONS_DIR / filename
        if not path.exists():
            missing.append(filename)
            continue
        predictions[model_name] = pd.read_csv(path, parse_dates=["date"]).set_index(
            "date"
        )

    if missing:
        raise FileNotFoundError(
            "Missing prediction artifacts: "
            + ", ".join(missing)
            + ". Run all training commands first."
        )
    return predictions


def verify_aligned_test_period(predictions: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    model_names = list(predictions)
    reference = predictions[model_names[0]].index
    for model_name in model_names[1:]:
        if not reference.equals(predictions[model_name].index):
            raise ValueError(f"{model_name} does not use the shared test period.")
    return reference


def build_comparison_markdown(metrics: dict[str, dict[str, float]]) -> str:
    lines = [
        "# Model Comparison",
        "",
        "All models are evaluated on the same chronological test period.",
        "",
        "| Model | MAE | RMSE | MAPE | sMAPE | MASE | Notes |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for model_name, values in sorted(
        metrics.items(),
        key=lambda item: item[1]["mae"],
    ):
        lines.append(
            f"| {model_name} | {values['mae']:.3f} | {values['rmse']:.3f} | "
            f"{values['mape']:.3f}% | {values['smape']:.3f}% | "
            f"{values['mase']:.3f} | {MODEL_NOTES[model_name]} |"
        )
    return "\n".join(lines)


def save_evaluation_figures(
    predictions: dict[str, pd.DataFrame],
    best_model: str,
) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    actual = next(iter(predictions.values()))["actual"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(actual.index, actual, color="#27364a", linewidth=2.2, label="Actual")
    for model_name, frame in predictions.items():
        ax.plot(frame.index, frame["prediction"], linewidth=1.15, label=model_name)
    ax.set_title("Forecast comparison on shared test period")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "forecast_comparison.png", dpi=160)
    plt.close(fig)

    residuals = actual - predictions[best_model]["prediction"]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.axhline(0, color="#68778b", linewidth=1)
    ax.plot(residuals.index, residuals, color="#287eb8")
    ax.set_title(f"Residuals: {best_model}")
    ax.set_ylabel("Actual - prediction")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "residual_plot.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(residuals, bins=14, color="#287eb8", alpha=0.85)
    ax.set_title(f"Error distribution: {best_model}")
    ax.set_xlabel("Residual")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "error_distribution.png", dpi=160)
    plt.close(fig)


def main() -> None:
    _, features = load_modeling_data()
    training = features[features["split"].isin(["train", "validation"])]["co2"]
    predictions = load_predictions()
    verify_aligned_test_period(predictions)

    metrics = {}
    for model_name, frame in predictions.items():
        metrics[model_name] = calculate_metrics(
            frame["actual"].to_numpy(),
            frame["prediction"].to_numpy(),
            training.to_numpy(),
        )

    best_model = min(metrics, key=lambda name: metrics[name]["mae"])
    payload = {
        "best_model": best_model,
        "test_start": str(next(iter(predictions.values())).index.min().date()),
        "test_end": str(next(iter(predictions.values())).index.max().date()),
        "models": metrics,
    }
    write_json(REPORTS_DIR / "forecast_metrics.json", payload)
    (REPORTS_DIR / "model_comparison.md").write_text(
        build_comparison_markdown(metrics),
        encoding="utf-8",
    )
    save_evaluation_figures(predictions, best_model)
    print(json.dumps({"best_model": best_model, "metrics": metrics[best_model]}, indent=2))


if __name__ == "__main__":
    main()
