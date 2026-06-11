# Evaluation

## Metrics

- MAE: average absolute error in ppm
- RMSE: larger errors receive more weight
- MAPE: absolute percentage error
- sMAPE: symmetric percentage error
- MASE: MAE scaled by the 12-month seasonal naive error

## Comparison Rule

All eight models must produce predictions for exactly the same chronological
test dates. Evaluation is rolling one-step-ahead: each prediction may use
observations available before that target month. `src.evaluation.evaluate_forecasts`
validates the shared index before calculating metrics.

## Current Result

Exponential Smoothing has the lowest test MAE at 0.237 ppm and MASE at 0.190.
SARIMA is close. The result supports a central lesson of the project: model
complexity does not guarantee better forecasts on a small seasonal series.

## LSTM Caveat

The generated LSTM report comes from `--debug`, which trains for two epochs to verify the CPU pipeline. Run the documented 100-epoch command before comparing a serious LSTM experiment.
