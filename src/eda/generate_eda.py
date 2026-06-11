from __future__ import annotations

import matplotlib
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data.load_co2 import load_co2_dataset
from src.features.preprocess_timeseries import build_monthly_features
from src.utils.config import FIGURES_DIR, REPORTS_DIR, ensure_project_directories


def save_timeseries_plot(monthly: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly.index, monthly, color="#287eb8", linewidth=1.4)
    ax.set_title("Monthly atmospheric CO2")
    ax.set_ylabel("CO2 (ppm)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "co2_timeseries.png", dpi=160)
    plt.close(fig)


def save_rolling_plot(monthly: pd.Series) -> None:
    rolling_mean = monthly.rolling(12).mean()
    rolling_std = monthly.rolling(12).std()
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    axes[0].plot(monthly.index, monthly, color="#89a7bb", linewidth=1)
    axes[0].plot(
        rolling_mean.index,
        rolling_mean,
        color="#287eb8",
        linewidth=2,
        label="12-month mean",
    )
    axes[0].set_ylabel("CO2 (ppm)")
    axes[0].legend(frameon=False)
    axes[1].plot(rolling_std.index, rolling_std, color="#c77a24", linewidth=1.8)
    axes[1].set_ylabel("12-month std")
    axes[1].set_xlabel("Date")
    for axis in axes:
        axis.grid(alpha=0.2)
    fig.suptitle("Rolling statistics")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "rolling_statistics.png", dpi=160)
    plt.close(fig)


def save_decomposition_plot(monthly: pd.Series) -> None:
    decomposition = seasonal_decompose(monthly, model="additive", period=12)
    fig = decomposition.plot()
    fig.set_size_inches(12, 8)
    fig.suptitle("Additive seasonal decomposition", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "seasonal_decomposition.png", dpi=160)
    plt.close(fig)


def save_autocorrelation_plot(monthly: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    plot_acf(monthly, lags=48, ax=ax, alpha=0.05)
    ax.set_title("Monthly CO2 autocorrelation")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "autocorrelation.png", dpi=160)
    plt.close(fig)


def build_summary(raw: pd.DataFrame, monthly: pd.Series) -> str:
    level_statistic, level_p_value, *_ = adfuller(monthly)
    diff_statistic, diff_p_value, *_ = adfuller(monthly.diff().dropna())
    seasonal_amplitude = (
        monthly.groupby(monthly.index.month).mean().max()
        - monthly.groupby(monthly.index.month).mean().min()
    )
    return "\n".join(
        [
            "# EDA Summary",
            "",
            "## Dataset",
            "",
            f"- Weekly rows: {len(raw):,}",
            f"- Monthly rows after resampling: {len(monthly):,}",
            f"- Date range: {monthly.index.min().date()} to {monthly.index.max().date()}",
            f"- Missing weekly values before interpolation: {int(raw['co2'].isna().sum()):,}",
            "",
            "## Findings",
            "",
            "- The series has a persistent upward long-term trend.",
            f"- Average month-of-year seasonal amplitude is about {seasonal_amplitude:.2f} ppm.",
            "- Rolling variability is comparatively stable while the level rises.",
            "- Autocorrelation remains high across many lags because trend and seasonality are strong.",
            "",
            "## Stationarity",
            "",
            f"- Level ADF statistic: {level_statistic:.3f}, p-value: {level_p_value:.4f}.",
            f"- First-difference ADF statistic: {diff_statistic:.3f}, p-value: {diff_p_value:.4f}.",
            "- The level series is non-stationary; differencing materially improves stationarity.",
            "",
            "## Forecasting Challenges",
            "",
            "- Forecasts must model both trend and annual seasonality.",
            "- Evaluation must remain chronological to avoid future leakage.",
            "- Long-horizon uncertainty expands beyond the observed period.",
            "- The dataset is small enough that statistical models can outperform deep learning.",
        ]
    )


def main() -> None:
    ensure_project_directories()
    raw = load_co2_dataset()
    monthly, _ = build_monthly_features(raw)
    series = monthly["co2"]
    save_timeseries_plot(series)
    save_rolling_plot(series)
    save_decomposition_plot(series)
    save_autocorrelation_plot(series)
    (REPORTS_DIR / "eda_summary.md").write_text(
        build_summary(raw, series),
        encoding="utf-8",
    )
    print("Saved EDA summary and four figures.")


if __name__ == "__main__":
    main()
