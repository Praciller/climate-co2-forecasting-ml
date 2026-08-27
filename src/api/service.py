from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.schemas import ForecastPoint, ForecastResponse
from src.artifacts import ArtifactValidationError, validate_manifest
from src.utils.config import MAX_FORECAST_HORIZON, PROJECT_ROOT


class ServiceNotReadyError(RuntimeError):
    """Raised when governed serving artifacts are unavailable."""


class ForecastService:
    REQUIRED_ARTIFACTS = {
        "monthly_data",
        "forecast_metrics",
        "interval_report",
        "residual_report",
        "live_forecast",
        "anomalies",
    }

    def __init__(self, root: Path = PROJECT_ROOT) -> None:
        self.root = root.resolve()
        self.ready = False
        self.readiness_code = "artifact_validation_failed"
        self.manifest: dict[str, Any] = {}
        self.paths: dict[str, Path] = {}
        self.history = pd.DataFrame()
        self.metrics: dict[str, Any] = {}
        self.forecast_artifact: dict[str, Any] = {}
        try:
            self._load_governed_artifacts()
        except (ArtifactValidationError, ValueError, KeyError, OSError):
            return
        self.ready = True
        self.readiness_code = "ready"

    def _load_governed_artifacts(self) -> None:
        manifest_path = self.root / "reports" / "model_manifest.json"
        self.manifest, self.paths = validate_manifest(
            manifest_path,
            root=self.root,
            required_artifacts=self.REQUIRED_ARTIFACTS,
        )
        self.history = pd.read_csv(
            self.paths["monthly_data"],
            parse_dates=["date"],
            index_col="date",
        ).sort_index()
        if (
            self.history.empty
            or self.history.index.has_duplicates
            or not self.history.index.is_monotonic_increasing
            or self.history["co2"].isna().any()
        ):
            raise ArtifactValidationError("Monthly history is invalid.")
        self.metrics = json.loads(
            self.paths["forecast_metrics"].read_text(encoding="utf-8")
        )
        self.forecast_artifact = json.loads(
            self.paths["live_forecast"].read_text(encoding="utf-8")
        )
        forecast = self.forecast_artifact.get("forecast", [])
        if len(forecast) < MAX_FORECAST_HORIZON:
            raise ArtifactValidationError(
                "Live forecast does not cover the configured maximum horizon."
            )
        dates = pd.to_datetime([row["date"] for row in forecast])
        expected = pd.date_range(
            pd.Timestamp(self.forecast_artifact["forecast_origin"])
            + pd.offsets.MonthEnd(1),
            periods=len(forecast),
            freq="ME",
        )
        if not pd.DatetimeIndex(dates).equals(expected):
            raise ArtifactValidationError("Forecast timestamps are not contiguous.")
        for row in forecast:
            if not float(row["lower"]) <= float(row["prediction"]) <= float(
                row["upper"]
            ):
                raise ArtifactValidationError("Forecast interval ordering is invalid.")

    def require_ready(self) -> None:
        if not self.ready:
            raise ServiceNotReadyError(self.readiness_code)

    def forecast(self, horizon_months: int) -> ForecastResponse:
        self.require_ready()
        artifact = self.forecast_artifact
        interval = artifact["interval"]
        return ForecastResponse(
            model=str(artifact["model_name"]),
            model_version=str(artifact["model_version"]),
            forecast_origin=artifact["forecast_origin"],
            horizon_months=horizon_months,
            frequency=str(artifact["frequency"]),
            protocol=str(artifact["protocol"]),
            interval_method=str(interval["method"]),
            interval_nominal_coverage=float(interval["nominal_coverage"]),
            interval_coverage_scope=str(interval["coverage_scope"]),
            generated_at=artifact["generated_at"],
            limitations=list(artifact["limitations"]),
            forecast=[
                ForecastPoint(
                    date=row["date"],
                    prediction=float(row["prediction"]),
                    lower=float(row["lower"]),
                    upper=float(row["upper"]),
                )
                for row in artifact["forecast"][:horizon_months]
            ],
        )

    def historical_records(self) -> list[dict[str, object]]:
        self.require_ready()
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
        self.require_ready()
        selection = self.metrics["selection"]
        final_test = self.metrics["final_test"]
        return {
            "active_model": selection["selected_model"],
            "model_version": self.forecast_artifact["model_version"],
            "dataset": self.manifest["dataset"],
            "preprocessing": self.manifest["preprocessing"],
            "split_boundaries": self.manifest["split_boundaries"],
            "forecasting_protocol": self.manifest["forecasting_protocol"],
            "selection": selection,
            "interval": self.manifest["interval"],
            "training_rows": self.forecast_artifact["training_rows"],
            "training_end": self.forecast_artifact["training_end"],
            "artifact_generated_at": self.forecast_artifact["generated_at"],
            "candidate_models": list(final_test["models"]),
            "metrics": self.metrics,
        }

    def anomalies(self) -> list[dict[str, object]]:
        self.require_ready()
        frame = pd.read_csv(self.paths["anomalies"], parse_dates=["date"])
        records = []
        for row in frame.to_dict(orient="records"):
            records.append(
                {
                    "date": row["date"].date(),
                    "co2": float(row["co2"]),
                    "residual_ppm": (
                        None
                        if pd.isna(row.get("residual_ppm"))
                        else float(row["residual_ppm"])
                    ),
                    "residual_anomaly": bool(row["residual_anomaly"]),
                    "isolation_score": (
                        None
                        if pd.isna(row.get("isolation_score"))
                        else float(row["isolation_score"])
                    ),
                    "isolation_forest_anomaly": bool(
                        row["isolation_forest_anomaly"]
                    ),
                    "methods": str(row["methods"]).split("|"),
                }
            )
        return records
