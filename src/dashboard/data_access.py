from pathlib import Path
import json

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ML_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "ml"

EVENT_LOG_PATH = PROCESSED_DIR / "event_log.parquet"
CASE_TIMES_PATH = PROCESSED_DIR / "case_cycle_times.parquet"
OPERATIONAL_CASE_TIMES_PATH = PROCESSED_DIR / "case_cycle_times_clean.parquet"
DATA_QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.csv"

VARIANT_ANALYSIS_PATH = PROCESSED_DIR / "variant_analysis.parquet"
BOTTLENECK_ANALYSIS_PATH = PROCESSED_DIR / "bottleneck_analysis.parquet"
RECOMMENDATIONS_PATH = PROCESSED_DIR / "recommendations.parquet"
ROOT_CAUSE_ANALYSIS_PATH = PROCESSED_DIR / "root_cause_analysis.parquet"

SLA_METRICS_PATH = PROCESSED_DIR / "sla_metrics.parquet"
SLA_BREAKDOWN_PATH = PROCESSED_DIR / "sla_breakdown.parquet"

REWORK_CASE_ANALYSIS_PATH = PROCESSED_DIR / "rework_case_analysis.parquet"
REWORK_ACTIVITY_ANALYSIS_PATH = PROCESSED_DIR / "rework_activity_analysis.parquet"

PROCESS_EDGES_PATH = PROCESSED_DIR / "process_edges.parquet"
PROCESS_ACTIVITIES_PATH = PROCESSED_DIR / "process_activities.parquet"

DELAY_COST_ESTIMATE_PATH = PROCESSED_DIR / "delay_cost_estimate.parquet"

PREDICTION_METRICS_PATH = ML_OUTPUT_DIR / "model_metrics.json"
RISK_PREDICTIONS_PATH = ML_OUTPUT_DIR / "risk_predictions.csv"
FEATURE_IMPORTANCE_PATH = ML_OUTPUT_DIR / "feature_importance.csv"
CONFUSION_MATRIX_PATH = ML_OUTPUT_DIR / "confusion_matrix.csv"

OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS = 365


def validate_required_files() -> None:
    required_files = [
        EVENT_LOG_PATH,
        CASE_TIMES_PATH,
        OPERATIONAL_CASE_TIMES_PATH,
        DATA_QUALITY_REPORT_PATH,
        VARIANT_ANALYSIS_PATH,
        BOTTLENECK_ANALYSIS_PATH,
        RECOMMENDATIONS_PATH,
        ROOT_CAUSE_ANALYSIS_PATH,
        SLA_METRICS_PATH,
        SLA_BREAKDOWN_PATH,
        REWORK_CASE_ANALYSIS_PATH,
        REWORK_ACTIVITY_ANALYSIS_PATH,
        PROCESS_EDGES_PATH,
        PROCESS_ACTIVITIES_PATH,
    ]

    missing_files = [path for path in required_files if not path.exists()]

    if missing_files:
        st.error("Processed data files are missing.")
        st.write("Run these scripts first:")
        st.code(
            """
python scripts/02_convert_xes_to_parquet.py
python scripts/03_calculate_initial_kpis.py
python scripts/04_create_clean_case_table.py
python scripts/05_calculate_variant_analysis.py
python scripts/06_calculate_bottlenecks.py
python scripts/07_generate_recommendations.py
python scripts/08_calculate_root_cause_analysis.py
python scripts/10_calculate_sla_metrics.py
python scripts/11_calculate_rework_detection.py
python scripts/12_calculate_process_explorer.py
            """.strip()
        )
        st.write("Missing files:")
        for path in missing_files:
            st.write(f"- {path}")
        st.stop()


@st.cache_data(show_spinner=False)
def load_event_log() -> pd.DataFrame:
    return pd.read_parquet(EVENT_LOG_PATH)


@st.cache_data(show_spinner=False)
def load_raw_case_times() -> pd.DataFrame:
    return pd.read_parquet(CASE_TIMES_PATH)


@st.cache_data(show_spinner=False)
def load_operational_case_times() -> pd.DataFrame:
    return pd.read_parquet(OPERATIONAL_CASE_TIMES_PATH)


@st.cache_data(show_spinner=False)
def load_data_quality_report() -> pd.DataFrame:
    return pd.read_csv(DATA_QUALITY_REPORT_PATH)


@st.cache_data(show_spinner=False)
def load_variant_analysis() -> pd.DataFrame:
    return pd.read_parquet(VARIANT_ANALYSIS_PATH)


@st.cache_data(show_spinner=False)
def load_bottleneck_analysis() -> pd.DataFrame:
    return pd.read_parquet(BOTTLENECK_ANALYSIS_PATH)


@st.cache_data(show_spinner=False)
def load_recommendations() -> pd.DataFrame:
    return pd.read_parquet(RECOMMENDATIONS_PATH)


@st.cache_data(show_spinner=False)
def load_root_cause_analysis() -> pd.DataFrame:
    return pd.read_parquet(ROOT_CAUSE_ANALYSIS_PATH)


@st.cache_data(show_spinner=False)
def load_sla_metrics() -> pd.DataFrame:
    return pd.read_parquet(SLA_METRICS_PATH)


@st.cache_data(show_spinner=False)
def load_sla_breakdown() -> pd.DataFrame:
    return pd.read_parquet(SLA_BREAKDOWN_PATH)


@st.cache_data(show_spinner=False)
def load_rework_case_analysis() -> pd.DataFrame:
    return pd.read_parquet(REWORK_CASE_ANALYSIS_PATH)


@st.cache_data(show_spinner=False)
def load_rework_activity_analysis() -> pd.DataFrame:
    return pd.read_parquet(REWORK_ACTIVITY_ANALYSIS_PATH)


@st.cache_data(show_spinner=False)
def load_process_edges() -> pd.DataFrame:
    return pd.read_parquet(PROCESS_EDGES_PATH)


@st.cache_data(show_spinner=False)
def load_process_activities() -> pd.DataFrame:
    return pd.read_parquet(PROCESS_ACTIVITIES_PATH)


@st.cache_data(show_spinner=False)
def load_delay_cost_estimate() -> pd.DataFrame:
    if not DELAY_COST_ESTIMATE_PATH.exists():
        return pd.DataFrame()

    return pd.read_parquet(DELAY_COST_ESTIMATE_PATH)


@st.cache_data(show_spinner=False)
def load_prediction_metrics() -> dict | None:
    if not PREDICTION_METRICS_PATH.exists():
        return None

    with open(PREDICTION_METRICS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data(show_spinner=False)
def load_risk_predictions() -> pd.DataFrame:
    if not RISK_PREDICTIONS_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(RISK_PREDICTIONS_PATH)


@st.cache_data(show_spinner=False)
def load_feature_importance() -> pd.DataFrame:
    if not FEATURE_IMPORTANCE_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(FEATURE_IMPORTANCE_PATH)


@st.cache_data(show_spinner=False)
def load_confusion_matrix() -> pd.DataFrame:
    if not CONFUSION_MATRIX_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(CONFUSION_MATRIX_PATH, index_col=0)