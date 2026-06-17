import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def render_root_cause_analysis_view(root_cause_analysis: pd.DataFrame) -> None:
    st.markdown("## Root Cause Analysis")

    slow_case_threshold = root_cause_analysis["slow_case_threshold_days"].iloc[0]

    vendor_signals = root_cause_analysis[
        root_cause_analysis["dimension"] == "vendor"
    ].copy()

    top_vendor_signal = vendor_signals.sort_values(
        "impact_score",
        ascending=False,
    ).iloc[0]

    high_lift_signals = root_cause_analysis[
        root_cause_analysis["slow_case_lift"] >= 2
    ]

    with module_container(
        title="Decision Focus",
        subtitle="Identify dimensions that are overrepresented among slow-running cases.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                Slow cases are defined as cases with cycle time above
                <strong>{slow_case_threshold:.2f} days</strong>.
                The strongest vendor-level signal is
                <strong>{top_vendor_signal["dimension_value"]}</strong>,
                with <strong>{top_vendor_signal["slow_case_share_pct"]:.2f}%</strong>
                slow cases and a slow-case lift of
                <strong>{top_vendor_signal["slow_case_lift"]:.2f}x</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card(
            icon="🔎",
            label="Root Cause Signals",
            value=f"{len(root_cause_analysis):,}",
            delta="after minimum case threshold",
            positive=True,
        )

    with col2:
        render_kpi_card(
            icon="⏱️",
            label="Slow Case Threshold",
            value=f"{slow_case_threshold:.1f} d",
            delta="P90 operational cycle time",
            positive=False,
        )

    with col3:
        render_kpi_card(
            icon="⚠️",
            label="High Lift Signals",
            value=f"{len(high_lift_signals):,}",
            delta="slow-case lift >= 2x",
            positive=False,
        )

    st.write("")

    top_signals = root_cause_analysis[
        [
            "root_cause_rank",
            "dimension",
            "dimension_value",
            "cases",
            "slow_cases",
            "slow_case_share_pct",
            "slow_case_contribution_pct",
            "slow_case_lift",
            "median_cycle_time_days",
            "p90_cycle_time_days",
            "impact_score",
        ]
    ].head(20)

    with module_container(
        title="Top Root Cause Signals",
        subtitle="Signals ranked by slow-case contribution and overrepresentation among slow cases.",
        eyebrow="Root Cause Ranking",
    ):
        st.dataframe(
            styled_dataframe(top_signals),
            use_container_width=True,
            hide_index=True,
        )

    vendor_table = (
        vendor_signals[
            [
                "root_cause_rank",
                "dimension_value",
                "cases",
                "slow_cases",
                "slow_case_share_pct",
                "slow_case_lift",
                "median_cycle_time_days",
                "p90_cycle_time_days",
                "impact_score",
            ]
        ]
        .sort_values("impact_score", ascending=False)
        .head(20)
    )

    with module_container(
        title="Vendor-Level Slow Case Signals",
        subtitle="Vendors with elevated slow-case share and operational impact.",
        eyebrow="Vendor Analysis",
    ):
        st.dataframe(
            styled_dataframe(vendor_table),
            use_container_width=True,
            hide_index=True,
        )

    with module_container(
        title="Interpretation",
        subtitle="How to read these signals.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            """
            Root Cause Analysis highlights dimensions that are overrepresented among slow cases.
            High-volume dimensions such as company or document type can explain a large share of slow cases,
            but vendor-level signals are often more actionable because they reveal specific supplier patterns
            with elevated slow-case lift.
            """
        )