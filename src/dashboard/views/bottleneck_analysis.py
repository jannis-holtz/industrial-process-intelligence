import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def render_bottleneck_analysis_view(
    bottleneck_analysis: pd.DataFrame,
    delay_cost_estimate: pd.DataFrame | None = None,
) -> None:
    st.markdown("## Bottleneck Analysis")

    top_bottleneck = bottleneck_analysis.iloc[0]

    has_delay_cost = (
        delay_cost_estimate is not None
        and not delay_cost_estimate.empty
        and "estimated_delay_cost" in delay_cost_estimate.columns
    )

    if has_delay_cost:
        top_cost_driver = delay_cost_estimate.iloc[0]
        total_estimated_delay_cost = delay_cost_estimate[
            "estimated_delay_cost"
        ].sum()
        assumed_cost_per_waiting_day = delay_cost_estimate[
            "assumed_cost_per_waiting_day"
        ].iloc[0]
    else:
        top_cost_driver = None
        total_estimated_delay_cost = None
        assumed_cost_per_waiting_day = None

    with module_container(
        title="Decision Focus",
        subtitle="Identify where operational waiting time and estimated delay impact accumulate.",
        eyebrow="Bottleneck Intelligence",
    ):
        if has_delay_cost:
            st.markdown(
                f"""
                <div class="decision-box">
                    The strongest operational bottleneck is
                    <strong>{top_bottleneck["transition"]}</strong>
                    with a median waiting time of
                    <strong>{top_bottleneck["median_waiting_time_days"]:.2f} days</strong>.
                    The same transition is also the largest estimated delay-cost driver,
                    contributing <strong>{top_cost_driver["share_of_estimated_delay_cost_pct"]:.2f}%</strong>
                    of total estimated delay cost.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="decision-box">
                    The strongest operational bottleneck is
                    <strong>{top_bottleneck["transition"]}</strong>
                    with a median waiting time of
                    <strong>{top_bottleneck["median_waiting_time_days"]:.2f} days</strong>.
                </div>
                """,
                unsafe_allow_html=True,
            )

    if has_delay_cost:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="⏱️",
                label="Top Median Wait",
                value=f"{top_bottleneck['median_waiting_time_days']:.1f} days",
                delta=top_bottleneck["transition"],
                positive=False,
            )

        with col2:
            render_kpi_card(
                icon="📊",
                label="Waiting-Time Share",
                value=f"{top_bottleneck['share_of_total_waiting_time_pct']:.1f}%",
                delta="top bottleneck contribution",
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="💰",
                label="Estimated Delay Cost",
                value=f"{total_estimated_delay_cost / 1_000_000:,.1f}M",
                delta="cost units, assumption-based",
                positive=False,
            )

        with col4:
            render_kpi_card(
                icon="⚙️",
                label="Cost Assumption",
                value=f"{assumed_cost_per_waiting_day:,.0f}",
                delta="cost units per waiting day",
                positive=True,
            )

    st.write("")

    if has_delay_cost:
        left, right = st.columns([1, 1])

        with left:
            with module_container(
                title="Top Operational Bottleneck",
                subtitle="Transition with the highest bottleneck impact score.",
                eyebrow="Waiting-Time Driver",
            ):
                st.markdown(
                    f"""
                    <div class="hero-card">
                        <h2>{top_bottleneck["transition"]}</h2>
                        <p>
                            Median wait:
                            <strong>{top_bottleneck["median_waiting_time_days"]:.2f} days</strong>,
                            P90 wait:
                            <strong>{top_bottleneck["p90_waiting_time_days"]:.2f} days</strong>.
                        </p>
                        <p>
                            Waiting-time contribution:
                            <strong>{top_bottleneck["share_of_total_waiting_time_pct"]:.2f}%</strong>.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with right:
            with module_container(
                title="Top Estimated Delay-Cost Driver",
                subtitle="Assumption-based business impact using waiting time multiplied by cost units.",
                eyebrow="Business Impact",
            ):
                st.markdown(
                    f"""
                    <div class="hero-card">
                        <h2>{top_cost_driver["transition"]}</h2>
                        <p>
                            Estimated delay cost:
                            <strong>{top_cost_driver["estimated_delay_cost"]:,.0f} cost units</strong>.
                        </p>
                        <p>
                            Cost share:
                            <strong>{top_cost_driver["share_of_estimated_delay_cost_pct"]:.2f}%</strong>,
                            estimated cost per case:
                            <strong>{top_cost_driver["estimated_cost_per_case"]:,.2f}</strong>.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

        tab1, tab2, tab3 = st.tabs(
            [
                "Bottlenecks by Waiting Time",
                "Estimated Delay Cost",
                "Raw Bottleneck Table",
            ]
        )

        with tab1:
            bottleneck_display = (
                bottleneck_analysis[
                    [
                        "bottleneck_rank",
                        "transition",
                        "transition_count",
                        "median_waiting_time_days",
                        "p90_waiting_time_days",
                        "total_waiting_time_days",
                        "share_of_total_waiting_time_pct",
                        "impact_score",
                        "dominant_item_category",
                    ]
                ]
                .head(15)
                .rename(
                    columns={
                        "bottleneck_rank": "Rank",
                        "transition": "Transition",
                        "transition_count": "Transitions",
                        "median_waiting_time_days": "Median Wait Days",
                        "p90_waiting_time_days": "P90 Wait Days",
                        "total_waiting_time_days": "Total Wait Days",
                        "share_of_total_waiting_time_pct": "Waiting-Time Share %",
                        "impact_score": "Impact Score",
                        "dominant_item_category": "Dominant Item Category",
                    }
                )
            )

            with module_container(
                title="Top Bottlenecks by Waiting-Time Impact",
                subtitle="Transitions ranked by operational bottleneck impact.",
                eyebrow="Operational Delay",
            ):
                st.dataframe(
                    styled_dataframe(bottleneck_display),
                    use_container_width=True,
                    hide_index=True,
                )

        with tab2:
            delay_cost_display = (
                delay_cost_estimate[
                    [
                        "delay_cost_rank",
                        "transition",
                        "transition_count",
                        "median_waiting_time_days",
                        "total_waiting_time_days",
                        "estimated_delay_cost",
                        "estimated_cost_per_case",
                        "share_of_estimated_delay_cost_pct",
                        "dominant_item_category",
                    ]
                ]
                .head(15)
                .rename(
                    columns={
                        "delay_cost_rank": "Rank",
                        "transition": "Transition",
                        "transition_count": "Transitions",
                        "median_waiting_time_days": "Median Wait Days",
                        "total_waiting_time_days": "Total Wait Days",
                        "estimated_delay_cost": "Estimated Delay Cost",
                        "estimated_cost_per_case": "Estimated Cost per Case",
                        "share_of_estimated_delay_cost_pct": "Cost Share %",
                        "dominant_item_category": "Dominant Item Category",
                    }
                )
            )

            with module_container(
                title="Estimated Delay-Cost Drivers",
                subtitle="Assumption-based ranking of process transitions by estimated business impact.",
                eyebrow="Cost Impact",
            ):
                st.info(
                    "Cost values are not actual financials. They use a transparent assumption: "
                    f"{assumed_cost_per_waiting_day:,.0f} cost units per waiting day."
                )

                st.dataframe(
                    styled_dataframe(delay_cost_display),
                    use_container_width=True,
                    hide_index=True,
                )

        with tab3:
            with module_container(
                title="Raw Bottleneck Analysis",
                subtitle="Full bottleneck output for technical inspection.",
                eyebrow="Detailed Table",
            ):
                st.dataframe(
                    styled_dataframe(bottleneck_analysis),
                    use_container_width=True,
                    hide_index=True,
                )

    with module_container(
        title="Interpretation",
        subtitle="How to read the bottleneck and delay-cost analysis.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            """
            Bottleneck Analysis identifies where operational waiting time accumulates.
            Delay Cost Estimate adds an assumption-based business impact layer by multiplying
            waiting time with a fixed cost-per-waiting-day assumption.

            The key signal is especially strong when the same transition appears as top bottleneck,
            top recommendation focus area, and top estimated delay-cost driver.
            """
        )