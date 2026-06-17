from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
SLA_METRICS_PATH = PROJECT_ROOT / "data" / "processed" / "sla_metrics.parquet"
SLA_BREAKDOWN_PATH = PROJECT_ROOT / "data" / "processed" / "sla_breakdown.parquet"

SLA_THRESHOLD_DAYS = 120

BREAKDOWN_DIMENSIONS = [
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
        *BREAKDOWN_DIMENSIONS,
    ]

    missing_columns = [
        column for column in required_columns if column not in clean_cases.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def calculate_sla_metrics(clean_cases: pd.DataFrame) -> pd.DataFrame:
    enriched = clean_cases.copy()
    enriched["sla_breached"] = enriched["cycle_time_days"] > SLA_THRESHOLD_DAYS

    total_cases = len(enriched)
    breached_cases = int(enriched["sla_breached"].sum())
    fulfilled_cases = total_cases - breached_cases

    sla_metrics = pd.DataFrame(
        [
            {
                "metric": "analytical_sla_threshold_days",
                "value": SLA_THRESHOLD_DAYS,
                "unit": "days",
                "description": "Analytical SLA threshold used for process monitoring.",
            },
            {
                "metric": "total_operational_cases",
                "value": total_cases,
                "unit": "cases",
                "description": "Number of operational cases after KPI filter.",
            },
            {
                "metric": "sla_fulfilled_cases",
                "value": fulfilled_cases,
                "unit": "cases",
                "description": "Cases with cycle_time_days <= SLA threshold.",
            },
            {
                "metric": "sla_breached_cases",
                "value": breached_cases,
                "unit": "cases",
                "description": "Cases with cycle_time_days > SLA threshold.",
            },
            {
                "metric": "sla_compliance_rate_pct",
                "value": round(fulfilled_cases / total_cases * 100, 2),
                "unit": "percent",
                "description": "Share of cases fulfilling the analytical SLA.",
            },
            {
                "metric": "sla_breach_rate_pct",
                "value": round(breached_cases / total_cases * 100, 2),
                "unit": "percent",
                "description": "Share of cases breaching the analytical SLA.",
            },
        ]
    )

    return sla_metrics


def calculate_sla_breakdown(clean_cases: pd.DataFrame) -> pd.DataFrame:
    enriched = clean_cases.copy()
    enriched["sla_breached"] = enriched["cycle_time_days"] > SLA_THRESHOLD_DAYS

    results = []

    for dimension in BREAKDOWN_DIMENSIONS:
        grouped = (
            enriched.groupby(dimension, dropna=False)
            .agg(
                cases=("case_id", "count"),
                sla_breaches=("sla_breached", "sum"),
                average_cycle_time_days=("cycle_time_days", "mean"),
                median_cycle_time_days=("cycle_time_days", "median"),
                p90_cycle_time_days=("cycle_time_days", lambda values: values.quantile(0.90)),
            )
            .reset_index()
            .rename(columns={dimension: "dimension_value"})
        )

        grouped["dimension"] = dimension
        grouped["case_share_pct"] = grouped["cases"] / len(enriched) * 100
        grouped["sla_breach_rate_pct"] = grouped["sla_breaches"] / grouped["cases"] * 100
        grouped["sla_breach_contribution_pct"] = (
            grouped["sla_breaches"] / enriched["sla_breached"].sum() * 100
        )

        grouped["impact_score"] = (
            grouped["sla_breach_contribution_pct"]
            * grouped["sla_breach_rate_pct"]
            / 100
        )

        results.append(grouped)

    sla_breakdown = pd.concat(results, ignore_index=True)

    numeric_columns = [
        "case_share_pct",
        "sla_breach_rate_pct",
        "sla_breach_contribution_pct",
        "average_cycle_time_days",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "impact_score",
    ]

    sla_breakdown[numeric_columns] = sla_breakdown[numeric_columns].round(2)

    sla_breakdown = sla_breakdown.sort_values(
        ["impact_score", "sla_breach_contribution_pct"],
        ascending=[False, False],
    ).reset_index(drop=True)

    sla_breakdown.insert(
        0,
        "sla_rank",
        range(1, len(sla_breakdown) + 1),
    )

    sla_breakdown["sla_threshold_days"] = SLA_THRESHOLD_DAYS

    return sla_breakdown[
        [
            "sla_rank",
            "dimension",
            "dimension_value",
            "cases",
            "case_share_pct",
            "sla_breaches",
            "sla_breach_rate_pct",
            "sla_breach_contribution_pct",
            "average_cycle_time_days",
            "median_cycle_time_days",
            "p90_cycle_time_days",
            "impact_score",
            "sla_threshold_days",
        ]
    ]


def print_summary(sla_metrics: pd.DataFrame, sla_breakdown: pd.DataFrame) -> None:
    metric_lookup = dict(zip(sla_metrics["metric"], sla_metrics["value"]))

    print("\n=== SLA Metrics Summary ===")
    print(f"Analytical SLA threshold: {SLA_THRESHOLD_DAYS} days")
    print(f"Operational cases: {int(metric_lookup['total_operational_cases']):,}")
    print(f"SLA fulfilled cases: {int(metric_lookup['sla_fulfilled_cases']):,}")
    print(f"SLA breached cases: {int(metric_lookup['sla_breached_cases']):,}")
    print(f"SLA compliance rate: {metric_lookup['sla_compliance_rate_pct']:.2f}%")
    print(f"SLA breach rate: {metric_lookup['sla_breach_rate_pct']:.2f}%")

    print("\n=== Top 15 SLA Breach Signals ===")
    columns = [
        "sla_rank",
        "dimension",
        "dimension_value",
        "cases",
        "sla_breaches",
        "sla_breach_rate_pct",
        "sla_breach_contribution_pct",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "impact_score",
    ]

    print(sla_breakdown[columns].head(15).to_string(index=False))


def main() -> None:
    print("Loading clean case table...")
    clean_cases = load_clean_cases()
    validate_columns(clean_cases)

    print("Calculating SLA metrics...")
    sla_metrics = calculate_sla_metrics(clean_cases)
    sla_breakdown = calculate_sla_breakdown(clean_cases)

    SLA_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    sla_metrics.to_parquet(SLA_METRICS_PATH, index=False)
    sla_breakdown.to_parquet(SLA_BREAKDOWN_PATH, index=False)

    print_summary(sla_metrics, sla_breakdown)

    print(f"\nSaved SLA metrics to: {SLA_METRICS_PATH}")
    print(f"Saved SLA breakdown to: {SLA_BREAKDOWN_PATH}")


if __name__ == "__main__":
    main()