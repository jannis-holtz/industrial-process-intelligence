from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"
CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
BOTTLENECK_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "bottleneck_analysis.parquet"

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


def build_transition_table(
    event_log: pd.DataFrame,
    clean_cases: pd.DataFrame,
) -> pd.DataFrame:
    clean_case_ids = set(clean_cases["case_id"])

    # Only keep the event-level columns needed for transition calculation.
    # This prevents duplicated case attributes like item_category_x / item_category_y after merging.
    required_event_columns = ["case_id", "activity", "timestamp", "resource"]
    missing_event_columns = [
        column for column in required_event_columns if column not in event_log.columns
    ]

    if missing_event_columns:
        raise ValueError(f"Missing event log columns: {missing_event_columns}")

    events = event_log.loc[
        event_log["case_id"].isin(clean_case_ids),
        required_event_columns,
    ].copy()

    events = events.sort_values(["case_id", "timestamp", "activity"])

    events["next_activity"] = events.groupby("case_id")["activity"].shift(-1)
    events["next_timestamp"] = events.groupby("case_id")["timestamp"].shift(-1)
    events["next_resource"] = events.groupby("case_id")["resource"].shift(-1)

    events["waiting_time_days"] = (
        events["next_timestamp"] - events["timestamp"]
    ).dt.total_seconds() / 86_400

    transitions = events.dropna(
        subset=["next_activity", "next_timestamp", "waiting_time_days"]
    ).copy()

    transitions = transitions[transitions["waiting_time_days"] >= 0].copy()

    transitions["transition"] = (
        transitions["activity"] + " → " + transitions["next_activity"]
    )

    required_case_columns = [
        "case_id",
        "company",
        "item_category",
        "document_type",
        "vendor",
        "cycle_time_days",
    ]

    missing_case_columns = [
        column for column in required_case_columns if column not in clean_cases.columns
    ]

    if missing_case_columns:
        raise ValueError(f"Missing clean case columns: {missing_case_columns}")

    case_attributes = clean_cases[required_case_columns].copy()

    transitions = transitions.merge(
        case_attributes,
        on="case_id",
        how="left",
        validate="many_to_one",
    )

    return transitions


def most_frequent_value(values: pd.Series):
    mode = values.dropna().mode()
    if mode.empty:
        return None
    return mode.iloc[0]


def calculate_bottleneck_analysis(transitions: pd.DataFrame) -> pd.DataFrame:
    total_waiting_time = transitions["waiting_time_days"].sum()

    bottlenecks = (
        transitions.groupby("transition")
        .agg(
            transition_count=("transition", "count"),
            average_waiting_time_days=("waiting_time_days", "mean"),
            median_waiting_time_days=("waiting_time_days", "median"),
            p90_waiting_time_days=(
                "waiting_time_days",
                lambda values: values.quantile(0.90),
            ),
            total_waiting_time_days=("waiting_time_days", "sum"),
            affected_cases=("case_id", "nunique"),
            dominant_item_category=("item_category", most_frequent_value),
            dominant_document_type=("document_type", most_frequent_value),
        )
        .reset_index()
    )

    bottlenecks = bottlenecks[
        bottlenecks["transition_count"] >= MIN_TRANSITION_COUNT
    ].copy()

    bottlenecks["share_of_total_waiting_time_pct"] = (
        bottlenecks["total_waiting_time_days"] / total_waiting_time * 100
    )

    # Impact combines waiting-time contribution and typical waiting time.
    # This prioritizes transitions that are both frequent enough and operationally expensive.
    bottlenecks["impact_score"] = (
        bottlenecks["share_of_total_waiting_time_pct"]
        * bottlenecks["median_waiting_time_days"]
    )

    numeric_columns = [
        "average_waiting_time_days",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "total_waiting_time_days",
        "share_of_total_waiting_time_pct",
        "impact_score",
    ]

    bottlenecks[numeric_columns] = bottlenecks[numeric_columns].round(2)

    bottlenecks = bottlenecks.sort_values(
        ["impact_score", "total_waiting_time_days"],
        ascending=[False, False],
    ).reset_index(drop=True)

    bottlenecks.insert(0, "bottleneck_rank", range(1, len(bottlenecks) + 1))

    return bottlenecks


def print_summary(bottlenecks: pd.DataFrame, transitions: pd.DataFrame) -> None:
    print("\n=== Bottleneck Analysis Summary ===")
    print(f"Transitions analyzed: {len(transitions):,}")
    print(f"Distinct transitions after threshold: {len(bottlenecks):,}")
    print(f"Minimum transition count threshold: {MIN_TRANSITION_COUNT:,}")

    print("\n=== Top 10 Bottlenecks by Impact Score ===")
    columns = [
        "bottleneck_rank",
        "transition",
        "transition_count",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "total_waiting_time_days",
        "share_of_total_waiting_time_pct",
        "impact_score",
        "dominant_item_category",
    ]

    print(bottlenecks[columns].head(10).to_string(index=False))

    print("\n=== Top 10 Transitions by Total Waiting Time ===")
    print(
        bottlenecks.sort_values("total_waiting_time_days", ascending=False)[columns]
        .head(10)
        .to_string(index=False)
    )


def main() -> None:
    print("Loading processed event log and clean case table...")
    event_log, clean_cases = load_data()

    print("Building transition-level waiting times...")
    transitions = build_transition_table(event_log, clean_cases)

    print("Calculating bottleneck-level KPIs...")
    bottlenecks = calculate_bottleneck_analysis(transitions)

    BOTTLENECK_ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    bottlenecks.to_parquet(BOTTLENECK_ANALYSIS_PATH, index=False)

    print_summary(bottlenecks, transitions)

    print(f"\nSaved bottleneck analysis to: {BOTTLENECK_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()