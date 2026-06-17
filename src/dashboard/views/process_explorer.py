import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def get_non_self_loop_edges(process_edges: pd.DataFrame) -> pd.DataFrame:
    return process_edges[
        process_edges["source_activity"] != process_edges["target_activity"]
    ].copy()


def render_empty_process_explorer_state() -> None:
    st.markdown("## Process Explorer")

    with module_container(
        title="Process Explorer not available",
        subtitle="The required process flow output is missing or empty.",
        eyebrow="Missing Data",
    ):
        st.warning(
            "No process explorer data is available. "
            "Run `python scripts/12_calculate_process_explorer.py` first."
        )


def render_process_explorer_view(
    process_edges: pd.DataFrame,
    process_activities: pd.DataFrame,
) -> None:
    st.markdown("## Process Explorer")

    if process_edges.empty or process_activities.empty:
        render_empty_process_explorer_state()
        return

    non_self_loop_edges = get_non_self_loop_edges(process_edges)

    if non_self_loop_edges.empty:
        st.warning("No non-self-loop process flows available.")
        return

    top_volume_edge = (
        non_self_loop_edges.sort_values("transition_count", ascending=False)
        .iloc[0]
    )

    top_wait_edge = (
        non_self_loop_edges.sort_values("share_of_waiting_time_pct", ascending=False)
        .iloc[0]
    )

    top_activity = process_activities.iloc[0]

    with module_container(
        title="Decision Focus",
        subtitle="Understand the actually observed process flow and where operational delay accumulates.",
        eyebrow="Process Flow",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                The most frequent relevant process flow is
                <strong>{top_volume_edge["transition"]}</strong>
                with <strong>{int(top_volume_edge["transition_count"]):,}</strong> observed transitions.
                The largest waiting-time contributor is
                <strong>{top_wait_edge["transition"]}</strong>,
                accounting for <strong>{top_wait_edge["share_of_waiting_time_pct"]:.2f}%</strong>
                of total observed waiting time.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            icon="🗺️",
            label="Process Flows",
            value=f"{len(process_edges):,}",
            delta="relevant edges",
            positive=True,
        )

    with col2:
        render_kpi_card(
            icon="🔁",
            label="Activities",
            value=f"{len(process_activities):,}",
            delta="activity types",
            positive=True,
        )

    with col3:
        render_kpi_card(
            icon="⏱️",
            label="Top Wait Share",
            value=f"{top_wait_edge['share_of_waiting_time_pct']:.1f}%",
            delta="waiting-time contribution",
            positive=False,
        )

    with col4:
        render_kpi_card(
            icon="📌",
            label="Top Activity Coverage",
            value=f"{top_activity['share_of_cases_pct']:.1f}%",
            delta=str(top_activity["activity"]),
            positive=True,
        )

    st.write("")

    left, right = st.columns([1, 1])

    with left:
        with module_container(
            title="Most Frequent Process Flow",
            subtitle="The most common non-self-loop transition in the operational process.",
            eyebrow="Volume Driver",
        ):
            st.markdown(
                f"""
                <div class="hero-card">
                    <h2>{top_volume_edge["transition"]}</h2>
                    <p>
                        <strong>{int(top_volume_edge["transition_count"]):,}</strong> transitions
                        across <strong>{int(top_volume_edge["case_count"]):,}</strong> cases.
                    </p>
                    <p>
                        Median waiting time:
                        <strong>{top_volume_edge["median_waiting_time_days"]:.2f} days</strong>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        with module_container(
            title="Largest Waiting-Time Contributor",
            subtitle="The process flow that contributes the largest share of total waiting time.",
            eyebrow="Delay Driver",
        ):
            st.markdown(
                f"""
                <div class="hero-card">
                    <h2>{top_wait_edge["transition"]}</h2>
                    <p>
                        Accounts for
                        <strong>{top_wait_edge["share_of_waiting_time_pct"]:.2f}%</strong>
                        of total observed waiting time.
                    </p>
                    <p>
                        Median wait:
                        <strong>{top_wait_edge["median_waiting_time_days"]:.2f} days</strong>,
                        P90 wait:
                        <strong>{top_wait_edge["p90_waiting_time_days"]:.2f} days</strong>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    tab1, tab2, tab3 = st.tabs(
        [
            "Top Flows by Volume",
            "Top Flows by Waiting Time",
            "Top Activities",
        ]
    )

    with tab1:
        top_edges_by_volume = (
            non_self_loop_edges[
                [
                    "edge_rank",
                    "transition",
                    "transition_count",
                    "case_count",
                    "share_of_transitions_pct",
                    "median_waiting_time_days",
                    "p90_waiting_time_days",
                ]
            ]
            .sort_values("transition_count", ascending=False)
            .head(15)
            .rename(
                columns={
                    "edge_rank": "Rank",
                    "transition": "Process Flow",
                    "transition_count": "Transitions",
                    "case_count": "Cases",
                    "share_of_transitions_pct": "Share of Transitions %",
                    "median_waiting_time_days": "Median Wait Days",
                    "p90_waiting_time_days": "P90 Wait Days",
                }
            )
        )

        with module_container(
            title="Top Process Flows by Volume",
            subtitle="Most common process transitions, excluding technical self-loops for readability.",
            eyebrow="Process Volume",
        ):
            st.dataframe(
                styled_dataframe(top_edges_by_volume),
                use_container_width=True,
                hide_index=True,
            )

    with tab2:
        top_edges_by_wait = (
            non_self_loop_edges[
                [
                    "edge_rank",
                    "transition",
                    "transition_count",
                    "case_count",
                    "median_waiting_time_days",
                    "p90_waiting_time_days",
                    "total_waiting_time_days",
                    "share_of_waiting_time_pct",
                    "flow_impact_score",
                ]
            ]
            .sort_values("share_of_waiting_time_pct", ascending=False)
            .head(15)
            .rename(
                columns={
                    "edge_rank": "Rank",
                    "transition": "Process Flow",
                    "transition_count": "Transitions",
                    "case_count": "Cases",
                    "median_waiting_time_days": "Median Wait Days",
                    "p90_waiting_time_days": "P90 Wait Days",
                    "total_waiting_time_days": "Total Wait Days",
                    "share_of_waiting_time_pct": "Waiting-Time Share %",
                    "flow_impact_score": "Impact Score",
                }
            )
        )

        with module_container(
            title="Top Process Flows by Waiting-Time Contribution",
            subtitle="Transitions that explain where delay accumulates in the real process.",
            eyebrow="Delay Contribution",
        ):
            st.dataframe(
                styled_dataframe(top_edges_by_wait),
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        top_activities = (
            process_activities[
                [
                    "activity_rank",
                    "activity",
                    "event_count",
                    "case_count",
                    "share_of_events_pct",
                    "share_of_cases_pct",
                ]
            ]
            .head(15)
            .rename(
                columns={
                    "activity_rank": "Rank",
                    "activity": "Activity",
                    "event_count": "Events",
                    "case_count": "Cases",
                    "share_of_events_pct": "Share of Events %",
                    "share_of_cases_pct": "Share of Cases %",
                }
            )
        )

        with module_container(
            title="Top Activities",
            subtitle="Activities ranked by event volume and case coverage.",
            eyebrow="Activity Footprint",
        ):
            st.dataframe(
                styled_dataframe(top_activities),
                use_container_width=True,
                hide_index=True,
            )

    with module_container(
        title="Interpretation",
        subtitle="How to read this page.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            """
            The Process Explorer shows the real observed process flow, not the documented target process.
            For readability, the main view focuses on non-self-loop transitions.

            Self-loops can still be relevant for rework analysis, but they are not ideal as the first
            management-facing process-flow signal.

            The key takeaway is that process volume is concentrated around goods receipt and invoice
            receipt flows, while the largest operational delay accumulates between invoice receipt and
            invoice clearing.
            """
        )