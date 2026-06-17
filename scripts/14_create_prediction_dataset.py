from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "prediction_dataset.csv"

CASE_TIMES_PATH = PROCESSED_DIR / "case_cycle_times_clean.parquet"
EVENT_LOG_PATH = PROCESSED_DIR / "event_log.parquet"
REWORK_CASE_ANALYSIS_PATH = PROCESSED_DIR / "rework_case_analysis.parquet"
SLA_METRICS_PATH = PROCESSED_DIR / "sla_metrics.parquet"

SLA_THRESHOLD_DAYS = 120


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {column.lower(): column for column in df.columns}

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def main() -> None:
    if not CASE_TIMES_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {CASE_TIMES_PATH}")

    case_df = pd.read_parquet(CASE_TIMES_PATH)

    case_id_col = find_column(
        case_df,
        [
            "case_id",
            "case:concept:name",
            "case_concept_name",
            "Case ID",
            "case",
        ],
    )

    cycle_time_col = find_column(
        case_df,
        [
            "cycle_time_days",
            "case_cycle_time_days",
            "duration_days",
            "throughput_time_days",
        ],
    )

    if case_id_col is None:
        raise ValueError(
            f"No case ID column found in {CASE_TIMES_PATH}. Columns: {list(case_df.columns)}"
        )

    if cycle_time_col is None:
        raise ValueError(
            f"No cycle time column found in {CASE_TIMES_PATH}. Columns: {list(case_df.columns)}"
        )

    prediction_df = case_df[[case_id_col, cycle_time_col]].copy()
    prediction_df = prediction_df.rename(
        columns={
            case_id_col: "case_id",
            cycle_time_col: "cycle_time_days",
        }
    )

    prediction_df["sla_breach"] = (
        prediction_df["cycle_time_days"] > SLA_THRESHOLD_DAYS
    ).astype(int)

    prediction_df["event_count"] = 0
    prediction_df["unique_activity_count"] = 0

    if EVENT_LOG_PATH.exists():
        event_log = pd.read_parquet(EVENT_LOG_PATH)

        event_case_col = find_column(
            event_log,
            [
                "case_id",
                "case:concept:name",
                "case_concept_name",
                "Case ID",
                "case",
            ],
        )

        activity_col = find_column(
            event_log,
            [
                "activity",
                "concept:name",
                "event_name",
                "Activity",
            ],
        )

        if event_case_col is not None:
            aggregations = {}

            if activity_col is not None:
                event_features = (
                    event_log.groupby(event_case_col)
                    .agg(
                        event_count=(activity_col, "count"),
                        unique_activity_count=(activity_col, "nunique"),
                    )
                    .reset_index()
                    .rename(columns={event_case_col: "case_id"})
                )
            else:
                event_features = (
                    event_log.groupby(event_case_col)
                    .size()
                    .reset_index(name="event_count")
                    .rename(columns={event_case_col: "case_id"})
                )
                event_features["unique_activity_count"] = 0

            prediction_df = prediction_df.merge(
                event_features,
                on="case_id",
                how="left",
                suffixes=("", "_from_event_log"),
            )

            for column in ["event_count", "unique_activity_count"]:
                fallback_column = f"{column}_from_event_log"

                if fallback_column in prediction_df.columns:
                    prediction_df[column] = prediction_df[fallback_column].fillna(
                        prediction_df[column]
                    )
                    prediction_df = prediction_df.drop(columns=[fallback_column])

    prediction_df["has_rework"] = 0

    if REWORK_CASE_ANALYSIS_PATH.exists():
        rework_df = pd.read_parquet(REWORK_CASE_ANALYSIS_PATH)

        rework_case_col = find_column(
            rework_df,
            [
                "case_id",
                "case:concept:name",
                "case_concept_name",
                "Case ID",
                "case",
            ],
        )

        rework_flag_col = find_column(
            rework_df,
            [
                "has_rework",
                "rework_flag",
                "is_rework",
                "contains_rework",
            ],
        )

        if rework_case_col is not None:
            if rework_flag_col is not None:
                rework_features = rework_df[[rework_case_col, rework_flag_col]].copy()
                rework_features = rework_features.rename(
                    columns={
                        rework_case_col: "case_id",
                        rework_flag_col: "has_rework",
                    }
                )
            else:
                rework_features = rework_df[[rework_case_col]].copy()
                rework_features = rework_features.rename(
                    columns={rework_case_col: "case_id"}
                )
                rework_features["has_rework"] = 1

            prediction_df = prediction_df.drop(columns=["has_rework"])
            prediction_df = prediction_df.merge(
                rework_features,
                on="case_id",
                how="left",
            )
            prediction_df["has_rework"] = prediction_df["has_rework"].fillna(0).astype(int)

    prediction_df["event_count"] = prediction_df["event_count"].fillna(0).astype(int)
    prediction_df["unique_activity_count"] = (
        prediction_df["unique_activity_count"].fillna(0).astype(int)
    )

    prediction_df = prediction_df.dropna(subset=["cycle_time_days"])
    prediction_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Prediction dataset created: {OUTPUT_PATH}")
    print(f"Rows: {len(prediction_df):,}")
    print(f"SLA threshold: {SLA_THRESHOLD_DAYS} days")
    print(f"SLA breach rate: {prediction_df['sla_breach'].mean():.2%}")
    print(f"Columns: {list(prediction_df.columns)}")


if __name__ == "__main__":
    main()