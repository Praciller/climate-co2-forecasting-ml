from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pandas as pd

from src.api.schemas import ForecastPoint, ForecastResponse
from src.data.load_co2 import load_co2_dataset
from src.features.preprocess_timeseries import build_monthly_features
from src.utils.config import (
    ANOMALIES_PATH,
    FORECAST_METRICS_PATH,
    LIVE_FORECAST_PATH,
    MAX_FORECAST_HORIZON,
    MONTHLY_DATA_PATH,
)
from src.utils.io import read_json


class ForecastService:
    def __init__(self) -> None:
        self.history = self._load_history()
        self.forecast_artifact = self._load_forecast_artifact()

    @staticmethod
    def _load_history() -> pd.DataFrame:
        if MONTHLY_DATA_PATH.exists():
            frame = pd.read_csv(
                MONTHLY_DATA_PATH,
                parse_dates=["date"],
                index_col="date",
            )
            if not frame.empty and frame["co2"].notna().all():
                frame.index = pd.DatetimeIndex(frame.index, freq="ME", name="date")
                return frame.sort_index()

        monthly, _ = build_monthly_features(load_co2_dataset())
        return monthly

    @staticmethod
    def _load_forecast_artifact() -> dict[str, Any]:
        artifact = read_json(LIVE_FORECAST_PATH, None)
        if not artifact:
            raise FileNotFoundError(
                "Live forecast artifact is missing. Run "
                "`python -m src.models.train_statistical` first."
            )

        forecast = artifact.get("forecast", [])
        if len(forecast) < MAX_FORECAST_HORIZON:
            raise ValueError(
                "Live forecast artifact does not cover the configured maximum "
                "forecast horizon."
            )
        return artifact

    def forecast(self, horizon_months: int) -> ForecastResponse:
        forecast_rows = self.forecast_artifact["forecast"][:horizon_months]
        residual_std = float(self.forecast_artifact["residual_std"])
        points = []
        for step, row in enumerate(forecast_rows, start=1):
            prediction = float(row["prediction"])
            interval = 1.96 * residual_std * step**0.5
            points.append(
                ForecastPoint(
                    date=row["date"],
                    prediction=prediction,
                    lower=float(prediction - interval),
                    upper=float(prediction + interval),
                )
            )

        return ForecastResponse(
            model=str(self.forecast_artifact["model_name"]),
            horizon_months=horizon_months,
            generated_at=datetime.now(UTC),
            forecast=points,
        )

    def historical_records(self) -> list[dict[str, object]]:
        frame = self.history.copy()
        frame["rolling_mean_12"] = frame["co2"].rolling(12).mean()
        return [
            {
                "date": index.date(),
                "co2": float(row.co2),
                "rolling_mean_12": (
                    None
                    if pd.isna(row.rolling_mean_12)
                    else float(row.rolling_mean_12)
                ),
            }
            for index, row in frame.iterrows()
        ]

    def model_info(self) -> dict[str, object]:
        metrics = read_json(FORECAST_METRICS_PATH, {})
        return {
            "active_model": self.forecast_artifact["model_name"],
            "live_forecast_mode": "precomputed monthly multi-step forecast",
            "training_rows": self.forecast_artifact["training_rows"],
            "training_end": self.forecast_artifact["training_end"],
            "artifact_generated_at": self.forecast_artifact["generated_at"],
            "available_models": [
                "Naive",
                "Moving Average",
                "Seasonal Naive",
                "Exponential Smoothing",
                "SARIMA",
                "Random Forest",
                "Gradient Boosting",
                "PyTorch LSTM",
            ],
            "metrics": metrics,
        }

    @staticmethod
    def anomalies() -> list[dict[str, object]]:
        if not ANOMALIES_PATH.exists():
            return []

        frame = pd.read_csv(ANOMALIES_PATH, parse_dates=["date"])
        records = []
        for row in frame.to_dict(orient="records"):
            records.append(
                {
                    "date": row["date"].date(),
                    "co2": float(row["co2"]),
                    "residual_anomaly": bool(row["residual_anomaly"]),
                    "isolation_forest_anomaly": bool(
                        row["isolation_forest_anomaly"]
                    ),
                    "methods": str(row["methods"]).split("|"),
                }
            )
        return records
