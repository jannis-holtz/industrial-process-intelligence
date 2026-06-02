import pandas as pd


def calculate_activity_waiting_times(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values(["case_id", "timestamp"]).copy()

    ordered["next_activity"] = ordered.groupby("case_id")["activity"].shift(-1)
    ordered["next_timestamp"] = ordered.groupby("case_id")["timestamp"].shift(-1)

    ordered["waiting_time_days"] = (
        ordered["next_timestamp"] - ordered["timestamp"]
    ).dt.total_seconds() / 86_400

    transitions = ordered.dropna(subset=["next_activity", "waiting_time_days"]).copy()
    transitions["transition"] = transitions["activity"] + " → " + transitions["next_activity"]

    return (
        transitions.groupby("transition")
        .agg(
            average_waiting_time_days=("waiting_time_days", "mean"),
            median_waiting_time_days=("waiting_time_days", "median"),
            transition_count=("transition", "count"),
        )
        .reset_index()
        .sort_values("average_waiting_time_days", ascending=False)
    )
