from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor

from src.evaluation.metrics import calculate_metrics
from src.models.common import (
    feature_matrix,
    load_modeling_data,
    save_forecast_plot,
    save_metrics,
    save_prediction_artifact,
)
from src.utils.config import FIGURES_DIR, MODELS_DIR, REPORTS_DIR


def build_models(seed: int) -> dict[str, object]:
    return {
        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=seed,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.03,
            max_depth=2,
            loss="huber",
            random_state=seed,
        ),
    }


def main(seed: int = 42) -> None:
    _, features = load_modeling_data()
    development = features[features["split"].isin(["train", "validation"])]
    test = features[features["split"] == "test"]
    x_development = feature_matrix(development)
    y_development = development["co2"]
    x_test = feature_matrix(test)
    y_test = test["co2"]

    metrics = {}
    predictions = {}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for model_name, model in build_models(seed).items():
        model.fit(x_development, y_development)
        values = model.predict(x_test)
        metrics[model_name] = calculate_metrics(
            y_test.to_numpy(),
            values,
            y_development.to_numpy(),
        )
        save_prediction_artifact(model_name, test.index, y_test, values)
        predictions[model_name] = pd.Series(values, index=test.index)
        artifact_name = (
            "random_forest_forecaster.joblib"
            if model_name == "Random Forest"
            else "gradient_boosting_forecaster.joblib"
        )
        joblib.dump(model, MODELS_DIR / artifact_name)

    save_metrics(REPORTS_DIR / "ml_regressor_metrics.json", metrics)
    save_forecast_plot(
        FIGURES_DIR / "ml_forecast.png",
        "Machine-learning forecasts on the held-out test period",
        y_test,
        predictions,
    )
    print("Trained Random Forest and Gradient Boosting regressors.")


if __name__ == "__main__":
    main()
