from datetime import date

import pytest
from pydantic import ValidationError

from src.api.schemas import ForecastPoint, ForecastResponse


def test_forecast_schema_accepts_numeric_predictions_and_dates() -> None:
    response = ForecastResponse(
        model="Exponential Smoothing",
        horizon_months=1,
        generated_at="2026-06-10T00:00:00Z",
        forecast=[
            ForecastPoint(
                date=date(2026, 7, 31),
                prediction=429.4,
                lower=427.1,
                upper=431.7,
            )
        ],
    )

    assert response.forecast[0].prediction == 429.4
    assert response.horizon_months == len(response.forecast)


def test_forecast_schema_rejects_inverted_interval() -> None:
    with pytest.raises(ValidationError):
        ForecastPoint(
            date=date(2026, 7, 31),
            prediction=429.4,
            lower=432.0,
            upper=431.0,
        )
