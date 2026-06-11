# EDA Summary

## Dataset

- Weekly rows: 2,284
- Monthly rows after resampling: 526
- Date range: 1958-03-31 to 2001-12-31
- Missing weekly values before interpolation: 59

## Findings

- The series has a persistent upward long-term trend.
- Average month-of-year seasonal amplitude is about 5.52 ppm.
- Rolling variability is comparatively stable while the level rises.
- Autocorrelation remains high across many lags because trend and seasonality are strong.

## Stationarity

- Level ADF statistic: 2.232, p-value: 0.9989.
- First-difference ADF statistic: -4.751, p-value: 0.0001.
- The level series is non-stationary; differencing materially improves stationarity.

## Forecasting Challenges

- Forecasts must model both trend and annual seasonality.
- Evaluation must remain chronological to avoid future leakage.
- Long-horizon uncertainty expands beyond the observed period.
- The dataset is small enough that statistical models can outperform deep learning.