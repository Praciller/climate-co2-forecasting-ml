from datetime import date

import pytest
from pydantic import ValidationError

from src.api.schemas import ForecastPoint, ForecastResponse


def test_forecast_schema_accepts_numeric_predictions_and_dates() -> None:
    response = ForecastResponse(
        model="Exponential Smoothing",
        model_version="governed-test",
        forecast_origin="2001-12-31",
        horizon_months=1,
        frequency="month-end",
        protocol="fixed-origin multi-step forecast",
        interval_method="split-conformal absolute validation residual",
        interval_nominal_coverage=0.9,
        interval_coverage_scope="rolling one-step final test only",
        generated_at="2026-07-23T00:00:00Z",
        limitations=["Historical educational dataset."],
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
