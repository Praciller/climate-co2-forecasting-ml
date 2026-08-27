from __future__ import annotations

from src.anomaly.detect_anomalies import main as detect_anomalies
from src.data.load_co2 import main as load_data
from src.data.validate_data import main as validate_data
from src.eda.generate_eda import main as generate_eda
from src.evaluation.evaluate_forecasts import main as evaluate_forecasts
from src.features.preprocess_timeseries import main as preprocess
from src.models.train_baselines import main as train_baselines
from src.models.train_lstm import TrainingConfig
from src.models.train_lstm import train as train_lstm
from src.models.train_ml_regressors import main as train_ml
from src.models.train_statistical import main as train_statistical


def main() -> None:
    load_data()
    validate_data()
    preprocess()
    generate_eda()
    train_baselines()
    train_statistical()
    train_ml()
    train_lstm(TrainingConfig(epochs=2, hidden_size=16))
    evaluate_forecasts()
    detect_anomalies()
    print("Governed local review pipeline completed.")


if __name__ == "__main__":
    main()
