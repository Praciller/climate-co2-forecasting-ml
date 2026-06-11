import pandas as pd

from src.data.load_co2 import load_co2_dataset


def test_co2_dataset_loads_with_datetime_index_and_numeric_values() -> None:
    frame = load_co2_dataset()

    assert not frame.empty
    assert frame.index.name == "date"
    assert isinstance(frame.index, pd.DatetimeIndex)
    assert frame.columns.tolist() == ["co2"]
    assert pd.api.types.is_numeric_dtype(frame["co2"])
    assert frame["co2"].notna().any()
