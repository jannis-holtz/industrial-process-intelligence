import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def render_variant_intelligence_view(variant_analysis: pd.DataFrame) -> None:
    st.markdown("## Variant Intelligence")

    total_variants = len(variant_analysis)
    top_10_coverage = variant_analysis.head(10)["share_of_cases_pct"].sum()
    top_25_coverage = variant_analysis.head(25)["share_of_cases_pct"].sum()

    with module_container(
        title="Decision Focus",
        subtitle="Identify dominant process paths and prioritize inefficient high-volume variants.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                The process contains <strong>{total_variants:,}</strong> distinct variants.
                The Top 10 variants cover <strong>{top_10_coverage:.2f}%</strong> of operational cases,
                while the Top 25 variants cover <strong>{top_25_coverage:.2f}%</strong>.
                This means improvement work can focus on a manageable set of high-volume paths first.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card(
            icon="🧭",
            label="Distinct Variants",
            value=f"{total_variants:,}",
            delta="process complexity",
            positive=False,
        )

    with col2:
        render_kpi_card(
            icon="🎯",
            label="Top 10 Coverage",
            value=f"{top_10_coverage:.1f}%",
            delta="case concentration",
            positive=True,
        )

    with col3:
        render_kpi_card(
            icon="📌",
            label="Top 25 Coverage",
            value=f"{top_25_coverage:.1f}%",
            delta="focus area",
            positive=True,
        )

    st.write("")

    top_variants = variant_analysis[
        [
            "variant_rank",
            "case_count",
            "share_of_cases_pct",
            "median_cycle_time_days",
            "p90_cycle_time_days",
            "average_event_count",
            "dominant_item_category",
            "variant_name",
        ]
    ].head(15)

    with module_container(
        title="Top Variants by Case Volume",
        subtitle="Most frequent process paths in the operational KPI view.",
        eyebrow="Variant Ranking",
    ):
        st.dataframe(
            styled_dataframe(top_variants),
            use_container_width=True,
            hide_index=True,
        )

    highest_impact = (
        variant_analysis[
            [
                "variant_rank",
                "case_count",
                "share_of_cases_pct",
                "median_cycle_time_days",
                "impact_score",
                "dominant_item_category",
                "variant_name",
            ]
        ]
        .sort_values("impact_score", ascending=False)
        .head(15)
    )

    with module_container(
        title="Highest Impact Variants",
        subtitle="Variants with a combination of high volume and high median cycle time.",
        eyebrow="Improvement Priority",
    ):
        st.dataframe(
            styled_dataframe(highest_impact),
            use_container_width=True,
            hide_index=True,
        )

    with module_container(
        title="Interpretation",
        subtitle="What this means for process improvement.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            """
            The process has a large number of variants, but most operational volume is concentrated
            in a limited set of dominant paths. Improvement initiatives should first target variants
            that combine high case volume with high median cycle time or payment-block-related activities.
            """
        )