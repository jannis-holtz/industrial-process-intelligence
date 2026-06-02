from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.dashboard.components import render_header
from src.dashboard.data_access import (
    load_data_quality_report,
    load_event_log,
    load_operational_case_times,
    load_raw_case_times,
    validate_required_files,
)
from src.dashboard.views import (
    render_bottleneck_placeholder,
    render_data_quality_view,
    render_executive_overview,
    render_prediction_placeholder,
    render_process_layers_view,
    render_recommendations_placeholder,
    render_root_cause_placeholder,
    render_variant_placeholder,
)


st.set_page_config(
    page_title="Industrial Process Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


NAVIGATION_ITEMS = [
    "🏠 Executive Overview",
    "🛡️ Data Quality",
    "🧭 Variant Intelligence",
    "⏱️ Bottleneck Analysis",
    "🔎 Root Cause",
    "🎯 Recommendations",
    "⚠️ Prediction & Risk",
    "🧱 Platform Layers",
]


def initialize_navigation_state() -> None:
    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "🏠 Executive Overview"


def render_sidebar() -> str:
    initialize_navigation_state()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-logo">
                <div class="sidebar-logo-mark">IPI</div>
                <div>
                    <div class="sidebar-title">Industrial Process Intelligence</div>
                    <div class="sidebar-subtitle">Process Intelligence Platform</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)

        for item in NAVIGATION_ITEMS:
            is_active = st.session_state.selected_view == item
            button_type = "primary" if is_active else "secondary"

            if st.button(
                item,
                key=f"nav_{item}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state.selected_view = item
                st.rerun()

        st.markdown("---")

        st.markdown('<div class="sidebar-section-label">System Status</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="sidebar-status-card">
                <div class="status-dot"></div>
                <div>
                    <div class="status-title-small">All Systems Operational</div>
                    <div class="status-text-small">Local analysis run</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return st.session_state.selected_view


def main() -> None:
    validate_required_files()

    selected_view = render_sidebar()
    render_header()

    event_log = load_event_log()
    raw_cases = load_raw_case_times()
    operational_cases = load_operational_case_times()
    data_quality_report = load_data_quality_report()

    if selected_view == "🏠 Executive Overview":
        render_executive_overview(
            event_log,
            raw_cases,
            operational_cases,
            data_quality_report,
        )

    elif selected_view == "🛡️ Data Quality":
        render_data_quality_view(
            raw_cases,
            operational_cases,
            data_quality_report,
        )

    elif selected_view == "🧭 Variant Intelligence":
        render_variant_placeholder(operational_cases)

    elif selected_view == "⏱️ Bottleneck Analysis":
        render_bottleneck_placeholder()

    elif selected_view == "🔎 Root Cause":
        render_root_cause_placeholder(operational_cases)

    elif selected_view == "🎯 Recommendations":
        render_recommendations_placeholder()

    elif selected_view == "⚠️ Prediction & Risk":
        render_prediction_placeholder()

    elif selected_view == "🧱 Platform Layers":
        render_process_layers_view()


if __name__ == "__main__":
    main()