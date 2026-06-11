from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class HistoricalPoint(BaseModel):
    date: date
    co2: float
    rolling_mean_12: float | None = None


class ForecastPoint(BaseModel):
    date: date
    prediction: float
    lower: float
    upper: float

    @model_validator(mode="after")
    def validate_interval(self) -> "ForecastPoint":
        if self.lower > self.upper:
            raise ValueError("Forecast lower bound must not exceed upper bound.")
        if not self.lower <= self.prediction <= self.upper:
            raise ValueError("Prediction must fall inside the forecast interval.")
        return self


class ForecastResponse(BaseModel):
    model: str
    horizon_months: int = Field(ge=1)
    generated_at: datetime
    forecast: list[ForecastPoint]

    @model_validator(mode="after")
    def validate_horizon_length(self) -> "ForecastResponse":
        if self.horizon_months != len(self.forecast):
            raise ValueError("Forecast length must match horizon_months.")
        return self


class AnomalyPoint(BaseModel):
    date: date
    co2: float
    residual_anomaly: bool
    isolation_forest_anomaly: bool
    methods: list[str]
