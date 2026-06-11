# Anomaly Detection Report

These findings are exploratory signals, not verified climate events.

## Methods

- Residual threshold using the best forecast model: **Exponential Smoothing**
- Residual threshold: **1.123 ppm**
- Isolation Forest using lag, rolling, and calendar features

## Results

- Residual anomalies: 0
- Isolation Forest anomalies: 16
- Unique flagged months: 16