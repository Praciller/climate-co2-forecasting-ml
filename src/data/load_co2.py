from __future__ import annotations

import pandas as pd
import statsmodels.api as sm

from src.utils.config import (
    PROJECT_ROOT,
    RAW_DATA_PATH,
    REPORTS_DIR,
    ensure_project_directories,
)


def load_co2_dataset() -> pd.DataFrame:
    frame = sm.datasets.co2.load_pandas().data.copy()
    frame.index = pd.DatetimeIndex(frame.index, name="date")
    frame = frame.rename(columns={frame.columns[0]: "co2"})
    frame["co2"] = pd.to_numeric(frame["co2"], errors="coerce")
    return frame.sort_index()


def build_metadata(frame: pd.DataFrame) -> str:
    inferred_frequency = pd.infer_freq(frame.index[:50]) or "irregular weekly"
    return "\n".join(
        [
            "# Dataset Metadata",
            "",
            "- **Source:** statsmodels atmospheric CO2 dataset",
            f"- **Rows:** {len(frame):,}",
            f"- **Date range:** {frame.index.min().date()} to {frame.index.max().date()}",
            f"- **Columns:** {', '.join(frame.columns)}",
            f"- **Index frequency:** {inferred_frequency}",
            f"- **Missing CO2 values:** {int(frame['co2'].isna().sum()):,}",
            "- **Synthetic data:** No",
            "",
            "Loaded with `statsmodels.api.datasets.co2.load_pandas()`.",
        ]
    )


def main() -> None:
    ensure_project_directories()
    frame = load_co2_dataset()
    frame.to_csv(RAW_DATA_PATH, index_label="date")
    metadata_path = REPORTS_DIR / "dataset_metadata.md"
    metadata_path.write_text(build_metadata(frame), encoding="utf-8")
    print(f"Saved {len(frame):,} rows to {RAW_DATA_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
