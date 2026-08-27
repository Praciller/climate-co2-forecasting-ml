from __future__ import annotations

import numpy as np


def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    training: np.ndarray,
    *,
    seasonal_period: int = 12,
) -> dict[str, float | None]:
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.asarray(predicted, dtype=float)
    training_values = np.asarray(training, dtype=float)

    if actual_values.shape != predicted_values.shape:
        raise ValueError("Actual and predicted arrays must have matching shapes.")
    if actual_values.size == 0:
        raise ValueError("Metric inputs must not be empty.")
    if seasonal_period < 1 or training_values.size <= seasonal_period:
        raise ValueError("Training data must exceed the seasonal period.")

    errors = actual_values - predicted_values
    nonzero_actual = np.abs(actual_values) > np.finfo(float).eps
    mape = (
        float(
            np.mean(
                np.abs(errors[nonzero_actual] / actual_values[nonzero_actual])
            )
            * 100
        )
        if nonzero_actual.any()
        else None
    )
    denominator = (np.abs(actual_values) + np.abs(predicted_values)) / 2
    nonzero_denominator = denominator > np.finfo(float).eps
    smape = (
        float(
            np.mean(
                np.abs(
                    errors[nonzero_denominator]
                    / denominator[nonzero_denominator]
                )
            )
            * 100
        )
        if nonzero_denominator.any()
        else None
    )
    naive_scale = np.mean(
        np.abs(training_values[seasonal_period:] - training_values[:-seasonal_period])
    )
    if naive_scale <= np.finfo(float).eps:
        raise ValueError("MASE scale is zero; training data has no seasonal variation.")

    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "mape": mape,
        "smape": smape,
        "mase": float(np.mean(np.abs(errors)) / naive_scale),
    }
