from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"
CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"

PROCESS_EDGES_PATH = PROJECT_ROOT / "data" / "processed" / "process_edges.parquet"
PROCESS_ACTIVITIES_PATH = PROJECT_ROOT / "data" / "processed" / "process_activities.parquet"

MIN_TRANSITION_COUNT = 50


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not EVENT_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Event log not found: {EVENT_LOG_PATH}\n"
            "Run scripts/02_convert_xes_to_parquet.py first."
        )

    if not CLEAN_CASE_TIMES_PATH.exists():
        raise FileNotFoundError(
            f"Clean case table not found: {CLEAN_CASE_TIMES_PATH}\n"
            "Run scripts/04_create_clean_case_table.py first."
        )

    event_log = pd.read_parquet(EVENT_LOG_PATH)
    clean_cases = pd.read_parquet(CLEAN_CASE_TIMES_PATH)

    return event_log, clean_cases


def validate_columns(event_log: pd.DataFrame, clean_cases: pd.DataFrame) -> None:
    required_event_columns = [
        "case_id",
        "activity",
        "timestamp",
    ]

    required_case_columns = [
        "case_id",
    ]

    missing_event_columns = [
        column for column in required_event_columns if column not in event_log.columns
    ]

    missing_case_columns = [
        column for column in required_case_columns if column not in clean_cases.columns
    ]

    if missing_event_columns:
        raise ValueError(f"Missing event log columns: {missing_event_columns}")

    if missing_case_columns:
        raise ValueError(f"Missing clean case columns: {missing_case_columns}")


def filter_operational_events(
    event_log: pd.DataFrame,
    clean_cases: pd.DataFrame,
) -> pd.DataFrame:
    operational_case_ids = clean_cases[["case_id"]].drop_duplicates()

    operational_events = event_log.merge(
        operational_case_ids,
        on="case_id",
        how="inner",
    )

    operational_events = operational_events[
        [
            "case_id",
            "activity",
            "timestamp",
        ]
    ].copy()

    operational_events["timestamp"] = pd.to_datetime(operational_events["timestamp"])

    return operational_events


def calculate_process_edges(operational_events: pd.DataFrame) -> pd.DataFrame:
    ordered_events = operational_events.sort_values(
        ["case_id", "timestamp", "activity"]
    ).copy()

    ordered_events["next_activity"] = ordered_events.groupby("case_id")[
        "activity"
    ].shift(-1)

    ordered_events["next_timestamp"] = ordered_events.groupby("case_id")[
        "timestamp"
    ].shift(-1)

    transitions = ordered_events.dropna(
        subset=["next_activity", "next_timestamp"]
    ).copy()

    transitions["waiting_time_days"] = (
        transitions["next_timestamp"] - transitions["timestamp"]
    ).dt.total_seconds() / 86400

    transitions = transitions[transitions["waiting_time_days"] >= 0].copy()

    transitions["transition"] = (
        transitions["activity"] + " → " + transitions["next_activity"]
    )

    process_edges = (
        transitions.groupby(["activity", "next_activity", "transition"])
        .agg(
            transition_count=("transition", "count"),
            case_count=("case_id", "nunique"),
            average_waiting_time_days=("waiting_time_days", "mean"),
            median_waiting_time_days=("waiting_time_days", "median"),
            p90_waiting_time_days=("waiting_time_days", lambda values: values.quantile(0.90)),
            total_waiting_time_days=("waiting_time_days", "sum"),
        )
        .reset_index()
        .rename(
            columns={
                "activity": "source_activity",
                "next_activity": "target_activity",
            }
        )
    )

    process_edges = process_edges[
        process_edges["transition_count"] >= MIN_TRANSITION_COUNT
    ].copy()

    total_transitions = process_edges["transition_count"].sum()
    total_waiting_time = process_edges["total_waiting_time_days"].sum()

    process_edges["share_of_transitions_pct"] = (
        process_edges["transition_count"] / total_transitions * 100
    )

    process_edges["share_of_waiting_time_pct"] = (
        process_edges["total_waiting_time_days"] / total_waiting_time * 100
    )

    process_edges["flow_impact_score"] = (
        process_edges["share_of_transitions_pct"]
        * process_edges["median_waiting_time_days"]
    )

    numeric_columns = [
        "average_waiting_time_days",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "total_waiting_time_days",
        "share_of_transitions_pct",
        "share_of_waiting_time_pct",
        "flow_impact_score",
    ]

    process_edges[numeric_columns] = process_edges[numeric_columns].round(2)

    process_edges = process_edges.sort_values(
        ["transition_count", "flow_impact_score"],
        ascending=[False, False],
    ).reset_index(drop=True)

    process_edges.insert(
        0,
        "edge_rank",
        range(1, len(process_edges) + 1),
    )

    return process_edges


def calculate_process_activities(operational_events: pd.DataFrame) -> pd.DataFrame:
    activity_summary = (
        operational_events.groupby("activity")
        .agg(
            event_count=("activity", "count"),
            case_count=("case_id", "nunique"),
        )
        .reset_index()
    )

    total_events = len(operational_events)
    total_cases = operational_events["case_id"].nunique()

    activity_summary["share_of_events_pct"] = (
        activity_summary["event_count"] / total_events * 100
    )

    activity_summary["share_of_cases_pct"] = (
        activity_summary["case_count"] / total_cases * 100
    )

    activity_summary["share_of_events_pct"] = activity_summary[
        "share_of_events_pct"
    ].round(2)

    activity_summary["share_of_cases_pct"] = activity_summary[
        "share_of_cases_pct"
    ].round(2)

    activity_summary = activity_summary.sort_values(
        ["event_count", "case_count"],
        ascending=[False, False],
    ).reset_index(drop=True)

    activity_summary.insert(
        0,
        "activity_rank",
        range(1, len(activity_summary) + 1),
    )

    return activity_summary


def print_summary(
    process_edges: pd.DataFrame,
    process_activities: pd.DataFrame,
) -> None:
    print("\n=== Process Explorer Summary ===")
    print(f"Relevant process edges: {len(process_edges):,}")
    print(f"Activities: {len(process_activities):,}")
    print(f"Minimum transition count threshold: {MIN_TRANSITION_COUNT:,}")

    print("\n=== Top 15 Process Edges by Volume ===")
    edge_columns = [
        "edge_rank",
        "transition",
        "transition_count",
        "case_count",
        "share_of_transitions_pct",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "share_of_waiting_time_pct",
    ]

    print(process_edges[edge_columns].head(15).to_string(index=False))

    print("\n=== Top 15 Activities by Event Count ===")
    activity_columns = [
        "activity_rank",
        "activity",
        "event_count",
        "case_count",
        "share_of_events_pct",
        "share_of_cases_pct",
    ]

    print(process_activities[activity_columns].head(15).to_string(index=False))


def main() -> None:
    print("Loading event log and clean case table...")
    event_log, clean_cases = load_data()
    validate_columns(event_log, clean_cases)

    print("Filtering operational events...")
    operational_events = filter_operational_events(event_log, clean_cases)

    print("Calculating process edges...")
    process_edges = calculate_process_edges(operational_events)

    print("Calculating activity summary...")
    process_activities = calculate_process_activities(operational_events)

    PROCESS_EDGES_PATH.parent.mkdir(parents=True, exist_ok=True)
    process_edges.to_parquet(PROCESS_EDGES_PATH, index=False)
    process_activities.to_parquet(PROCESS_ACTIVITIES_PATH, index=False)

    print_summary(process_edges, process_activities)

    print(f"\nSaved process edges to: {PROCESS_EDGES_PATH}")
    print(f"Saved process activities to: {PROCESS_ACTIVITIES_PATH}")


if __name__ == "__main__":
    main()