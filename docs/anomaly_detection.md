# Anomaly Detection

## Residual Method

The best forecasting model produces held-out residuals:

```text
residual = actual - prediction
```

A month is flagged when its absolute residual exceeds the mean absolute residual plus three residual standard deviations.

## Isolation Forest

Isolation Forest uses observed lag, rolling, and calendar features. It is fitted across the observed feature history because training only on early years makes the later upward-trending period look entirely out-of-distribution.

## Interpretation

The current run flags 16 months through Isolation Forest and zero through the residual threshold. These are exploratory feature-space signals, not verified climate events, sensor failures, or causal attributions.

## Output

- `reports/anomalies.csv`
- `reports/anomaly_report.md`
- `reports/figures/anomaly_timeline.png`
