from pathlib import Path
import sys

import streamlit as st
import streamlit.components.v1 as components


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.dashboard.components import render_header
from src.dashboard.data_access import (
    load_bottleneck_analysis,
    load_confusion_matrix,
    load_data_quality_report,
    load_delay_cost_estimate,
    load_event_log,
    load_feature_importance,
    load_operational_case_times,
    load_prediction_metrics,
    load_process_activities,
    load_process_edges,
    load_raw_case_times,
    load_recommendations,
    load_rework_activity_analysis,
    load_rework_case_analysis,
    load_risk_predictions,
    load_root_cause_analysis,
    load_sla_breakdown,
    load_sla_metrics,
    load_variant_analysis,
    validate_required_files,
)
from src.dashboard.views import (
    render_bottleneck_analysis_view,
    render_data_quality_view,
    render_executive_overview,
    render_prediction_risk_view,
    render_process_explorer_view,
    render_process_layers_view,
    render_recommendations_view,
    render_rework_detection_view,
    render_root_cause_analysis_view,
    render_sla_compliance_view,
    render_variant_intelligence_view,
)


st.set_page_config(
    page_title="Industrial Process Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


NAVIGATION_ITEMS = [
    "🏠 Executive Overview",
    "🗺️ Process Explorer",
    "🛡️ Data Quality",
    "🧭 Variant Intelligence",
    "⏱️ Bottleneck Analysis",
    "📍 SLA Compliance",
    "🔁 Rework Detection",
    "🔎 Root Cause",
    "🎯 Recommendations",
    "⚠️ Prediction & Risk",
    "🧱 Platform Layers",
]


def scroll_to_top() -> None:
    components.html(
        """
        <script>
            const scrollToTop = () => {
                const doc = window.parent.document;
                const main = doc.querySelector('[data-testid="stAppViewContainer"]');

                if (main) {
                    main.scrollTo({ top: 0, behavior: "smooth" });
                }

                window.parent.scrollTo({ top: 0, behavior: "smooth" });
            };

            setTimeout(scrollToTop, 100);
        </script>
        """,
        height=0,
    )


def get_view_from_query_params() -> None:
    view = st.query_params.get("view")

    if view and view in NAVIGATION_ITEMS:
        st.session_state.selected_view = view


def initialize_navigation_state() -> None:
    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "🏠 Executive Overview"

    get_view_from_query_params()


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

        st.markdown(
            '<div class="sidebar-section-label">Navigation</div>',
            unsafe_allow_html=True,
        )

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
                st.query_params["view"] = item
                st.rerun()

        st.markdown("---")

        st.markdown(
            '<div class="sidebar-section-label">System Status</div>',
            unsafe_allow_html=True,
        )

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


def load_dashboard_data() -> dict:
    return {
        "event_log": load_event_log(),
        "raw_cases": load_raw_case_times(),
        "operational_cases": load_operational_case_times(),
        "data_quality_report": load_data_quality_report(),
        "variant_analysis": load_variant_analysis(),
        "bottleneck_analysis": load_bottleneck_analysis(),
        "delay_cost_estimate": load_delay_cost_estimate(),
        "recommendations": load_recommendations(),
        "root_cause_analysis": load_root_cause_analysis(),
        "process_edges": load_process_edges(),
        "process_activities": load_process_activities(),
        "sla_metrics": load_sla_metrics(),
        "sla_breakdown": load_sla_breakdown(),
        "rework_case_analysis": load_rework_case_analysis(),
        "rework_activity_analysis": load_rework_activity_analysis(),
        "prediction_metrics": load_prediction_metrics(),
        "risk_predictions": load_risk_predictions(),
        "feature_importance": load_feature_importance(),
        "confusion_matrix": load_confusion_matrix(),
    }


def render_selected_view(selected_view: str, data: dict) -> None:
    if selected_view == "🏠 Executive Overview":
        render_executive_overview(
            event_log=data["event_log"],
            raw_cases=data["raw_cases"],
            operational_cases=data["operational_cases"],
            data_quality_report=data["data_quality_report"],
            bottleneck_analysis=data["bottleneck_analysis"],
            sla_metrics=data["sla_metrics"],
            rework_case_analysis=data["rework_case_analysis"],
            rework_activity_analysis=data["rework_activity_analysis"],
            recommendations=data["recommendations"],
            delay_cost_estimate=data["delay_cost_estimate"],
        )
    elif selected_view == "🗺️ Process Explorer":
        render_process_explorer_view(
            data["process_edges"],
            data["process_activities"],
        )

    elif selected_view == "🛡️ Data Quality":
        render_data_quality_view(
            data["raw_cases"],
            data["operational_cases"],
            data["data_quality_report"],
        )

    elif selected_view == "🧭 Variant Intelligence":
        render_variant_intelligence_view(data["variant_analysis"])

    elif selected_view == "⏱️ Bottleneck Analysis":
        render_bottleneck_analysis_view(
            data["bottleneck_analysis"],
            data["delay_cost_estimate"],
        )

    elif selected_view == "📍 SLA Compliance":
        render_sla_compliance_view(
            sla_metrics=data["sla_metrics"],
            sla_breakdown=data["sla_breakdown"],
        )

    elif selected_view == "🔁 Rework Detection":
        render_rework_detection_view(
            rework_case_analysis=data["rework_case_analysis"],
            rework_activity_analysis=data["rework_activity_analysis"],
        )

    elif selected_view == "🔎 Root Cause":
        render_root_cause_analysis_view(data["root_cause_analysis"])

    elif selected_view == "🎯 Recommendations":
        render_recommendations_view(
            recommendations=data["recommendations"],
            delay_cost_estimate=data["delay_cost_estimate"],
        )

    elif selected_view == "⚠️ Prediction & Risk":
        render_prediction_risk_view(
            prediction_metrics=data["prediction_metrics"],
            risk_predictions=data["risk_predictions"],
            feature_importance=data["feature_importance"],
            confusion_matrix=data["confusion_matrix"],
        )

    elif selected_view == "🧱 Platform Layers":
        render_process_layers_view()

    else:
        st.warning("Unknown view selected. Returning to Executive Overview.")
        st.session_state.selected_view = "🏠 Executive Overview"
        st.query_params["view"] = "🏠 Executive Overview"
        st.rerun()


def main() -> None:
    validate_required_files()

    selected_view = render_sidebar()

    scroll_to_top()
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    render_header()

    with st.spinner("Loading Process Intelligence dashboard data..."):
        data = load_dashboard_data()

    render_selected_view(selected_view, data)


if __name__ == "__main__":
    main()