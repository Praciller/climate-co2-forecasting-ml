# Data Validation Report

## Integrity

- Missing timestamps against weekly calendar: 0
- Missing CO2 values: 59
- Duplicate timestamps: 0
- Date range: 1958-03-29 to 2001-12-29
- Inferred frequency: W-SAT
- Numeric range: 313.00 to 373.90 ppm
- Non-positive observed values: 0
- Monotonic ordering: True

## Monthly Transformation

- Aggregation: month-end mean of available weekly observations
- Missing-month strategy: causal forward fill, bounded to 3 months
- Monthly rows: 526
- Monthly date range: 1958-03-31 to 2001-12-31
- Missing months before fill: 5
- Missing months after fill: 0
- Imputed months: 1958-06-30, 1958-10-31, 1964-02-29, 1964-03-31, 1964-04-30
- Duplicate monthly timestamps: 0
- Non-positive monthly values: 0
- Frequency consistent: True

## IQR Outlier Summary

- Lower bound: 279.80 ppm
- Upper bound: 399.80 ppm
- Values outside bounds: 0

## Descriptive Statistics

| Statistic | Value |
|---|---:|
| count | 2225.000 |
| mean | 340.142 |
| std | 17.004 |
| min | 313.000 |
| 25% | 324.800 |
| 50% | 338.300 |
| 75% | 354.800 |
| max | 373.900 |