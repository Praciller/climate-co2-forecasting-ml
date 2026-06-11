from __future__ import annotations

import warnings
from datetime import UTC, datetime

import joblib
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.evaluation.metrics import calculate_metrics
from src.models.common import (
    load_modeling_data,
    save_forecast_plot,
    save_metrics,
    save_prediction_artifact,
)
from src.utils.config import (
    FIGURES_DIR,
    LIVE_FORECAST_PATH,
    MAX_FORECAST_HORIZON,
    MODELS_DIR,
    REPORTS_DIR,
)
from src.utils.io import write_json


def fit_exponential_smoothing(series: pd.Series):
    return ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)


def fit_sarima(series: pd.Series):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False, maxiter=100)


def rolling_exponential_smoothing(
    history: pd.Series,
    test: pd.Series,
) -> np.ndarray:
    observed = history.copy()
    predictions = []
    for forecast_date, actual in test.items():
        model = fit_exponential_smoothing(observed)
        predictions.append(float(model.forecast(1).iloc[0]))
        observed = pd.concat(
            [observed, pd.Series([actual], index=pd.DatetimeIndex([forecast_date]))]
        )
        observed.index = pd.DatetimeIndex(observed.index, freq="ME", name="date")
    return np.asarray(predictions)


def rolling_sarima(history: pd.Series, test: pd.Series) -> np.ndarray:
    model = fit_sarima(history)
    predictions = []
    for forecast_date, actual in test.items():
        predictions.append(float(model.forecast(1).iloc[0]))
        observation = pd.DataFrame(
            {"co2": [actual]},
            index=pd.DatetimeIndex([forecast_date], freq="ME", name="date"),
        )
        model = model.append(observation, refit=False)
    return np.asarray(predictions)


def save_live_forecast_artifact(
    model_name: str,
    model: object,
    history: pd.Series,
) -> None:
    predictions = np.asarray(model.forecast(MAX_FORECAST_HORIZON), dtype=float)
    dates = pd.date_range(
        history.index.max() + pd.offsets.MonthEnd(1),
        periods=MAX_FORECAST_HORIZON,
        freq="ME",
    )
    residuals = history - model.fittedvalues
    residual_std = max(float(residuals.dropna().std(ddof=0)), 0.1)
    write_json(
        LIVE_FORECAST_PATH,
        {
            "model_name": model_name,
            "generated_at": datetime.now(UTC).isoformat(),
            "training_rows": len(history),
            "training_end": history.index.max().date().isoformat(),
            "residual_std": residual_std,
            "forecast": [
                {
                    "date": forecast_date.date().isoformat(),
                    "prediction": float(prediction),
                }
                for forecast_date, prediction in zip(
                    dates,
                    predictions,
                    strict=True,
                )
            ],
        },
    )


def main() -> None:
    monthly, features = load_modeling_data()
    test_dates = features.index[features["split"] == "test"]
    train_series = monthly.loc[monthly.index < test_dates.min(), "co2"]
    test = monthly.loc[test_dates, "co2"]

    prediction_values = {
        "Exponential Smoothing": rolling_exponential_smoothing(train_series, test),
        "SARIMA": rolling_sarima(train_series, test),
    }
    metrics = {}
    predictions = {}

    for model_name, values in prediction_values.items():
        metrics[model_name] = calculate_metrics(
            test.to_numpy(),
            values,
            train_series.to_numpy(),
        )
        save_prediction_artifact(model_name, test.index, test, values)
        predictions[model_name] = pd.Series(values, index=test.index)

    best_name = min(metrics, key=lambda name: metrics[name]["mae"])
    full_series = monthly["co2"]
    best_model = (
        fit_exponential_smoothing(full_series)
        if best_name == "Exponential Smoothing"
        else fit_sarima(full_series)
    )
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model_name": best_name, "model": best_model},
        MODELS_DIR / "statistical_model.joblib",
    )
    save_live_forecast_artifact(best_name, best_model, full_series)
    save_metrics(REPORTS_DIR / "statistical_metrics.json", metrics)
    save_forecast_plot(
        FIGURES_DIR / "statistical_forecast.png",
        "Statistical forecasts on the held-out test period",
        test,
        predictions,
    )
    print(f"Trained statistical models. Best by MAE: {best_name}.")


if __name__ == "__main__":
    main()
