from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
ROOT_CAUSE_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "root_cause_analysis.parquet"

SLOW_CASE_QUANTILE = 0.90
MIN_CASE_COUNT = 50

ROOT_CAUSE_DIMENSIONS = [
    "item_category",
    "document_type",
    "company",
    "vendor",
]


def load_clean_cases() -> pd.DataFrame:
    if not CLEAN_CASE_TIMES_PATH.exists():
        raise FileNotFoundError(
            f"Clean case table not found: {CLEAN_CASE_TIMES_PATH}\n"
            "Run scripts/04_create_clean_case_table.py first."
        )

    return pd.read_parquet(CLEAN_CASE_TIMES_PATH)


def validate_columns(clean_cases: pd.DataFrame) -> None:
    required_columns = [
        "case_id",
        "cycle_time_days",
        "event_count",
        "activity_count",
        *ROOT_CAUSE_DIMENSIONS,
    ]

    missing_columns = [
        column for column in required_columns if column not in clean_cases.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def calculate_dimension_root_cause(
    clean_cases: pd.DataFrame,
    dimension: str,
    slow_case_threshold: float,
) -> pd.DataFrame:
    enriched = clean_cases.copy()
    enriched["is_slow_case"] = enriched["cycle_time_days"] >= slow_case_threshold

    grouped = (
        enriched.groupby(dimension, dropna=False)
        .agg(
            cases=("case_id", "count"),
            slow_cases=("is_slow_case", "sum"),
            average_cycle_time_days=("cycle_time_days", "mean"),
            median_cycle_time_days=("cycle_time_days", "median"),
            p90_cycle_time_days=("cycle_time_days", lambda values: values.quantile(0.90)),
            average_event_count=("event_count", "mean"),
            average_activity_count=("activity_count", "mean"),
        )
        .reset_index()
        .rename(columns={dimension: "dimension_value"})
    )

    grouped["dimension"] = dimension

    grouped = grouped[grouped["cases"] >= MIN_CASE_COUNT].copy()

    grouped["case_share_pct"] = grouped["cases"] / len(clean_cases) * 100
    grouped["slow_case_share_pct"] = grouped["slow_cases"] / grouped["cases"] * 100
    grouped["slow_case_contribution_pct"] = (
        grouped["slow_cases"] / enriched["is_slow_case"].sum() * 100
    )

    overall_slow_case_share = enriched["is_slow_case"].mean() * 100

    grouped["slow_case_lift"] = (
        grouped["slow_case_share_pct"] / overall_slow_case_share
    )

    grouped["impact_score"] = (
        grouped["slow_case_contribution_pct"]
        * grouped["slow_case_lift"]
    )

    numeric_columns = [
        "average_cycle_time_days",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "average_event_count",
        "average_activity_count",
        "case_share_pct",
        "slow_case_share_pct",
        "slow_case_contribution_pct",
        "slow_case_lift",
        "impact_score",
    ]

    grouped[numeric_columns] = grouped[numeric_columns].round(2)

    grouped = grouped[
        [
            "dimension",
            "dimension_value",
            "cases",
            "case_share_pct",
            "slow_cases",
            "slow_case_share_pct",
            "slow_case_contribution_pct",
            "slow_case_lift",
            "average_cycle_time_days",
            "median_cycle_time_days",
            "p90_cycle_time_days",
            "average_event_count",
            "average_activity_count",
            "impact_score",
        ]
    ]

    return grouped


def calculate_root_cause_analysis(clean_cases: pd.DataFrame) -> pd.DataFrame:
    validate_columns(clean_cases)

    slow_case_threshold = clean_cases["cycle_time_days"].quantile(SLOW_CASE_QUANTILE)

    results = []

    for dimension in ROOT_CAUSE_DIMENSIONS:
        dimension_result = calculate_dimension_root_cause(
            clean_cases=clean_cases,
            dimension=dimension,
            slow_case_threshold=slow_case_threshold,
        )
        results.append(dimension_result)

    root_cause_analysis = pd.concat(results, ignore_index=True)

    root_cause_analysis["slow_case_threshold_days"] = round(slow_case_threshold, 2)

    root_cause_analysis = root_cause_analysis.sort_values(
        ["impact_score", "slow_case_contribution_pct"],
        ascending=[False, False],
    ).reset_index(drop=True)

    root_cause_analysis.insert(
        0,
        "root_cause_rank",
        range(1, len(root_cause_analysis) + 1),
    )

    return root_cause_analysis


def print_summary(root_cause_analysis: pd.DataFrame) -> None:
    print("\n=== Root Cause Analysis Summary ===")
    print(f"Root cause signals: {len(root_cause_analysis):,}")
    print(
        f"Slow case threshold: "
        f"{root_cause_analysis['slow_case_threshold_days'].iloc[0]:.2f} days"
    )
    print(f"Minimum case count threshold: {MIN_CASE_COUNT:,}")

    print("\n=== Top 15 Root Cause Signals ===")
    columns = [
        "root_cause_rank",
        "dimension",
        "dimension_value",
        "cases",
        "slow_cases",
        "slow_case_share_pct",
        "slow_case_contribution_pct",
        "slow_case_lift",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "impact_score",
    ]

    print(root_cause_analysis[columns].head(15).to_string(index=False))


def main() -> None:
    print("Loading clean case table...")
    clean_cases = load_clean_cases()

    print("Calculating root cause signals...")
    root_cause_analysis = calculate_root_cause_analysis(clean_cases)

    ROOT_CAUSE_ANALYSIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    root_cause_analysis.to_parquet(ROOT_CAUSE_ANALYSIS_PATH, index=False)

    print_summary(root_cause_analysis)

    print(f"\nSaved root cause analysis to: {ROOT_CAUSE_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()