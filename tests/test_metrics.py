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
