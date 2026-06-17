import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def _safe_get_first_row(df: pd.DataFrame) -> pd.Series | None:
    if df is None or df.empty:
        return None

    return df.iloc[0]


def _format_column_name(column: str) -> str:
    return str(column).replace("_", " ").title()


def _get_priority_count(
    recommendations: pd.DataFrame,
    priority: str,
) -> int:
    if recommendations is None or recommendations.empty:
        return 0

    if "priority" not in recommendations.columns:
        return 0

    return int((recommendations["priority"] == priority).sum())


def _get_top_delay_cost_driver(
    delay_cost_estimate: pd.DataFrame | None,
) -> pd.Series | None:
    if delay_cost_estimate is None or delay_cost_estimate.empty:
        return None

    if "estimated_delay_cost" not in delay_cost_estimate.columns:
        return delay_cost_estimate.iloc[0]

    return delay_cost_estimate.sort_values(
        "estimated_delay_cost",
        ascending=False,
    ).iloc[0]


def _get_delay_cost_summary(
    delay_cost_estimate: pd.DataFrame | None,
) -> dict:
    if delay_cost_estimate is None or delay_cost_estimate.empty:
        return {
            "has_delay_cost": False,
            "top_transition": "Record Invoice Receipt → Clear Invoice",
            "top_estimated_cost": 0.0,
            "top_cost_share": 0.0,
            "estimated_cost_per_case": 0.0,
            "total_estimated_cost": 0.0,
            "assumed_cost_per_waiting_day": 0.0,
        }

    top_driver = _get_top_delay_cost_driver(delay_cost_estimate)

    total_estimated_cost = (
        delay_cost_estimate["estimated_delay_cost"].sum()
        if "estimated_delay_cost" in delay_cost_estimate.columns
        else 0.0
    )

    return {
        "has_delay_cost": True,
        "top_transition": str(top_driver.get("transition", "Unknown transition")),
        "top_estimated_cost": float(top_driver.get("estimated_delay_cost", 0.0)),
        "top_cost_share": float(
            top_driver.get("share_of_estimated_delay_cost_pct", 0.0)
        ),
        "estimated_cost_per_case": float(
            top_driver.get("estimated_cost_per_case", 0.0)
        ),
        "total_estimated_cost": float(total_estimated_cost),
        "assumed_cost_per_waiting_day": float(
            top_driver.get("assumed_cost_per_waiting_day", 0.0)
        ),
    }


def _prepare_recommendation_table(
    recommendations: pd.DataFrame,
) -> pd.DataFrame:
    preferred_columns = [
        "priority_rank",
        "priority",
        "recommendation_type",
        "focus_area",
        "observed_issue",
        "business_rationale",
        "expected_lever",
        "source_module",
    ]

    available_columns = [
        column for column in preferred_columns if column in recommendations.columns
    ]

    if not available_columns:
        return recommendations.head(10).copy()

    table = recommendations[available_columns].head(10).copy()

    table = table.rename(
        columns={
            column: _format_column_name(column)
            for column in table.columns
        }
    )

    return table


def _prepare_delay_cost_table(
    delay_cost_estimate: pd.DataFrame,
) -> pd.DataFrame:
    if delay_cost_estimate is None or delay_cost_estimate.empty:
        return pd.DataFrame()

    preferred_columns = [
        "delay_cost_rank",
        "transition",
        "transition_count",
        "median_waiting_time_days",
        "p90_waiting_time_days",
        "estimated_delay_cost",
        "estimated_cost_per_case",
        "share_of_estimated_delay_cost_pct",
        "dominant_item_category",
    ]

    available_columns = [
        column for column in preferred_columns if column in delay_cost_estimate.columns
    ]

    if not available_columns:
        return delay_cost_estimate.head(10).copy()

    table = delay_cost_estimate[available_columns].head(10).copy()

    table = table.rename(
        columns={
            "delay_cost_rank": "Rank",
            "transition": "Transition",
            "transition_count": "Transitions",
            "median_waiting_time_days": "Median Wait Days",
            "p90_waiting_time_days": "P90 Wait Days",
            "estimated_delay_cost": "Estimated Delay Cost",
            "estimated_cost_per_case": "Estimated Cost per Case",
            "share_of_estimated_delay_cost_pct": "Delay Cost Share %",
            "dominant_item_category": "Dominant Item Category",
        }
    )

    return table


def render_recommendations_view(
    recommendations: pd.DataFrame,
    delay_cost_estimate: pd.DataFrame | None = None,
) -> None:
    st.markdown("## 🎯 Recommendations")

    if recommendations is None or recommendations.empty:
        with module_container(
            title="Recommendations Missing",
            subtitle="The recommendation output is not available.",
            eyebrow="Pipeline Status",
        ):
            st.warning("No recommendation data available.")
        return

    top_recommendation = _safe_get_first_row(recommendations)
    delay_summary = _get_delay_cost_summary(delay_cost_estimate)

    high_priority_count = _get_priority_count(recommendations, "High")
    medium_priority_count = _get_priority_count(recommendations, "Medium")

    recommendation_focus = str(
        top_recommendation.get("focus_area", "Invoice clearing process review")
    )
    recommendation_type = str(
        top_recommendation.get("recommendation_type", "Process improvement")
    )
    expected_lever = str(
        top_recommendation.get("expected_lever", "Reduce operational waiting time")
    )

    if "Record Invoice Receipt" in recommendation_focus and "Clear Invoice" in recommendation_focus:
        recommendation_label = "Invoice clearing process review"
    else:
        recommendation_label = recommendation_focus

    with module_container(
        title="Executive Recommendation",
        subtitle="Highest-priority action based on bottleneck, recommendation and delay-cost evidence.",
        eyebrow="Management Takeaway",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                The strongest improvement lever is the
                <strong>{recommendation_label}</strong>.
                This recommendation is supported by the same transition appearing as
                top recommendation focus area and top estimated delay-cost driver:
                <strong>{delay_summary["top_transition"]}</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-box">
                Cost values are assumption-based decision-support units, not actual financial accounting values.
                They help prioritize improvement work by estimated operational impact.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Top Recommendation Impact",
        subtitle="Business impact attached to the highest-priority recommendation.",
        eyebrow="Decision Support",
    ):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="🎯",
                label="Top Recommendation",
                value="Invoice clearing review",
                delta=recommendation_type,
                positive=True,
            )

        with col2:
            render_kpi_card(
                icon="💸",
                label="Estimated Delay Cost",
                value=f"{delay_summary['top_estimated_cost'] / 1_000_000:,.1f}M",
                delta="cost units",
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="📊",
                label="Delay-Cost Share",
                value=f"{delay_summary['top_cost_share']:.2f}%",
                delta="of total estimated delay cost",
                positive=False,
            )

        with col4:
            render_kpi_card(
                icon="📦",
                label="Cost per Case",
                value=f"{delay_summary['estimated_cost_per_case']:,.0f}",
                delta="estimated cost units",
                positive=False,
            )

        st.markdown(
            f"""
            <div class="hero-card">
                <h2>{delay_summary["top_transition"]}</h2>
                <p>
                    This transition contributes
                    <strong>{delay_summary["top_cost_share"]:.2f}%</strong>
                    of total estimated delay cost and should therefore be reviewed first.
                </p>
                <p>
                    Recommended lever:
                    <strong>{expected_lever}</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Recommendation Backlog",
        subtitle="Rule-based improvement actions derived from process intelligence modules.",
        eyebrow="Action Portfolio",
    ):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="🎯",
                label="Recommendations",
                value=f"{len(recommendations):,}",
                delta="generated actions",
                positive=True,
            )

        with col2:
            render_kpi_card(
                icon="🔥",
                label="High Priority",
                value=f"{high_priority_count:,}",
                delta="immediate focus",
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="📌",
                label="Medium Priority",
                value=f"{medium_priority_count:,}",
                delta="next review",
                positive=True,
            )

        with col4:
            render_kpi_card(
                icon="⚙️",
                label="Cost Assumption",
                value=f"{delay_summary['assumed_cost_per_waiting_day']:,.0f}",
                delta="cost units / waiting day",
                positive=True,
            )

    with module_container(
        title="Prioritized Actions",
        subtitle="Focused backlog for process owners.",
        eyebrow="Action Prioritization",
    ):
        recommendation_table = _prepare_recommendation_table(recommendations)

        st.dataframe(
            styled_dataframe(recommendation_table),
            use_container_width=True,
            hide_index=True,
        )

    with module_container(
        title="Delay-Cost Evidence",
        subtitle="Estimated delay-cost evidence behind recommendation prioritization.",
        eyebrow="Business Impact",
    ):
        if delay_summary["has_delay_cost"]:
            delay_cost_table = _prepare_delay_cost_table(delay_cost_estimate)

            st.dataframe(
                styled_dataframe(delay_cost_table),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Delay-cost estimate is not available. "
                "The recommendation still uses bottleneck and recommendation outputs."
            )

    with module_container(
        title="Business Interpretation",
        subtitle="How to use the recommendation layer.",
        eyebrow="Management View",
    ):
        st.markdown(
            """
            The recommendation layer does not automate management decisions.
            It converts process findings into a prioritized improvement backlog.

            **Current management conclusion:**  
            Invoice clearing should be reviewed first because it is supported by bottleneck,
            recommendation and delay-cost evidence.

            **Operational focus areas:**
            - approval delays
            - invoice exception handling
            - vendor-specific SLA patterns
            - invoice-before-goods-receipt cases
            - handover and rework drivers
            """
        )