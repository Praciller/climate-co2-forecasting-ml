from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

import matplotlib
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, Dataset

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.metrics import calculate_metrics
from src.models.common import (
    load_modeling_data,
    save_forecast_plot,
    save_metrics,
    save_prediction_artifact,
)
from src.utils.config import FIGURES_DIR, MODELS_DIR, REPORTS_DIR
from src.utils.reproducibility import set_seed


@dataclass(frozen=True)
class TrainingConfig:
    epochs: int = 100
    lookback: int = 24
    batch_size: int = 16
    learning_rate: float = 0.001
    hidden_size: int = 32
    seed: int = 42


class SequenceDataset(Dataset):
    def __init__(self, sequences: np.ndarray, targets: np.ndarray) -> None:
        self.sequences = torch.tensor(sequences, dtype=torch.float32).unsqueeze(-1)
        self.targets = torch.tensor(targets, dtype=torch.float32).unsqueeze(-1)

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[index], self.targets[index]


class LSTMForecaster(nn.Module):
    def __init__(self, hidden_size: int) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, batch_first=True)
        self.output = nn.Linear(hidden_size, 1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        output, _ = self.lstm(inputs)
        return self.output(output[:, -1, :])


def make_sequences(
    scaled_values: np.ndarray,
    dates: pd.DatetimeIndex,
    lookback: int,
) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
    sequences, targets, target_dates = [], [], []
    for index in range(lookback, len(scaled_values)):
        sequences.append(scaled_values[index - lookback : index])
        targets.append(scaled_values[index])
        target_dates.append(dates[index])
    return (
        np.asarray(sequences),
        np.asarray(targets),
        pd.DatetimeIndex(target_dates),
    )


def train(config: TrainingConfig) -> None:
    set_seed(config.seed)
    monthly, features = load_modeling_data()
    train_end = features.index[features["split"] == "train"].max()
    validation_end = features.index[features["split"] == "validation"].max()
    test_dates = features.index[features["split"] == "test"]

    scaler = StandardScaler()
    scaler.fit(monthly.loc[:train_end, ["co2"]])
    scaled = scaler.transform(monthly[["co2"]]).ravel()
    sequences, targets, dates = make_sequences(
        scaled,
        monthly.index,
        config.lookback,
    )

    train_mask = dates <= train_end
    validation_mask = (dates > train_end) & (dates <= validation_end)
    test_mask = dates.isin(test_dates)
    train_dataset = SequenceDataset(sequences[train_mask], targets[train_mask])
    validation_dataset = SequenceDataset(
        sequences[validation_mask],
        targets[validation_mask],
    )
    test_dataset = SequenceDataset(sequences[test_mask], targets[test_mask])
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
    )

    model = LSTMForecaster(config.hidden_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_function = nn.MSELoss()
    training_losses, validation_losses = [], []

    for _ in range(config.epochs):
        model.train()
        batch_losses = []
        for inputs, target in train_loader:
            optimizer.zero_grad()
            loss = loss_function(model(inputs), target)
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())

        model.eval()
        with torch.no_grad():
            validation_prediction = model(validation_dataset.sequences)
            validation_loss = loss_function(
                validation_prediction,
                validation_dataset.targets,
            )
        training_losses.append(float(np.mean(batch_losses)))
        validation_losses.append(float(validation_loss.item()))

    model.eval()
    with torch.no_grad():
        scaled_predictions = model(test_dataset.sequences).numpy().ravel()
    predictions = scaler.inverse_transform(
        scaled_predictions.reshape(-1, 1)
    ).ravel()
    actual = monthly.loc[dates[test_mask], "co2"]
    training_values = monthly.loc[:validation_end, "co2"].to_numpy()
    metrics = {
        "PyTorch LSTM": calculate_metrics(
            actual.to_numpy(),
            predictions,
            training_values,
        )
    }

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": asdict(config),
            "scaler_mean": scaler.mean_.tolist(),
            "scaler_scale": scaler.scale_.tolist(),
        },
        MODELS_DIR / "lstm_forecaster.pt",
    )
    save_metrics(REPORTS_DIR / "lstm_metrics.json", metrics)
    save_prediction_artifact("PyTorch LSTM", actual.index, actual, predictions)
    save_training_curve(training_losses, validation_losses)
    save_forecast_plot(
        FIGURES_DIR / "lstm_forecast.png",
        "PyTorch LSTM forecast on the held-out test period",
        actual,
        {"PyTorch LSTM": pd.Series(predictions, index=actual.index)},
    )
    print(f"Trained PyTorch LSTM for {config.epochs} epochs.")


def save_training_curve(training: list[float], validation: list[float]) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(training, label="Training loss")
    ax.plot(validation, label="Validation loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE")
    ax.set_title("LSTM training curve")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "lstm_training_curve.png", dpi=160)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the PyTorch LSTM forecaster.")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lookback", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--hidden-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TrainingConfig(
        epochs=2 if args.debug else args.epochs,
        lookback=args.lookback,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_size=16 if args.debug else args.hidden_size,
        seed=args.seed,
    )
    train(config)


if __name__ == "__main__":
    main()
