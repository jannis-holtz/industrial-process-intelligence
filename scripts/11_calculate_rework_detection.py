from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"
CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"

REWORK_CASE_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "rework_case_analysis.parquet"
REWORK_ACTIVITY_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "rework_activity_analysis.parquet"


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
        "cycle_time_days",
        "event_count",
        "activity_count",
        "item_category",
        "document_type",
        "company",
        "vendor",
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

    return operational_events


def calculate_case_rework_features(
    operational_events: pd.DataFrame,
    clean_cases: pd.DataFrame,
) -> pd.DataFrame:
    activity_counts = (
        operational_events.groupby(["case_id", "activity"])
        .size()
        .reset_index(name="activity_occurrences")
    )

    repeated_activities = activity_counts[
        activity_counts["activity_occurrences"] > 1
    ].copy()

    repeated_summary = (
        repeated_activities.groupby("case_id")
        .agg(
            repeated_activity_count=("activity", "nunique"),
            total_repeated_event_count=("activity_occurrences", "sum"),
        )
        .reset_index()
    )

    repeated_summary["rework_event_count"] = (
        repeated_summary["total_repeated_event_count"]
        - repeated_summary["repeated_activity_count"]
    )

    rework_cases = clean_cases[
        [
            "case_id",
            "cycle_time_days",
            "event_count",
            "activity_count",
            "item_category",
            "document_type",
            "company",
            "vendor",
        ]
    ].merge(
        repeated_summary[
            [
                "case_id",
                "repeated_activity_count",
                "rework_event_count",
            ]
        ],
        on="case_id",
        how="left",
    )

    rework_cases["repeated_activity_count"] = (
        rework_cases["repeated_activity_count"].fillna(0).astype(int)
    )
    rework_cases["rework_event_count"] = (
        rework_cases["rework_event_count"].fillna(0).astype(int)
    )
    rework_cases["has_rework"] = rework_cases["rework_event_count"] > 0

    return rework_cases


def calculate_rework_activity_analysis(
    operational_events: pd.DataFrame,
    rework_case_analysis: pd.DataFrame,
) -> pd.DataFrame:
    activity_counts = (
        operational_events.groupby(["case_id", "activity"])
        .size()
        .reset_index(name="activity_occurrences")
    )

    repeated_activities = activity_counts[
        activity_counts["activity_occurrences"] > 1
    ].copy()

    if repeated_activities.empty:
        return pd.DataFrame(
            columns=[
                "activity",
                "rework_cases",
                "total_rework_events",
                "average_occurrences_when_repeated",
                "share_of_rework_cases_pct",
            ]
        )

    repeated_activities["rework_events"] = (
        repeated_activities["activity_occurrences"] - 1
    )

    total_rework_cases = rework_case_analysis["has_rework"].sum()

    rework_activity_analysis = (
        repeated_activities.groupby("activity")
        .agg(
            rework_cases=("case_id", "nunique"),
            total_rework_events=("rework_events", "sum"),
            average_occurrences_when_repeated=("activity_occurrences", "mean"),
        )
        .reset_index()
    )

    rework_activity_analysis["share_of_rework_cases_pct"] = (
        rework_activity_analysis["rework_cases"] / total_rework_cases * 100
    )

    numeric_columns = [
        "average_occurrences_when_repeated",
        "share_of_rework_cases_pct",
    ]

    rework_activity_analysis[numeric_columns] = (
        rework_activity_analysis[numeric_columns].round(2)
    )

    rework_activity_analysis = rework_activity_analysis.sort_values(
        ["rework_cases", "total_rework_events"],
        ascending=[False, False],
    ).reset_index(drop=True)

    rework_activity_analysis.insert(
        0,
        "rework_activity_rank",
        range(1, len(rework_activity_analysis) + 1),
    )

    return rework_activity_analysis


def print_summary(
    rework_case_analysis: pd.DataFrame,
    rework_activity_analysis: pd.DataFrame,
) -> None:
    total_cases = len(rework_case_analysis)
    rework_cases = int(rework_case_analysis["has_rework"].sum())
    rework_case_share = rework_cases / total_cases * 100

    print("\n=== Rework Detection Summary ===")
    print(f"Operational cases analyzed: {total_cases:,}")
    print(f"Cases with rework: {rework_cases:,}")
    print(f"Rework case share: {rework_case_share:.2f}%")
    print(
        f"Average cycle time without rework: "
        f"{rework_case_analysis.loc[~rework_case_analysis['has_rework'], 'cycle_time_days'].mean():.2f} days"
    )
    print(
        f"Average cycle time with rework: "
        f"{rework_case_analysis.loc[rework_case_analysis['has_rework'], 'cycle_time_days'].mean():.2f} days"
    )

    print("\n=== Top 15 Rework Activities ===")

    if rework_activity_analysis.empty:
        print("No repeated activities detected.")
        return

    columns = [
        "rework_activity_rank",
        "activity",
        "rework_cases",
        "total_rework_events",
        "average_occurrences_when_repeated",
        "share_of_rework_cases_pct",
    ]

    print(rework_activity_analysis[columns].head(15).to_string(index=False))


def main() -> None:
    print("Loading event log and clean case table...")
    event_log, clean_cases = load_data()
    validate_columns(event_log, clean_cases)

    print("Filtering operational events...")
    operational_events = filter_operational_events(event_log, clean_cases)

    print("Calculating case-level rework features...")
    rework_case_analysis = calculate_case_rework_features(
        operational_events,
        clean_cases,
    )

    print("Calculating activity-level rework analysis...")
    rework_activity_analysis = calculate_rework_activity_analysis(
        operational_events,
        rework_case_analysis,
    )

    REWORK_CASE_ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rework_case_analysis.to_parquet(REWORK_CASE_ANALYSIS_PATH, index=False)
    rework_activity_analysis.to_parquet(REWORK_ACTIVITY_ANALYSIS_PATH, index=False)

    print_summary(rework_case_analysis, rework_activity_analysis)

    print(f"\nSaved rework case analysis to: {REWORK_CASE_ANALYSIS_PATH}")
    print(f"Saved rework activity analysis to: {REWORK_ACTIVITY_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()