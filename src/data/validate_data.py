from __future__ import annotations

import pandas as pd

from src.data.load_co2 import load_co2_dataset
from src.features.preprocess_timeseries import build_monthly_features
from src.utils.config import PROJECT_ROOT, RAW_DATA_PATH, REPORTS_DIR, ensure_project_directories


def load_source_frame() -> pd.DataFrame:
    if RAW_DATA_PATH.exists():
        return pd.read_csv(RAW_DATA_PATH, parse_dates=["date"], index_col="date")
    return load_co2_dataset()


def find_missing_timestamps(index: pd.DatetimeIndex) -> int:
    expected = pd.date_range(index.min(), index.max(), freq="W-SAT")
    return len(expected.difference(index))


def build_validation_report(frame: pd.DataFrame) -> str:
    values = frame["co2"]
    q1, q3 = values.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = values[(values < lower) | (values > upper)]
    stats = values.describe()
    raw_monthly = values.resample("ME").mean()
    monthly, _ = build_monthly_features(frame)
    missing_months = raw_monthly[raw_monthly.isna()].index
    imputed_months = monthly.index[monthly["is_imputed"]]

    lines = [
        "# Data Validation Report",
        "",
        "## Integrity",
        "",
        f"- Missing timestamps against weekly calendar: {find_missing_timestamps(frame.index)}",
        f"- Missing CO2 values: {int(values.isna().sum())}",
        f"- Duplicate timestamps: {int(frame.index.duplicated().sum())}",
        f"- Date range: {frame.index.min().date()} to {frame.index.max().date()}",
        f"- Inferred frequency: {pd.infer_freq(frame.index[:50]) or 'irregular weekly'}",
        f"- Numeric range: {values.min():.2f} to {values.max():.2f} ppm",
        f"- Non-positive observed values: {int((values.dropna() <= 0).sum())}",
        f"- Monotonic ordering: {frame.index.is_monotonic_increasing}",
        "",
        "## Monthly Transformation",
        "",
        "- Aggregation: month-end mean of available weekly observations",
        "- Missing-month strategy: causal forward fill, bounded to 3 months",
        f"- Monthly rows: {len(monthly)}",
        f"- Monthly date range: {monthly.index.min().date()} to {monthly.index.max().date()}",
        f"- Missing months before fill: {len(missing_months)}",
        f"- Missing months after fill: {int(monthly['co2'].isna().sum())}",
        f"- Imputed months: {', '.join(timestamp.date().isoformat() for timestamp in imputed_months)}",
        f"- Duplicate monthly timestamps: {int(monthly.index.duplicated().sum())}",
        f"- Non-positive monthly values: {int((monthly['co2'] <= 0).sum())}",
        f"- Frequency consistent: {pd.infer_freq(monthly.index) == 'ME'}",
        "",
        "## IQR Outlier Summary",
        "",
        f"- Lower bound: {lower:.2f} ppm",
        f"- Upper bound: {upper:.2f} ppm",
        f"- Values outside bounds: {len(outliers)}",
        "",
        "## Descriptive Statistics",
        "",
        "| Statistic | Value |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {value:.3f} |" for name, value in stats.items())
    return "\n".join(lines)


def main() -> None:
    ensure_project_directories()
    frame = load_source_frame()
    report_path = REPORTS_DIR / "data_validation_report.md"
    report_path.write_text(build_validation_report(frame), encoding="utf-8")
    print(f"Saved validation report to {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
