# Anomaly Holdout Drift Post-Mortem

## Summary

The first Isolation Forest implementation flagged all 78 held-out test months as anomalies. The detector had learned only the earlier, lower-CO2 portion of a strongly trending series, so every later observation appeared out-of-distribution. The fix fits the exploratory unsupervised detector across the full observed feature history while keeping residual anomalies tied to held-out forecast errors.

## Symptom

`python -m src.anomaly.detect_anomalies` wrote 78 anomaly rows. The held-out test split also contained exactly 78 rows.

Deterministic reproduction:

```text
test_rows=78
test_flags=78
```

## Root Cause

`src/anomaly/detect_anomalies.py` fitted Isolation Forest on train and validation rows, then predicted only the latest test rows. Features include absolute CO2 level, lags, rolling levels, and year. Atmospheric CO2 trends upward, so the test feature distribution sits above the earlier development distribution.

The detector therefore answered "is this later period similar to the earlier period?" instead of "is this point unusual within the observed history?"

## Why It Produced the Symptom

Isolation Forest isolates observations that are easy to separate from its fitted feature distribution. Every latest-period row carried later years and higher concentration-related features, making the complete test block easy to isolate.

## Fix

The implementation in `src/anomaly/detect_anomalies.py` now fits and scores Isolation Forest across the full observed engineered feature history. Residual flags remain limited to the shared held-out forecast period. API serialization in `src/api/service.py` also converts method labels into a stable list.

## How It Was Found

The integration run produced 78 anomaly rows. A direct differential test compared two fits:

```text
fit on train+validation: 78 of 78 test rows flagged
fit on full observed history: 16 of 514 rows flagged
```

This ruled out CSV duplication and residual-threshold logic. The exact equality between test size and flagged count exposed distribution shift as the dominant path.

## Why It Slipped Through

The initial implementation reused supervised forecast split boundaries for an exploratory unsupervised task. Unit tests covered data, features, schemas, metrics, and API validation, but no test asserted that anomaly output remained selective under a trending feature distribution.

## Validation

- Original command now writes 16 anomaly rows, not 78.
- `GET /anomalies` returns HTTP 200 and 16 schema-valid records.
- Browser anomaly table renders 16 rows.
- Timeline markers render without page overflow.

## Action Items

- Keep the report language explicitly exploratory.
- Add a selectivity regression test if anomaly method behavior becomes a maintained product contract.
- Revisit detrended or residual feature spaces before claiming production anomaly detection.
