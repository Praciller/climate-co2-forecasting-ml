from __future__ import annotations

import hashlib
from importlib.metadata import version

import pandas as pd
import statsmodels.api as sm

from src.utils.config import (
    DATASET_LICENSE,
    DATASET_MODULE,
    DATASET_NAME,
    DATASET_RETRIEVED_UPSTREAM,
    DATASET_UNIT,
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
    fingerprint = hashlib.sha256(
        frame.to_csv(index_label="date").encode("utf-8")
    ).hexdigest()
    return "\n".join(
        [
            "# Dataset Metadata",
            "",
            f"- **Dataset:** {DATASET_NAME}",
            f"- **Package module:** `{DATASET_MODULE}`",
            f"- **statsmodels version:** {version('statsmodels')}",
            f"- **Weekly calendar rows:** {len(frame):,}",
            f"- **Observed values:** {int(frame['co2'].notna().sum()):,}",
            f"- **Date range:** {frame.index.min().date()} to {frame.index.max().date()}",
            f"- **Unit:** {DATASET_UNIT}",
            f"- **Index frequency:** {inferred_frequency}",
            f"- **Missing CO2 values:** {int(frame['co2'].isna().sum()):,}",
            f"- **Duplicate timestamps:** {int(frame.index.duplicated().sum()):,}",
            f"- **Upstream retrieval date:** {DATASET_RETRIEVED_UPSTREAM}",
            f"- **Source-data license:** {DATASET_LICENSE}",
            f"- **CSV SHA-256:** `{fingerprint}`",
            "",
            "This is a historical dataset packaged with statsmodels. It is not "
            "a current monitoring feed and this repository performs no network "
            "retrieval when loading it.",
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
