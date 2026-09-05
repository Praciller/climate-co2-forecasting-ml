# Rolling-Origin Evaluation

Development-only expanding-window backtesting uses chronological, non-overlapping 7-month validation blocks. Each target is forecast one month after its permitted origin, then its actual value is appended to the next origin's history.

- Fold count: **11**
- Development boundary: **1995-06-30**
- Models: Naive, Seasonal Naive, Exponential Smoothing, SARIMA
- Robust development choice: **SARIMA**
- Selection key: mean fold MAE, mean fold RMSE, then simplicity
- Final governed/test rows are not used for folds, selection, or interval calibration.

## Temporal folds

| Fold | Train range | Validation range | Horizon |
|---:|---|---|---:|
| 1 | 1959-03-31 to 1989-01-31 | 1989-02-28 to 1989-08-31 | 7 |
| 2 | 1959-03-31 to 1989-08-31 | 1989-09-30 to 1990-03-31 | 7 |
| 3 | 1959-03-31 to 1990-03-31 | 1990-04-30 to 1990-10-31 | 7 |
| 4 | 1959-03-31 to 1990-10-31 | 1990-11-30 to 1991-05-31 | 7 |
| 5 | 1959-03-31 to 1991-05-31 | 1991-06-30 to 1991-12-31 | 7 |
| 6 | 1959-03-31 to 1991-12-31 | 1992-01-31 to 1992-07-31 | 7 |
| 7 | 1959-03-31 to 1992-07-31 | 1992-08-31 to 1993-02-28 | 7 |
| 8 | 1959-03-31 to 1993-02-28 | 1993-03-31 to 1993-09-30 | 7 |
| 9 | 1959-03-31 to 1993-09-30 | 1993-10-31 to 1994-04-30 | 7 |
| 10 | 1959-03-31 to 1994-04-30 | 1994-05-31 to 1994-11-30 | 7 |
| 11 | 1959-03-31 to 1994-11-30 | 1994-12-31 to 1995-06-30 | 7 |

## Aggregate metrics

Values are mean ± population standard deviation across folds; the median is retained in JSON for skewed fold distributions.

| Model | MAE | RMSE | sMAPE | MASE |
|---|---:|---:|---:|---:|
| SARIMA | 0.239 ± 0.067 | 0.284 ± 0.072 | 0.067% ± 0.019 | 0.195 ± 0.054 |
| Exponential Smoothing | 0.272 ± 0.084 | 0.319 ± 0.089 | 0.076% ± 0.024 | 0.221 ± 0.068 |
| Naive | 1.126 ± 0.143 | 1.257 ± 0.143 | 0.316% ± 0.040 | 0.917 ± 0.115 |
| Seasonal Naive | 1.278 ± 0.458 | 1.318 ± 0.455 | 0.359% ± 0.127 | 1.042 ± 0.377 |

## Interpretation and limits

**SARIMA** has the lowest mean development-fold MAE in this bounded candidate set. This is robustness evidence for this historical series, not a universal model claim.

The final governed/test period remains a one-time post-selection evaluation. Fold residuals are out-of-sample for their own origins, but temporal dependence and regime change mean formal exchangeable conformal guarantees should not be assumed.