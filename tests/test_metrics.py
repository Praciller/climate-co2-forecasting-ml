import numpy as np
import pytest

from src.evaluation.metrics import calculate_metrics


def test_calculate_metrics_returns_all_required_metrics() -> None:
    actual = np.array([10.0, 12.0, 14.0])
    predicted = np.array([9.0, 13.0, 14.0])
    training = np.array([2.0, 4.0, 6.0, 8.0, 10.0])

    metrics = calculate_metrics(actual, predicted, training, seasonal_period=1)

    assert set(metrics) == {"mae", "rmse", "mape", "smape", "mase"}
    assert metrics["mae"] == pytest.approx(2 / 3)
    assert metrics["mase"] == pytest.approx(1 / 3)


def test_percentage_metrics_are_none_when_denominators_are_all_zero() -> None:
    metrics = calculate_metrics(
        np.zeros(3),
        np.zeros(3),
        np.array([1.0, 2.0, 3.0, 4.0]),
        seasonal_period=1,
    )

    assert metrics["mape"] is None
    assert metrics["smape"] is None
