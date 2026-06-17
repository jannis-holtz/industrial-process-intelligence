from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BOTTLENECK_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "bottleneck_analysis.parquet"
DELAY_COST_ESTIMATE_PATH = PROJECT_ROOT / "data" / "processed" / "delay_cost_estimate.parquet"

ASSUMED_COST_PER_WAITING_DAY = 100


def load_bottleneck_analysis() -> pd.DataFrame:
    if not BOTTLENECK_ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Bottleneck analysis not found: {BOTTLENECK_ANALYSIS_PATH}\n"
            "Run scripts/06_calculate_bottlenecks.py first."
        )

    return pd.read_parquet(BOTTLENECK_ANALYSIS_PATH)


def validate_columns(bottleneck_analysis: pd.DataFrame) -> None:
    required_columns = [
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

    missing_columns = [
        column for column in required_columns if column not in bottleneck_analysis.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def calculate_delay_cost_estimate(bottleneck_analysis: pd.DataFrame) -> pd.DataFrame:
    delay_cost = bottleneck_analysis.copy()

    delay_cost["assumed_cost_per_waiting_day"] = ASSUMED_COST_PER_WAITING_DAY
    delay_cost["estimated_delay_cost"] = (
        delay_cost["total_waiting_time_days"] * ASSUMED_COST_PER_WAITING_DAY
    )

    total_estimated_cost = delay_cost["estimated_delay_cost"].sum()

    delay_cost["share_of_estimated_delay_cost_pct"] = (
        delay_cost["estimated_delay_cost"] / total_estimated_cost * 100
    )

    delay_cost["estimated_cost_per_case"] = (
        delay_cost["estimated_delay_cost"] / delay_cost["transition_count"]
    )

    numeric_columns = [
        "estimated_delay_cost",
        "share_of_estimated_delay_cost_pct",
        "estimated_cost_per_case",
    ]

    delay_cost[numeric_columns] = delay_cost[numeric_columns].round(2)

    delay_cost = delay_cost.sort_values(
        ["estimated_delay_cost", "impact_score"],
        ascending=[False, False],
    ).reset_index(drop=True)

    delay_cost.insert(
        0,
        "delay_cost_rank",
        range(1, len(delay_cost) + 1),
    )

    output_columns = [
        "delay_cost_rank",
        "bottleneck_rank",
        "transition",
        "transition_count",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "total_waiting_time_days",
        "share_of_total_waiting_time_pct",
        "assumed_cost_per_waiting_day",
        "estimated_delay_cost",
        "estimated_cost_per_case",
        "share_of_estimated_delay_cost_pct",
        "impact_score",
        "dominant_item_category",
    ]

    return delay_cost[output_columns]


def print_summary(delay_cost_estimate: pd.DataFrame) -> None:
    total_estimated_cost = delay_cost_estimate["estimated_delay_cost"].sum()
    top_cost_driver = delay_cost_estimate.iloc[0]

    print("\n=== Delay Cost Estimate Summary ===")
    print(f"Assumed cost per waiting day: {ASSUMED_COST_PER_WAITING_DAY:,} cost units")
    print(f"Estimated total delay cost: {total_estimated_cost:,.2f} cost units")
    print(
        f"Top cost driver: {top_cost_driver['transition']} "
        f"({top_cost_driver['share_of_estimated_delay_cost_pct']:.2f}% of estimated delay cost)"
    )

    print("\n=== Top 15 Delay Cost Drivers ===")

    columns = [
        "delay_cost_rank",
        "transition",
        "transition_count",
        "median_waiting_time_days",
        "total_waiting_time_days",
        "estimated_delay_cost",
        "estimated_cost_per_case",
        "share_of_estimated_delay_cost_pct",
    ]

    print(delay_cost_estimate[columns].head(15).to_string(index=False))


def main() -> None:
    print("Loading bottleneck analysis...")
    bottleneck_analysis = load_bottleneck_analysis()
    validate_columns(bottleneck_analysis)

    print("Calculating delay cost estimates...")
    delay_cost_estimate = calculate_delay_cost_estimate(bottleneck_analysis)

    DELAY_COST_ESTIMATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    delay_cost_estimate.to_parquet(DELAY_COST_ESTIMATE_PATH, index=False)

    print_summary(delay_cost_estimate)

    print(f"\nSaved delay cost estimate to: {DELAY_COST_ESTIMATE_PATH}")


if __name__ == "__main__":
    main()