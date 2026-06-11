# Model Comparison

All models are evaluated on the same chronological test period.

| Model | MAE | RMSE | MAPE | sMAPE | MASE | Notes |
|---|---:|---:|---:|---:|---:|---|
| Exponential Smoothing | 0.237 | 0.298 | 0.065% | 0.065% | 0.190 | Additive trend and seasonality |
| SARIMA | 0.239 | 0.295 | 0.065% | 0.065% | 0.192 | Seasonally differenced statistical model |
| Naive | 1.136 | 1.276 | 0.310% | 0.310% | 0.913 | One-step baseline |
| Seasonal Naive | 1.693 | 1.849 | 0.462% | 0.464% | 1.361 | Annual benchmark |
| Moving Average | 1.988 | 2.290 | 0.542% | 0.543% | 1.598 | 12-month mean |
| Random Forest | 3.991 | 5.005 | 1.081% | 1.090% | 3.208 | Lag and rolling features |
| Gradient Boosting | 5.847 | 6.858 | 1.586% | 1.603% | 4.700 | Lag and rolling features |
| PyTorch LSTM | 28.009 | 28.235 | 7.636% | 7.944% | 22.513 | Current artifact uses debug training |