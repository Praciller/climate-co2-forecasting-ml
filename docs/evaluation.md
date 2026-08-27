# Evaluation and Metric Governance

## Selection sequence

1. Validate the monthly feature and split contract.
2. Generate 11 deterministic, non-overlapping seven-month expanding folds from
   the train/validation development period.
3. Fit or initialize each bounded candidate only through each fold origin and
   score MAE, RMSE, sMAPE, and MASE.
4. Select the lowest mean fold MAE; break ties with mean fold RMSE, then model
   simplicity.
5. Freeze the selected model and calibrate its interval from development-fold
   residuals only.
6. Report 78 rolling-origin one-step final-test predictions once.
7. Fit the selected family on the full historical series for fixed-origin
   serving.

SARIMA is selected at `0.239 ppm` mean development-fold MAE across 11 folds.
Exponential Smoothing has a slightly lower final-test MAE (`0.237` versus
SARIMA's `0.243`), but the final test does not retroactively change selection.

## Temporal leakage contract

The executable validator in `src/evaluation/temporal_contract.py` checks the
following before evaluation:

- train ends at `1989-01-31`, validation ends at `1995-06-30`, and final test
  begins at `1995-07-31`;
- lags use only prior monthly values and rolling statistics start from
  `co2.shift(1)`, so the target month cannot enter its own features;
- monthly aggregation uses no interpolation; all-missing months use only a
  bounded causal forward fill, with imputation lineage retained;
- tabular candidates use unscaled values, while the LSTM `StandardScaler` is
  fitted on train rows only and its sequence loader does not shuffle temporal
  samples; and
- anomaly changes and prior-window statistics are causal, with detector fit and
  thresholds derived from train/validation development rows before final-test
  scoring.

The validator is called by the governed evaluator and has synthetic regression
tests for target-contaminated rolling features and split boundaries.

## Metrics

- MAE and RMSE are in ppm.
- MAPE excludes zero actual denominators and is `null` when no valid
  denominator exists.
- sMAPE excludes zero pair denominators and is `null` when undefined.
- MASE uses a 12-month seasonal scale computed only from the history available
  before the evaluated split.
- Raw, unrounded predictions are the source of every metric.

Trainer summaries and shared evaluation use the same split-specific MASE
history, eliminating the previous artifact drift.

## Why one split is insufficient

A single holdout measures one historical regime and can make model ranking
depend on that block's particular trend or seasonal phase. Rolling-origin
backtesting exposes fold-to-fold variability while preserving the information
available at each forecast origin. It is still not a guarantee for a new regime.

## Rolling-origin evidence

The backtest begins with the 359 train feature rows and evaluates 11 successive
seven-month blocks through `1995-06-30`. Training expands by seven months after
each block, validation blocks do not overlap, and each target has a one-month
origin. The final test begins at `1995-07-31`, so no test row enters fold
construction or model selection. Per-fold metrics and aggregate mean, median,
and population standard deviation are in
[`rolling_origin_evaluation.json`](../reports/rolling_origin_evaluation.json).

The API forecast is instead one fixed origin with horizons 1–60. Its metrics
must not be compared as though it were the rolling one-step task.

## Interval governance

The selected model's 77 out-of-sample development-fold absolute residuals define
a finite-sample residual-quantile radius. This is a residual-quantile/conformal-
style method; temporal dependence and regime change mean formal exchangeable
conformal guarantees should not be assumed. The 90% nominal radius is evaluated
once on the untouched final test:

- radius: 0.506 ppm
- observed one-step coverage: 91.0% (`71/78`)
- average width: 1.011 ppm
- calibration samples: 77
- test samples: 78

The API reuses that development-derived radius around multi-step projections for
bounded display. Coverage is measured only for the one-step task; no
multi-horizon calibration claim is made. This is a 90% prediction interval, not
a 95% confidence interval.

The compact machine-readable result is
[`forecast_interval_evaluation.json`](../reports/forecast_interval_evaluation.json).

## Residual evidence

Residuals are final-test forecast errors, never in-sample fitted residuals.
The report records mean, standard deviation, lag-1 autocorrelation, ordered
largest errors, source model, sample count, and interpretation limits.
