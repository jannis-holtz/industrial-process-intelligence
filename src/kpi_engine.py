import pandas as pd


def calculate_case_cycle_times(df: pd.DataFrame) -> pd.DataFrame:
    case_times = (
        df.groupby("case_id")["timestamp"]
        .agg(start_time="min", end_time="max")
        .reset_index()
    )

    case_times["cycle_time_days"] = (
        case_times["end_time"] - case_times["start_time"]
    ).dt.total_seconds() / 86_400

    return case_times


def calculate_kpis(df: pd.DataFrame) -> dict:
    case_times = calculate_case_cycle_times(df)

    return {
        "number_of_cases": int(df["case_id"].nunique()),
        "number_of_events": int(len(df)),
        "number_of_activities": int(df["activity"].nunique()),
        "average_cycle_time_days": round(case_times["cycle_time_days"].mean(), 2),
        "median_cycle_time_days": round(case_times["cycle_time_days"].median(), 2),
        "max_cycle_time_days": round(case_times["cycle_time_days"].max(), 2),
    }
