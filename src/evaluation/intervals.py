"""Leakage-safe prediction interval calibration and evaluation helpers."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _finite_array(values: np.ndarray | pd.Series, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain only finite values.")
    return array


def calibrate_residual_radius(
    residuals: pd.Series,
    nominal_coverage: float,
    *,
    development_end: pd.Timestamp | None = None,
) -> float:
    """Return a finite-sample absolute-residual quantile.

    Residuals are expected to be out-of-sample development residuals.  The
    optional boundary makes accidental use of final-test residuals explicit.
    This is a residual-quantile/conformal-style interval, not a claim of
    independent or exchangeable errors for this time series.
    """
    if residuals.empty or not 0 < nominal_coverage < 1:
        raise ValueError("Residual calibration inputs are invalid.")
    if development_end is not None:
        boundary = pd.Timestamp(development_end)
        if not isinstance(residuals.index, pd.DatetimeIndex):
            raise ValueError("Calibration boundary requires datetime residuals.")
        if residuals.index.max() > boundary:
            raise ValueError("Residuals exceed the calibration boundary.")

    absolute = _finite_array(residuals.abs().to_numpy(), "Calibration residuals")
    order = min(len(absolute), math.ceil((len(absolute) + 1) * nominal_coverage))
    return float(np.sort(absolute)[order - 1])


def symmetric_prediction_interval(
    predictions: np.ndarray | pd.Series,
    radius: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply a symmetric residual-quantile radius to point predictions."""
    prediction_values = _finite_array(predictions, "Predictions")
    if not np.isfinite(radius) or radius < 0:
        raise ValueError("Interval radius must be finite and non-negative.")
    return prediction_values - radius, prediction_values + radius


def coverage_rate(
    actual: np.ndarray | pd.Series,
    lower: np.ndarray | pd.Series,
    upper: np.ndarray | pd.Series,
) -> float:
    """Compute inclusive empirical coverage for ordered interval bounds."""
    actual_values = _finite_array(actual, "Actual values")
    lower_values = _finite_array(lower, "Lower bounds")
    upper_values = _finite_array(upper, "Upper bounds")
    if not (actual_values.shape == lower_values.shape == upper_values.shape):
        raise ValueError("Actual, lower, and upper arrays must have matching shapes.")
    if actual_values.size == 0:
        raise ValueError("Interval evaluation inputs must not be empty.")
    if np.any(lower_values > upper_values):
        raise ValueError("Lower interval bounds must not exceed upper bounds.")
    return float(
        np.mean((actual_values >= lower_values) & (actual_values <= upper_values))
    )


def evaluate_prediction_interval(
    actual: np.ndarray | pd.Series,
    predictions: np.ndarray | pd.Series,
    lower: np.ndarray | pd.Series,
    upper: np.ndarray | pd.Series,
    *,
    nominal_coverage: float,
) -> dict[str, float | int]:
    """Return nominal level, observed coverage, and interval width evidence."""
    if not 0 < nominal_coverage < 1:
        raise ValueError("Nominal coverage must be between 0 and 1.")
    actual_values = _finite_array(actual, "Actual values")
    prediction_values = _finite_array(predictions, "Predictions")
    lower_values = _finite_array(lower, "Lower bounds")
    upper_values = _finite_array(upper, "Upper bounds")
    if not (
        actual_values.shape
        == prediction_values.shape
        == lower_values.shape
        == upper_values.shape
    ):
        raise ValueError("Interval evaluation arrays must have matching shapes.")
    coverage = coverage_rate(actual_values, lower_values, upper_values)
    widths = upper_values - lower_values
    if np.any(prediction_values < lower_values) or np.any(
        prediction_values > upper_values
    ):
        raise ValueError("Predictions must lie inside interval bounds.")
    return {
        "nominal_coverage": float(nominal_coverage),
        "empirical_coverage": coverage,
        "covered_samples": int(
            np.sum((actual_values >= lower_values) & (actual_values <= upper_values))
        ),
        "samples": int(actual_values.size),
        "average_width": float(np.mean(widths)),
    }
