import streamlit as st

from src.dashboard.components import module_container, render_platform_layers


def render_process_layers_view() -> None:
    st.markdown("## Solution Architecture")

    left, right = st.columns([1.3, 1])

    with left:
        with module_container(
            title="Problem → Data → KPI → Decision → Recommendation",
            subtitle="Each layer transforms raw operational traces into more actionable process intelligence.",
            eyebrow="Architecture Logic",
        ):
            st.markdown(
                """
                <div class="hero-card">
                    <h2>Decision-support architecture</h2>
                    <p>
                        The platform is structured as a decision-support system.
                        Each layer increases the business usefulness of the original event log.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with module_container(
            title="Target Architecture",
            subtitle="End-to-end flow from raw event logs to dashboard-based decision support.",
            eyebrow="Pipeline",
        ):
            st.code(
                """
Raw XES Event Log
↓
PM4Py Import
↓
Standardized Event Log
↓
Parquet Analytical Layer
↓
Case-Level KPIs
↓
Operational KPI View
↓
Variant & Bottleneck Analysis
↓
Recommendations
↓
Dashboard
                """.strip()
            )

    with right:
        with module_container(
            title="Platform Layers",
            subtitle="Layered structure from raw data to process decision support.",
            eyebrow="Solution Layers",
        ):
            render_platform_layers()