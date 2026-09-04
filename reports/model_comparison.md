# Model Comparison

Candidate selection uses mean MAE across development rolling-origin folds. The selected model is then reported on the untouched final test period.

- Selected model: **SARIMA**
- Tie-break: mean fold RMSE, then explicit simplicity order
- Detailed fold evidence: `rolling_origin_evaluation.md`
- Final-test interval coverage: **91.0%** at 90% nominal (78 one-step forecasts)

| Model | Validation MAE | Validation RMSE | Test MAE | Test RMSE | Test sMAPE | Test MASE | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| SARIMA | 0.238 | 0.292 | 0.243 | 0.298 | 0.066% | 0.197 | **Selected**. Fixed parameters; state updated with each observation |
| Exponential Smoothing | 0.272 | 0.332 | 0.237 | 0.295 | 0.065% | 0.191 | Additive trend and seasonality; refit each origin |
| Naive | 1.126 | 1.265 | 1.136 | 1.276 | 0.310% | 0.918 | Observed value at the previous origin |
| Seasonal Naive | 1.278 | 1.394 | 1.693 | 1.849 | 0.464% | 1.368 | Observed value 12 months before the origin |
| Moving Average | 2.100 | 2.404 | 1.988 | 2.290 | 0.543% | 1.607 | Trailing 12-month observed mean |
| Random Forest | 3.290 | 4.202 | 3.966 | 4.984 | 1.084% | 3.205 | One-step lag and rolling features; no extrapolation |
| Gradient Boosting | 4.471 | 5.337 | 5.840 | 6.850 | 1.602% | 4.719 | One-step lag and rolling features; no extrapolation |

## Neural pipeline smoke

The PyTorch LSTM is excluded from selection and the candidate table. Its bounded run verifies sequence construction, train-only scaling, validation monitoring, checkpoint restoration, and CPU execution.

- Evidence type: `pipeline_smoke`
- Epochs completed: 2
- Ranking eligible: No