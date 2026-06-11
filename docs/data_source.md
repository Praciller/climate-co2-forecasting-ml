# Data Source

## Source

The project loads the atmospheric CO2 dataset packaged with `statsmodels`:

```python
import statsmodels.api as sm

data = sm.datasets.co2.load_pandas().data
```

The source is real weekly atmospheric concentration data. The project does not generate synthetic observations.

## Local Outputs

- `data/raw/co2_raw.csv`: direct package data with datetime index preserved
- `data/processed/co2_monthly.csv`: month-end means with time interpolation
- `data/processed/co2_features.csv`: leakage-safe features and split labels

## Validation

`python -m src.data.validate_data` reports missing timestamps, missing values, duplicates, date range, inferred frequency, numeric range, IQR outliers, and descriptive statistics.

## Reproducibility

No Kaggle account, API key, login, scraping, or paid service is required. Installing the Python dependencies is sufficient.
