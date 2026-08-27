# Data Source and Transformation

## Historical source contract

The repository loads `statsmodels.datasets.co2` through:

```python
import statsmodels.api as sm

data = sm.datasets.co2.load_pandas().data
```

The upstream dataset is **Mauna Loa Weekly Atmospheric CO2 Data**: atmospheric
CO2 concentration in ppmv from continuous air samples at Mauna Loa Observatory.
The period is March 1958 through December 2001. Statsmodels records 2,225
observations; the returned weekly calendar frame has 2,284 rows including 59
missing values. The data is public domain and was obtained upstream on
2014-03-15.

Primary documentation:
[statsmodels dataset page](https://www.statsmodels.org/stable/datasets/generated/co2.html).

This project uses the historical package copy. It does not fetch a current
monitoring source, call NOAA, or use synthetic fallback data.

## Verified package output

| Field | Value |
|---|---|
| Package version used for committed artifacts | statsmodels 0.14.6 |
| Weekly calendar rows | 2,284 |
| Observed values | 2,225 |
| Missing values | 59 |
| Date range | 1958-03-29 to 2001-12-29 |
| Frequency | `W-SAT` |
| Duplicate timestamps | 0 |
| Ordering | Monotonic increasing |
| Unit | ppmv |
| Source-data license | Public domain |
| Raw CSV SHA-256 | `6d5ee9e8d32c1f8fa5f24f30a33ada05615ab19b3c4f6699fd2efc7d29b73085` |

## Weekly-to-monthly contract

1. Sort the unique weekly index.
2. Compute a month-end mean from available weekly observations.
3. Record the count of observed weekly values per month.
4. Mark months with no observed weekly value as imputed.
5. Apply causal forward fill for no more than three consecutive months.
6. Fail if any missing month remains.

The five imputed months are 1958-06-30, 1958-10-31, 1964-02-29,
1964-03-31, and 1964-04-30. No later value is used to fill an earlier month.
The three-month limit is explicit and regression-tested.

Outputs:

- `data/raw/co2_raw.csv`: package-loaded weekly calendar
- `data/processed/co2_monthly.csv`: 526 month-end rows plus lineage columns
- `data/processed/co2_features.csv`: prior-only features and governed split
- `reports/dataset_metadata.md`: versioned source metadata and fingerprint
- `reports/data_validation_report.md`: raw and monthly integrity checks
