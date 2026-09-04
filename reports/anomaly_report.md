# Anomaly Signal Report

These are exploratory statistical signals under selected methods and assumptions, not verified climate events.

## Governed methods

- Residual source: SARIMA rolling one-step forecasts
- Residual threshold calibrated on validation only
- Residual threshold: 0.710 ppm (99% nominal)
- Isolation Forest fit on train and validation only
- Isolation features: changes, prior-window deviation/scale, and cyclical month; no absolute year or raw level
- Isolation contamination assumption: 3%
- Development-score threshold: 0.559439

## Final-test signals

- Evaluated months: 78
- Residual signals: 0
- Isolation Forest signals: 8
- Flagged by both methods: 0
- Unique flagged months: 8

Method disagreement is preserved in the CSV rather than merged into a confidence claim.