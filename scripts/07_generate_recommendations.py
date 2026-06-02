from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VARIANT_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "variant_analysis.parquet"
BOTTLENECK_ANALYSIS_PATH = PROJECT_ROOT / "data" / "processed" / "bottleneck_analysis.parquet"
RECOMMENDATIONS_PATH = PROJECT_ROOT / "data" / "processed" / "recommendations.parquet"

TOP_BOTTLENECK_LIMIT = 5
TOP_VARIANT_LIMIT = 5


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not VARIANT_ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Variant analysis not found: {VARIANT_ANALYSIS_PATH}\n"
            "Run scripts/05_calculate_variant_analysis.py first."
        )

    if not BOTTLENECK_ANALYSIS_PATH.exists():
        raise FileNotFoundError(
            f"Bottleneck analysis not found: {BOTTLENECK_ANALYSIS_PATH}\n"
            "Run scripts/06_calculate_bottlenecks.py first."
        )

    variant_analysis = pd.read_parquet(VARIANT_ANALYSIS_PATH)
    bottleneck_analysis = pd.read_parquet(BOTTLENECK_ANALYSIS_PATH)

    return variant_analysis, bottleneck_analysis


def classify_priority(score_rank: int) -> str:
    if score_rank <= 2:
        return "High"
    if score_rank <= 5:
        return "Medium"
    return "Low"


def generate_bottleneck_recommendations(
    bottleneck_analysis: pd.DataFrame,
) -> list[dict]:
    recommendations = []

    top_bottlenecks = bottleneck_analysis.head(TOP_BOTTLENECK_LIMIT)

    for index, row in top_bottlenecks.iterrows():
        priority_rank = index + 1

        recommendations.append(
            {
                "priority_rank": priority_rank,
                "priority": classify_priority(priority_rank),
                "recommendation_type": "Bottleneck",
                "focus_area": row["transition"],
                "observed_issue": (
                    f"Transition contributes {row['share_of_total_waiting_time_pct']:.2f}% "
                    f"of total observed waiting time with a median wait of "
                    f"{row['median_waiting_time_days']:.2f} days."
                ),
                "business_rationale": (
                    "This transition combines high waiting-time contribution with operational frequency. "
                    "Reducing delays here is likely to improve overall process throughput."
                ),
                "expected_lever": "Reduce waiting time between process activities",
                "supporting_metric": row["impact_score"],
                "source_module": "Bottleneck Analysis",
            }
        )

    return recommendations


def generate_variant_recommendations(
    variant_analysis: pd.DataFrame,
    start_priority_rank: int,
) -> list[dict]:
    recommendations = []

    high_impact_variants = (
        variant_analysis.sort_values("impact_score", ascending=False)
        .head(TOP_VARIANT_LIMIT)
        .reset_index(drop=True)
    )

    for index, row in high_impact_variants.iterrows():
        priority_rank = start_priority_rank + index

        recommendations.append(
            {
                "priority_rank": priority_rank,
                "priority": classify_priority(priority_rank),
                "recommendation_type": "Variant",
                "focus_area": f"Variant {int(row['variant_rank'])}",
                "observed_issue": (
                    f"Variant covers {row['share_of_cases_pct']:.2f}% of cases "
                    f"with a median cycle time of {row['median_cycle_time_days']:.2f} days."
                ),
                "business_rationale": (
                    "This variant combines relevant case volume with elevated cycle time. "
                    "It should be reviewed for avoidable rework, delays or unnecessary process steps."
                ),
                "expected_lever": "Standardize or improve high-impact process variant",
                "supporting_metric": row["impact_score"],
                "source_module": "Variant Intelligence",
            }
        )

    return recommendations


def generate_recommendations(
    variant_analysis: pd.DataFrame,
    bottleneck_analysis: pd.DataFrame,
) -> pd.DataFrame:
    bottleneck_recommendations = generate_bottleneck_recommendations(
        bottleneck_analysis
    )

    variant_recommendations = generate_variant_recommendations(
        variant_analysis,
        start_priority_rank=len(bottleneck_recommendations) + 1,
    )

    recommendations = pd.DataFrame(
        bottleneck_recommendations + variant_recommendations
    )

    recommendations = recommendations.sort_values("priority_rank").reset_index(drop=True)

    return recommendations


def print_summary(recommendations: pd.DataFrame) -> None:
    print("\n=== Recommendation Layer Summary ===")
    print(f"Recommendations generated: {len(recommendations):,}")

    print("\n=== Recommendations ===")
    columns = [
        "priority_rank",
        "priority",
        "recommendation_type",
        "focus_area",
        "observed_issue",
        "expected_lever",
        "source_module",
    ]

    print(recommendations[columns].to_string(index=False))


def main() -> None:
    print("Loading variant and bottleneck analysis...")
    variant_analysis, bottleneck_analysis = load_data()

    print("Generating rule-based recommendations...")
    recommendations = generate_recommendations(
        variant_analysis,
        bottleneck_analysis,
    )

    RECOMMENDATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    recommendations.to_parquet(RECOMMENDATIONS_PATH, index=False)

    print_summary(recommendations)

    print(f"\nSaved recommendations to: {RECOMMENDATIONS_PATH}")


if __name__ == "__main__":
    main()