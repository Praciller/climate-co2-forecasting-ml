from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.features.preprocess_timeseries import FEATURE_COLUMNS
from src.utils.config import (
    FEATURE_DATA_PATH,
    FIGURES_DIR,
    MONTHLY_DATA_PATH,
    REPORTS_DIR,
)

PREDICTIONS_DIR = REPORTS_DIR / "predictions"


def load_modeling_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not MONTHLY_DATA_PATH.exists() or not FEATURE_DATA_PATH.exists():
        raise FileNotFoundError(
            "Processed data is missing. Run "
            "`python -m src.features.preprocess_timeseries` first."
        )

    monthly = pd.read_csv(MONTHLY_DATA_PATH, parse_dates=["date"], index_col="date")
    features = pd.read_csv(FEATURE_DATA_PATH, parse_dates=["date"], index_col="date")
    monthly.index = pd.DatetimeIndex(monthly.index, freq="ME", name="date")
    features.index = pd.DatetimeIndex(features.index, freq="ME", name="date")
    return monthly.sort_index(), features.sort_index()


def feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[:, FEATURE_COLUMNS]


def slugify_model_name(model_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", model_name.lower()).strip("_")


def save_prediction_artifact(
    model_name: str,
    dates: pd.DatetimeIndex,
    actual: np.ndarray | pd.Series,
    prediction: np.ndarray | pd.Series,
) -> Path:
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = PREDICTIONS_DIR / f"{slugify_model_name(model_name)}.csv"
    frame = pd.DataFrame(
        {
            "date": dates,
            "actual": np.asarray(actual, dtype=float),
            "prediction": np.asarray(prediction, dtype=float),
        }
    )
    frame.to_csv(path, index=False)
    return path


def save_metrics(path: Path, metrics: dict[str, dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def save_forecast_plot(
    path: Path,
    title: str,
    actual: pd.Series,
    predictions: dict[str, pd.Series],
) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(actual.index, actual.values, color="#27364a", linewidth=2, label="Actual")
    for name, series in predictions.items():
        ax.plot(series.index, series.values, linewidth=1.6, label=name)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
