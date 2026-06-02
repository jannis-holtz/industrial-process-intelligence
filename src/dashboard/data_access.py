from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"
CASE_TIMES_PATH = PROJECT_ROOT / "data" / "processed" / "case_cycle_times.parquet"
OPERATIONAL_CASE_TIMES_PATH = (
    PROJECT_ROOT / "data" / "processed" / "case_cycle_times_clean.parquet"
)
DATA_QUALITY_REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_report.csv"

OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS = 365


def validate_required_files() -> None:
    required_files = [
        EVENT_LOG_PATH,
        CASE_TIMES_PATH,
        OPERATIONAL_CASE_TIMES_PATH,
        DATA_QUALITY_REPORT_PATH,
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
            """.strip()
        )
        for path in missing_files:
            st.write(f"- {path}")
        st.stop()


@st.cache_data
def load_event_log() -> pd.DataFrame:
    return pd.read_parquet(EVENT_LOG_PATH)


@st.cache_data
def load_raw_case_times() -> pd.DataFrame:
    return pd.read_parquet(CASE_TIMES_PATH)


@st.cache_data
def load_operational_case_times() -> pd.DataFrame:
    return pd.read_parquet(OPERATIONAL_CASE_TIMES_PATH)


@st.cache_data
def load_data_quality_report() -> pd.DataFrame:
    return pd.read_csv(DATA_QUALITY_REPORT_PATH)