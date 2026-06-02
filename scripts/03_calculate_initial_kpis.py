from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"


def load_event_log() -> pd.DataFrame:
    if not EVENT_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Processed event log not found: {EVENT_LOG_PATH}\n"
            "Run scripts/02_convert_xes_to_parquet.py first."
        )

    return pd.read_parquet(EVENT_LOG_PATH)


def calculate_case_cycle_times(df: pd.DataFrame) -> pd.DataFrame:
    case_times = (
        df.groupby("case_id")
        .agg(
            start_time=("timestamp", "min"),
            end_time=("timestamp", "max"),
            event_count=("activity", "count"),
            activity_count=("activity", "nunique"),
            company=("company", "first"),
            item_category=("item_category", "first"),
            document_type=("document_type", "first"),
            vendor=("vendor", "first"),
        )
        .reset_index()
    )

    case_times["cycle_time_days"] = (
        case_times["end_time"] - case_times["start_time"]
    ).dt.total_seconds() / 86_400

    return case_times


def print_kpis(df: pd.DataFrame, case_times: pd.DataFrame) -> None:
    print("\n=== Dataset Overview ===")
    print(f"Events: {len(df):,}")
    print(f"Cases: {df['case_id'].nunique():,}")
    print(f"Activities: {df['activity'].nunique():,}")
    print(f"Resources: {df['resource'].nunique():,}")

    print("\n=== Cycle Time KPIs ===")
    print(f"Average cycle time days: {case_times['cycle_time_days'].mean():.2f}")
    print(f"Median cycle time days: {case_times['cycle_time_days'].median():.2f}")
    print(f"P75 cycle time days: {case_times['cycle_time_days'].quantile(0.75):.2f}")
    print(f"P90 cycle time days: {case_times['cycle_time_days'].quantile(0.90):.2f}")
    print(f"P95 cycle time days: {case_times['cycle_time_days'].quantile(0.95):.2f}")
    print(f"Max cycle time days: {case_times['cycle_time_days'].max():.2f}")

    print("\n=== Data Quality Flags ===")
    suspicious_cases = case_times[case_times["cycle_time_days"] > 365]
    print(f"Cases with cycle time > 365 days: {len(suspicious_cases):,}")

    old_events = df[df["timestamp"].dt.year < 2018]
    future_events = df[df["timestamp"].dt.year > 2019]
    print(f"Events before 2018: {len(old_events):,}")
    print(f"Events after 2019: {len(future_events):,}")

    print("\n=== Top 10 Activities ===")
    print(df["activity"].value_counts().head(10))

    print("\n=== Item Categories ===")
    print(df["item_category"].value_counts())

    print("\n=== Document Types ===")
    print(df["document_type"].value_counts().head(10))

    print("\n=== Slowest 10 Cases ===")
    slowest_cases = case_times.sort_values("cycle_time_days", ascending=False).head(10)
    print(
        slowest_cases[
            [
                "case_id",
                "cycle_time_days",
                "event_count",
                "activity_count",
                "company",
                "item_category",
                "document_type",
            ]
        ]
    )


def main() -> None:
    print(f"Loading processed event log: {EVENT_LOG_PATH}")
    df = load_event_log()

    print("Calculating case cycle times...")
    case_times = calculate_case_cycle_times(df)

    output_path = PROJECT_ROOT / "data" / "processed" / "case_cycle_times.parquet"
    case_times.to_parquet(output_path, index=False)

    print_kpis(df, case_times)

    print(f"\nSaved case-level KPI table to: {output_path}")


if __name__ == "__main__":
    main()