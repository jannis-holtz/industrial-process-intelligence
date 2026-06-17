from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

EXPECTED_FILES = {
    "event_log": PROCESSED_DIR / "event_log.parquet",
    "case_cycle_times": PROCESSED_DIR / "case_cycle_times.parquet",
    "case_cycle_times_clean": PROCESSED_DIR / "case_cycle_times_clean.parquet",
    "data_quality_report": PROCESSED_DIR / "data_quality_report.csv",
    "variant_analysis": PROCESSED_DIR / "variant_analysis.parquet",
    "bottleneck_analysis": PROCESSED_DIR / "bottleneck_analysis.parquet",
    "recommendations": PROCESSED_DIR / "recommendations.parquet",
    "root_cause_analysis": PROCESSED_DIR / "root_cause_analysis.parquet",
    "sla_metrics": PROCESSED_DIR / "sla_metrics.parquet",
    "sla_breakdown": PROCESSED_DIR / "sla_breakdown.parquet",
    "rework_case_analysis": PROCESSED_DIR / "rework_case_analysis.parquet",
    "rework_activity_analysis": PROCESSED_DIR / "rework_activity_analysis.parquet",
    "process_edges": PROCESSED_DIR / "process_edges.parquet",
    "process_activities": PROCESSED_DIR / "process_activities.parquet",
    "delay_cost_estimate": PROCESSED_DIR / "delay_cost_estimate.parquet",
}

REQUIRED_COLUMNS = {
    "event_log": [
        "case_id",
        "activity",
        "timestamp",
    ],
    "case_cycle_times": [
        "case_id",
        "cycle_time_days",
        "event_count",
        "activity_count",
    ],
    "case_cycle_times_clean": [
        "case_id",
        "cycle_time_days",
        "event_count",
        "activity_count",
    ],
    "data_quality_report": [
        "check",
        "affected_cases",
    ],
    "variant_analysis": [
        "variant_rank",
        "variant_name",
        "case_count",
        "share_of_cases_pct",
        "median_cycle_time_days",
        "impact_score",
    ],
    "bottleneck_analysis": [
        "bottleneck_rank",
        "transition",
        "transition_count",
        "median_waiting_time_days",
        "share_of_total_waiting_time_pct",
        "impact_score",
    ],
    "recommendations": [
        "priority_rank",
        "priority",
        "recommendation_type",
        "focus_area",
        "observed_issue",
        "business_rationale",
        "expected_lever",
        "source_module",
    ],
    "root_cause_analysis": [
        "root_cause_rank",
        "dimension",
        "dimension_value",
        "cases",
        "slow_cases",
        "slow_case_share_pct",
        "slow_case_lift",
        "impact_score",
    ],
    "sla_metrics": [
        "metric",
        "value",
        "unit",
        "description",
    ],
    "sla_breakdown": [
        "sla_rank",
        "dimension",
        "dimension_value",
        "cases",
        "sla_breaches",
        "sla_breach_rate_pct",
        "sla_breach_contribution_pct",
        "impact_score",
        "sla_threshold_days",
    ],
    "rework_case_analysis": [
        "case_id",
        "cycle_time_days",
        "event_count",
        "activity_count",
        "has_rework",
        "repeated_activity_count",
        "rework_event_count",
    ],
    "rework_activity_analysis": [
        "rework_activity_rank",
        "activity",
        "rework_cases",
        "total_rework_events",
        "average_occurrences_when_repeated",
        "share_of_rework_cases_pct",
    ],
    "process_edges": [
        "edge_rank",
        "source_activity",
        "target_activity",
        "transition",
        "transition_count",
        "case_count",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "share_of_waiting_time_pct",
        "flow_impact_score",
    ],
    "process_activities": [
        "activity_rank",
        "activity",
        "event_count",
        "case_count",
        "share_of_events_pct",
        "share_of_cases_pct",
    ],
    "delay_cost_estimate": [
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
    ],
}


def load_table(name: str, path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)

    if path.suffix == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Unsupported file format for {name}: {path.suffix}")


def validate_expected_files() -> list[str]:
    errors = []

    for name, path in EXPECTED_FILES.items():
        if not path.exists():
            errors.append(f"[MISSING FILE] {name}: {path}")

    return errors


def validate_table_not_empty(name: str, df: pd.DataFrame) -> list[str]:
    errors = []

    if df.empty:
        errors.append(f"[EMPTY TABLE] {name}")

    return errors


def validate_required_columns(name: str, df: pd.DataFrame) -> list[str]:
    errors = []

    required_columns = REQUIRED_COLUMNS.get(name, [])
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        errors.append(f"[MISSING COLUMNS] {name}: {missing_columns}")

    return errors


def validate_case_consistency(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    raw_cases = tables["case_cycle_times"]
    clean_cases = tables["case_cycle_times_clean"]

    if len(clean_cases) > len(raw_cases):
        errors.append(
            "[CASE CONSISTENCY] Clean case table has more cases than raw case table."
        )

    if clean_cases["cycle_time_days"].max() > 365:
        errors.append(
            "[OPERATIONAL FILTER] Clean case table contains cycle_time_days > 365."
        )

    if raw_cases["cycle_time_days"].median() <= 0:
        errors.append("[KPI PLAUSIBILITY] Raw median cycle time is <= 0.")

    if clean_cases["cycle_time_days"].median() <= 0:
        errors.append("[KPI PLAUSIBILITY] Clean median cycle time is <= 0.")

    return errors


def validate_variant_analysis(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    variant_analysis = tables["variant_analysis"]
    clean_cases = tables["case_cycle_times_clean"]

    if variant_analysis["case_count"].sum() <= 0:
        errors.append("[VARIANT ANALYSIS] Sum of variant case_count is <= 0.")

    if variant_analysis["variant_rank"].duplicated().any():
        errors.append("[VARIANT ANALYSIS] Duplicate variant_rank values detected.")

    variant_case_coverage = (
        variant_analysis["case_count"].sum() / len(clean_cases) * 100
    )

    if variant_case_coverage < 99:
        errors.append(
            f"[VARIANT ANALYSIS] Variant case coverage is below 99% "
            f"({variant_case_coverage:.2f}%). This may indicate missing variants."
        )

    return errors


def validate_bottleneck_analysis(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    bottleneck_analysis = tables["bottleneck_analysis"]

    if bottleneck_analysis["transition_count"].sum() <= 0:
        errors.append("[BOTTLENECK ANALYSIS] Sum of transition_count is <= 0.")

    if bottleneck_analysis["median_waiting_time_days"].min() < 0:
        errors.append("[BOTTLENECK ANALYSIS] Negative median waiting time detected.")

    if bottleneck_analysis["share_of_total_waiting_time_pct"].sum() <= 0:
        errors.append(
            "[BOTTLENECK ANALYSIS] Sum of share_of_total_waiting_time_pct is <= 0."
        )

    return errors


def validate_recommendations(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    recommendations = tables["recommendations"]

    if len(recommendations) < 1:
        errors.append("[RECOMMENDATIONS] No recommendations generated.")

    valid_priorities = {"High", "Medium", "Low"}
    invalid_priorities = set(recommendations["priority"]) - valid_priorities

    if invalid_priorities:
        errors.append(
            f"[RECOMMENDATIONS] Invalid priority values: {invalid_priorities}"
        )

    if recommendations["priority_rank"].duplicated().any():
        errors.append("[RECOMMENDATIONS] Duplicate priority_rank values detected.")

    return errors


def validate_root_cause_analysis(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    root_cause_analysis = tables["root_cause_analysis"]

    if root_cause_analysis["cases"].sum() <= 0:
        errors.append("[ROOT CAUSE] Sum of cases is <= 0.")

    if root_cause_analysis["slow_cases"].sum() <= 0:
        errors.append("[ROOT CAUSE] Sum of slow_cases is <= 0.")

    if root_cause_analysis["slow_case_lift"].max() <= 1:
        errors.append(
            "[ROOT CAUSE] No dimension has slow_case_lift > 1. "
            "This may indicate weak or incorrect signal calculation."
        )

    return errors


def validate_sla_outputs(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    sla_metrics = tables["sla_metrics"]
    sla_breakdown = tables["sla_breakdown"]

    required_metrics = {
        "analytical_sla_threshold_days",
        "total_operational_cases",
        "sla_fulfilled_cases",
        "sla_breached_cases",
        "sla_compliance_rate_pct",
        "sla_breach_rate_pct",
    }

    existing_metrics = set(sla_metrics["metric"])
    missing_metrics = required_metrics - existing_metrics

    if missing_metrics:
        errors.append(f"[SLA] Missing SLA metrics: {missing_metrics}")

    metric_lookup = dict(zip(sla_metrics["metric"], sla_metrics["value"]))

    if "sla_compliance_rate_pct" in metric_lookup:
        compliance_rate = float(metric_lookup["sla_compliance_rate_pct"])
        if compliance_rate < 0 or compliance_rate > 100:
            errors.append("[SLA] SLA compliance rate is outside 0-100%.")

    if "sla_breach_rate_pct" in metric_lookup:
        breach_rate = float(metric_lookup["sla_breach_rate_pct"])
        if breach_rate < 0 or breach_rate > 100:
            errors.append("[SLA] SLA breach rate is outside 0-100%.")

    if sla_breakdown["cases"].sum() <= 0:
        errors.append("[SLA] SLA breakdown cases sum is <= 0.")

    if sla_breakdown["sla_breaches"].sum() <= 0:
        errors.append("[SLA] SLA breakdown breach sum is <= 0.")

    return errors


def validate_rework_outputs(tables: dict[str, pd.DataFrame]) -> list[str]:
    errors = []

    rework_case_analysis = tables["rework_case_analysis"]
    rework_activity_analysis = tables["rework_activity_analysis"]

    if rework_case_analysis["case_id"].duplicated().any():
        errors.append("[REWORK] Duplicate case_id values in rework case analysis.")

    if rework_case_analysis["rework_event_count"].min() < 0:
        errors.append("[REWORK] Negative rework_event_count detected.")

    if rework_case_analysis["has_rework"].sum() <= 0:
        errors.append("[REWORK] No rework cases detected.")

    if rework_activity_analysis["rework_cases"].sum() <= 0:
        errors.append("[REWORK] Rework activity cases sum is <= 0.")

    if rework_activity_analysis["total_rework_events"].sum() <= 0:
        errors.append("[REWORK] Rework activity events sum is <= 0.")

    return errors


def validate_process_explorer_outputs(
    tables: dict[str, pd.DataFrame],
) -> list[str]:
    errors = []

    process_edges = tables["process_edges"]
    process_activities = tables["process_activities"]

    if process_edges["transition_count"].sum() <= 0:
        errors.append("[PROCESS EXPLORER] Sum of transition_count is <= 0.")

    if process_edges["case_count"].sum() <= 0:
        errors.append("[PROCESS EXPLORER] Sum of edge case_count is <= 0.")

    if process_edges["median_waiting_time_days"].min() < 0:
        errors.append("[PROCESS EXPLORER] Negative median waiting time detected.")

    if process_activities["event_count"].sum() <= 0:
        errors.append("[PROCESS EXPLORER] Sum of activity event_count is <= 0.")

    if process_activities["case_count"].sum() <= 0:
        errors.append("[PROCESS EXPLORER] Sum of activity case_count is <= 0.")

    if process_activities["activity"].duplicated().any():
        errors.append("[PROCESS EXPLORER] Duplicate activity values detected.")

    return errors


def validate_delay_cost_estimate_outputs(
    tables: dict[str, pd.DataFrame],
) -> list[str]:
    errors = []

    delay_cost_estimate = tables["delay_cost_estimate"]

    if delay_cost_estimate["estimated_delay_cost"].sum() <= 0:
        errors.append("[DELAY COST] Sum of estimated_delay_cost is <= 0.")

    if delay_cost_estimate["estimated_cost_per_case"].min() < 0:
        errors.append("[DELAY COST] Negative estimated_cost_per_case detected.")

    if delay_cost_estimate["assumed_cost_per_waiting_day"].nunique() != 1:
        errors.append("[DELAY COST] More than one cost assumption detected.")

    if delay_cost_estimate["share_of_estimated_delay_cost_pct"].sum() < 99:
        errors.append("[DELAY COST] Estimated cost share sum is below 99%.")

    if delay_cost_estimate["delay_cost_rank"].duplicated().any():
        errors.append("[DELAY COST] Duplicate delay_cost_rank values detected.")

    return errors


def load_all_available_tables() -> tuple[dict[str, pd.DataFrame], list[str]]:
    tables = {}
    errors = validate_expected_files()

    if errors:
        return tables, errors

    for name, path in EXPECTED_FILES.items():
        try:
            tables[name] = load_table(name, path)
        except Exception as error:
            errors.append(f"[LOAD ERROR] {name}: {error}")

    return tables, errors


def run_validation() -> list[str]:
    tables, errors = load_all_available_tables()

    if errors:
        return errors

    for name, df in tables.items():
        errors.extend(validate_table_not_empty(name, df))
        errors.extend(validate_required_columns(name, df))

    if errors:
        return errors

    errors.extend(validate_case_consistency(tables))
    errors.extend(validate_variant_analysis(tables))
    errors.extend(validate_bottleneck_analysis(tables))
    errors.extend(validate_recommendations(tables))
    errors.extend(validate_root_cause_analysis(tables))
    errors.extend(validate_sla_outputs(tables))
    errors.extend(validate_rework_outputs(tables))
    errors.extend(validate_process_explorer_outputs(tables))
    errors.extend(validate_delay_cost_estimate_outputs(tables))

    return errors


def print_success_summary(tables: dict[str, pd.DataFrame]) -> None:
    raw_cases = tables["case_cycle_times"]
    clean_cases = tables["case_cycle_times_clean"]
    event_log = tables["event_log"]
    variants = tables["variant_analysis"]
    bottlenecks = tables["bottleneck_analysis"]
    recommendations = tables["recommendations"]
    root_cause = tables["root_cause_analysis"]
    sla_metrics = tables["sla_metrics"]
    sla_breakdown = tables["sla_breakdown"]
    rework_cases = tables["rework_case_analysis"]
    rework_activities = tables["rework_activity_analysis"]
    process_edges = tables["process_edges"]
    process_activities = tables["process_activities"]
    delay_cost_estimate = tables["delay_cost_estimate"]

    sla_lookup = dict(zip(sla_metrics["metric"], sla_metrics["value"]))

    print("\n=== Pipeline Validation Summary ===")
    print("Status: PASSED")

    print("\nCore outputs:")
    print(f"- Event log rows: {len(event_log):,}")
    print(f"- Raw cases: {len(raw_cases):,}")
    print(f"- Operational cases: {len(clean_cases):,}")
    print(f"- Variants: {len(variants):,}")
    print(f"- Bottlenecks: {len(bottlenecks):,}")
    print(f"- Recommendations: {len(recommendations):,}")
    print(f"- Root cause signals: {len(root_cause):,}")
    print(f"- SLA breakdown signals: {len(sla_breakdown):,}")
    print(f"- Rework case rows: {len(rework_cases):,}")
    print(f"- Rework activities: {len(rework_activities):,}")
    print(f"- Process edges: {len(process_edges):,}")
    print(f"- Process activities: {len(process_activities):,}")
    print(f"- Delay cost drivers: {len(delay_cost_estimate):,}")

    print("\nOperational KPI checks:")
    print(f"- Raw median cycle time: {raw_cases['cycle_time_days'].median():.2f} days")
    print(
        f"- Operational median cycle time: "
        f"{clean_cases['cycle_time_days'].median():.2f} days"
    )
    print(
        f"- Operational max cycle time: "
        f"{clean_cases['cycle_time_days'].max():.2f} days"
    )

    print("\nSLA checks:")
    print(
        f"- Analytical SLA threshold: "
        f"{float(sla_lookup['analytical_sla_threshold_days']):.0f} days"
    )
    print(f"- SLA compliance rate: {float(sla_lookup['sla_compliance_rate_pct']):.2f}%")
    print(f"- SLA breach rate: {float(sla_lookup['sla_breach_rate_pct']):.2f}%")

    print("\nRework checks:")
    print(f"- Rework cases: {int(rework_cases['has_rework'].sum()):,}")
    print(f"- Rework case share: {rework_cases['has_rework'].mean() * 100:.2f}%")
    print(f"- Top rework activity: {rework_activities.iloc[0]['activity']}")

    print("\nProcess Explorer checks:")
    print(f"- Process edges: {len(process_edges):,}")
    print(f"- Activities: {len(process_activities):,}")
    print(f"- Top process flow: {process_edges.iloc[0]['transition']}")
    print(f"- Top activity: {process_activities.iloc[0]['activity']}")

    print("\nDelay Cost checks:")
    print(
        f"- Assumed cost per waiting day: "
        f"{delay_cost_estimate['assumed_cost_per_waiting_day'].iloc[0]:,.0f} "
        f"cost units"
    )
    print(
        f"- Estimated total delay cost: "
        f"{delay_cost_estimate['estimated_delay_cost'].sum():,.2f} cost units"
    )
    print(f"- Top delay cost driver: {delay_cost_estimate.iloc[0]['transition']}")

    print("\nTop signals:")
    print(f"- Top variant: {variants.iloc[0]['variant_name']}")
    print(f"- Top bottleneck: {bottlenecks.iloc[0]['transition']}")
    print(f"- Top recommendation: {recommendations.iloc[0]['focus_area']}")
    print(f"- Top delay cost driver: {delay_cost_estimate.iloc[0]['transition']}")
    print(
        f"- Top root cause signal: "
        f"{root_cause.iloc[0]['dimension']} = {root_cause.iloc[0]['dimension_value']}"
    )


def main() -> None:
    errors = run_validation()

    if errors:
        print("\n=== Pipeline Validation Summary ===")
        print("Status: FAILED")
        print("\nErrors:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    tables, _ = load_all_available_tables()
    print_success_summary(tables)


if __name__ == "__main__":
    main()