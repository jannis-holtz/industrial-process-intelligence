from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"
CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
VARIANT_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "variant_analysis.parquet"

MAX_ACTIVITIES_IN_VARIANT_NAME = 12


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not EVENT_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Event log not found: {EVENT_LOG_PATH}\n"
            "Run scripts/02_convert_xes_to_parquet.py first."
        )

    if not CASE_TIMES_PATH.exists():
        raise FileNotFoundError(
            f"Clean case table not found: {CASE_TIMES_PATH}\n"
            "Run scripts/04_create_clean_case_table.py first."
        )

    event_log = pd.read_parquet(EVENT_LOG_PATH)
    clean_cases = pd.read_parquet(CASE_TIMES_PATH)

    return event_log, clean_cases


def build_case_variants(event_log: pd.DataFrame, clean_cases: pd.DataFrame) -> pd.DataFrame:
    clean_case_ids = set(clean_cases["case_id"])

    filtered_events = event_log[event_log["case_id"].isin(clean_case_ids)].copy()

    filtered_events = filtered_events.sort_values(
        ["case_id", "timestamp", "activity"]
    )

    case_variants = (
        filtered_events.groupby("case_id")
        .agg(
            variant_sequence=("activity", lambda values: tuple(values)),
            event_count_from_log=("activity", "count"),
            unique_activity_count=("activity", "nunique"),
        )
        .reset_index()
    )

    case_variants["variant_length"] = case_variants["variant_sequence"].apply(len)

    case_variants["variant_name"] = case_variants["variant_sequence"].apply(
        format_variant_name
    )

    case_variants = case_variants.merge(
        clean_cases[
            [
                "case_id",
                "cycle_time_days",
                "event_count",
                "activity_count",
                "company",
                "item_category",
                "document_type",
                "vendor",
            ]
        ],
        on="case_id",
        how="left",
    )

    return case_variants


def format_variant_name(sequence: tuple[str, ...]) -> str:
    if len(sequence) <= MAX_ACTIVITIES_IN_VARIANT_NAME:
        return " → ".join(sequence)

    visible_part = " → ".join(sequence[:MAX_ACTIVITIES_IN_VARIANT_NAME])
    remaining_steps = len(sequence) - MAX_ACTIVITIES_IN_VARIANT_NAME

    return f"{visible_part} → ... (+{remaining_steps} more)"


def calculate_variant_analysis(case_variants: pd.DataFrame) -> pd.DataFrame:
    total_cases = len(case_variants)

    variant_analysis = (
        case_variants.groupby("variant_name")
        .agg(
            case_count=("case_id", "count"),
            average_cycle_time_days=("cycle_time_days", "mean"),
            median_cycle_time_days=("cycle_time_days", "median"),
            p90_cycle_time_days=("cycle_time_days", lambda values: values.quantile(0.90)),
            average_event_count=("event_count", "mean"),
            average_activity_count=("activity_count", "mean"),
            variant_length=("variant_length", "median"),
            dominant_item_category=("item_category", lambda values: values.mode().iloc[0] if not values.mode().empty else None),
            dominant_document_type=("document_type", lambda values: values.mode().iloc[0] if not values.mode().empty else None),
        )
        .reset_index()
    )

    variant_analysis["share_of_cases_pct"] = (
        variant_analysis["case_count"] / total_cases * 100
    )

    variant_analysis["impact_score"] = (
        variant_analysis["share_of_cases_pct"]
        * variant_analysis["median_cycle_time_days"]
    )

    numeric_columns = [
        "average_cycle_time_days",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "average_event_count",
        "average_activity_count",
        "variant_length",
        "share_of_cases_pct",
        "impact_score",
    ]

    variant_analysis[numeric_columns] = variant_analysis[numeric_columns].round(2)

    variant_analysis = variant_analysis.sort_values(
        ["case_count", "median_cycle_time_days"],
        ascending=[False, False],
    ).reset_index(drop=True)

    variant_analysis.insert(0, "variant_rank", range(1, len(variant_analysis) + 1))

    return variant_analysis


def print_summary(variant_analysis: pd.DataFrame, case_variants: pd.DataFrame) -> None:
    print("\n=== Variant Intelligence Summary ===")
    print(f"Cases analyzed: {len(case_variants):,}")
    print(f"Distinct variants: {len(variant_analysis):,}")

    top_10_share = variant_analysis.head(10)["share_of_cases_pct"].sum()
    top_25_share = variant_analysis.head(25)["share_of_cases_pct"].sum()

    print(f"Top 10 variants cover: {top_10_share:.2f}% of cases")
    print(f"Top 25 variants cover: {top_25_share:.2f}% of cases")

    print("\n=== Top 10 Variants ===")
    columns = [
        "variant_rank",
        "case_count",
        "share_of_cases_pct",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "average_event_count",
        "dominant_item_category",
        "variant_name",
    ]

    print(variant_analysis[columns].head(10).to_string(index=False))

    print("\n=== Highest Impact Variants ===")
    impact_columns = [
        "variant_rank",
        "case_count",
        "share_of_cases_pct",
        "median_cycle_time_days",
        "impact_score",
        "variant_name",
    ]

    print(
        variant_analysis.sort_values("impact_score", ascending=False)[impact_columns]
        .head(10)
        .to_string(index=False)
    )


def main() -> None:
    print("Loading processed event log and clean case table...")
    event_log, clean_cases = load_data()

    print("Building case-level activity sequences...")
    case_variants = build_case_variants(event_log, clean_cases)

    print("Calculating variant-level KPIs...")
    variant_analysis = calculate_variant_analysis(case_variants)

    VARIANT_ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    variant_analysis.to_parquet(VARIANT_ANALYSIS_PATH, index=False)

    print_summary(variant_analysis, case_variants)

    print(f"\nSaved variant analysis to: {VARIANT_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()