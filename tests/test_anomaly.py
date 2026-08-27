import numpy as np
import pandas as pd

from src.anomaly.detect_anomalies import isolation_flags


def test_isolation_threshold_alignment_and_determinism() -> None:
    development_index = pd.date_range("1980-01-31", periods=100, freq="ME")
    target_index = pd.date_range("1990-01-31", periods=20, freq="ME")
    development = pd.DataFrame(
        {"signal": np.sin(np.arange(100) / 5)},
        index=development_index,
    )
    target = pd.DataFrame(
        {"signal": np.r_[np.zeros(19), 20.0]},
        index=target_index,
    )

    first_flags, first_scores, first_threshold = isolation_flags(
        development,
        target,
        contamination=0.03,
    )
    second_flags, second_scores, second_threshold = isolation_flags(
        development,
        target,
        contamination=0.03,
    )

    assert first_flags.index.equals(target_index)
    assert first_flags.iloc[-1]
    assert first_flags.equals(second_flags)
    assert first_scores.equals(second_scores)
    assert first_threshold == second_threshold
