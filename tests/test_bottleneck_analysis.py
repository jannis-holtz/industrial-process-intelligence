import pandas as pd

from src.bottleneck_analysis import calculate_activity_waiting_times


def test_calculate_activity_waiting_times_returns_transition():
    df = pd.DataFrame(
        {
            "case_id": ["A", "A"],
            "activity": ["Start", "End"],
            "timestamp": pd.to_datetime(["2025-01-01", "2025-01-03"]),
        }
    )

    result = calculate_activity_waiting_times(df)

    assert result.iloc[0]["transition"] == "Start → End"
    assert result.iloc[0]["average_waiting_time_days"] == 2
