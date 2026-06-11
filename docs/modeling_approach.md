# Modeling Approach

## Split Strategy

The project uses a chronological 70/15/15 train, validation, and test split. Random splitting is prohibited because future observations would leak into training.

## Features

- lags: 1, 3, 6, and 12 months
- rolling means: 3, 6, and 12 months
- rolling standard deviations: 3, 6, and 12 months
- calendar: month, quarter, and year

Rolling features shift the target by one month before aggregation, so the current target never enters its own predictors.

## Models

### Baselines

- naive
- 12-month moving average
- seasonal naive

### Statistical

- additive Exponential Smoothing
- SARIMA `(1,1,1)(1,1,1,12)`

### Machine Learning

- Random Forest Regressor
- Gradient Boosting Regressor

### Deep Learning

The PyTorch LSTM uses a configurable lookback window, standardization fitted on training data only, `Dataset`, `DataLoader`, Adam, MSE loss, and CPU-safe defaults.

## Artifact Contract

Every trainer writes aligned `date`, `actual`, and `prediction` CSV data under `reports/predictions/`. Shared evaluation rejects models that do not use the same test index.
