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
    metrics = {}
    predictions = {}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for split_name, training_splits in (
        ("validation", ["train"]),
        ("test", ["train", "validation"]),
    ):
        training = features[features["split"].isin(training_splits)]
        target = features[features["split"] == split_name]
        split_metrics = {}
        for model_name, model in build_models(seed).items():
            model.fit(feature_matrix(training), training["co2"])
            values = model.predict(feature_matrix(target))
            split_metrics[model_name] = calculate_metrics(
                target["co2"].to_numpy(),
                values,
                training["co2"].to_numpy(),
            )
            save_prediction_artifact(
                model_name,
                target.index,
                target["co2"],
                values,
                evaluation_split=split_name,
                refit_at_each_origin=False,
            )
            if split_name == "test":
                predictions[model_name] = pd.Series(values, index=target.index)
                artifact_name = (
                    "random_forest_forecaster.joblib"
                    if model_name == "Random Forest"
                    else "gradient_boosting_forecaster.joblib"
                )
                joblib.dump(model, MODELS_DIR / artifact_name)
        metrics[split_name] = split_metrics

    save_metrics(REPORTS_DIR / "ml_regressor_metrics.json", metrics)
    save_forecast_plot(
        FIGURES_DIR / "ml_forecast.png",
        "Machine-learning one-step forecasts on the final test period",
        target["co2"],
        predictions,
    )
    print("Generated validation and final-test evidence for two ML regressors.")


if __name__ == "__main__":
    main()
