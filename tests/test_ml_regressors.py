import numpy as np

from src.models.train_ml_regressors import build_models


def test_random_forest_uses_serial_deterministic_execution() -> None:
    first = build_models(seed=123)["Random Forest"]
    second = build_models(seed=123)["Random Forest"]
    first.set_params(n_estimators=8)
    second.set_params(n_estimators=8)

    features = np.array(
        [
            [-2.0, 0.5],
            [-1.0, 1.5],
            [0.0, -0.5],
            [1.0, 2.5],
            [2.0, 3.5],
            [3.0, 1.0],
        ]
    )
    target = np.array([10.0, 12.0, 11.0, 15.0, 18.0, 17.0])

    first.fit(features, target)
    second.fit(features, target)
    first_predictions = first.predict(features)
    second_predictions = second.predict(features)

    assert first.get_params()["n_jobs"] == 1
    assert first_predictions.tobytes() == second_predictions.tobytes()
