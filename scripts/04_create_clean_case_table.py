from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times.parquet"
CLEAN_CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
DATA_QUALITY_REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_report.csv"

MAX_REASONABLE_CYCLE_TIME_DAYS = 365


def load_case_times() -> pd.DataFrame:
    if not CASE_TIMES_PATH.exists():
        raise FileNotFoundError(
            f"Case cycle time table not found: {CASE_TIMES_PATH}\n"
            "Run scripts/03_calculate_initial_kpis.py first."
        )

    return pd.read_parquet(CASE_TIMES_PATH)


def create_clean_case_table(case_times: pd.DataFrame) -> pd.DataFrame:
    clean_case_times = case_times[
        case_times["cycle_time_days"] <= MAX_REASONABLE_CYCLE_TIME_DAYS
    ].copy()

    return clean_case_times.reset_index(drop=True)


def create_data_quality_report(case_times: pd.DataFrame) -> pd.DataFrame:
    total_cases = len(case_times)

    above_threshold = case_times[
        case_times["cycle_time_days"] > MAX_REASONABLE_CYCLE_TIME_DAYS
    ]

    negative_cycle_times = case_times[
        case_times["cycle_time_days"] < 0
    ]

    report = pd.DataFrame(
        [
            {
                "check": "cycle_time_above_365_days",
                "affected_cases": len(above_threshold),
                "share_of_cases_pct": round(len(above_threshold) / total_cases * 100, 4),
                "severity": "medium",
                "business_interpretation": (
                    "Cases above 365 days are excluded from operational KPI reporting "
                    "but retained for exception and data quality analysis."
                ),
            },
            {
                "check": "negative_cycle_time",
                "affected_cases": len(negative_cycle_times),
                "share_of_cases_pct": round(len(negative_cycle_times) / total_cases * 100, 4),
                "severity": "high",
                "business_interpretation": (
                    "Negative cycle times would indicate incorrect timestamp ordering "
                    "or corrupted event data."
                ),
            },
        ]
    )

    return report


def print_comparison(raw_case_times: pd.DataFrame, clean_case_times: pd.DataFrame) -> None:
    excluded_cases = len(raw_case_times) - len(clean_case_times)

    print("\n=== Raw vs Clean KPI Comparison ===")
    print(f"Raw cases: {len(raw_case_times):,}")
    print(f"Clean cases: {len(clean_case_times):,}")
    print(f"Excluded cases: {excluded_cases:,}")
    print(f"Excluded share: {excluded_cases / len(raw_case_times) * 100:.4f}%")

    print("\n=== Raw Cycle Time ===")
    print(f"Average: {raw_case_times['cycle_time_days'].mean():.2f} days")
    print(f"Median: {raw_case_times['cycle_time_days'].median():.2f} days")
    print(f"P90: {raw_case_times['cycle_time_days'].quantile(0.90):.2f} days")
    print(f"Max: {raw_case_times['cycle_time_days'].max():.2f} days")

    print("\n=== Clean Business Cycle Time ===")
    print(f"Average: {clean_case_times['cycle_time_days'].mean():.2f} days")
    print(f"Median: {clean_case_times['cycle_time_days'].median():.2f} days")
    print(f"P75: {clean_case_times['cycle_time_days'].quantile(0.75):.2f} days")
    print(f"P90: {clean_case_times['cycle_time_days'].quantile(0.90):.2f} days")
    print(f"P95: {clean_case_times['cycle_time_days'].quantile(0.95):.2f} days")
    print(f"Max: {clean_case_times['cycle_time_days'].max():.2f} days")


def main() -> None:
    case_times = load_case_times()

    clean_case_times = create_clean_case_table(case_times)
    data_quality_report = create_data_quality_report(case_times)

    clean_case_times.to_parquet(CLEAN_CASE_TIMES_PATH, index=False)
    data_quality_report.to_csv(DATA_QUALITY_REPORT_PATH, index=False)

    print_comparison(case_times, clean_case_times)

    print(f"\nSaved clean case table to: {CLEAN_CASE_TIMES_PATH}")
    print(f"Saved data quality report to: {DATA_QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()