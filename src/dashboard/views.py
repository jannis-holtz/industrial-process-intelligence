import pandas as pd
import streamlit as st

from src.dashboard.charts import (
    create_cycle_time_distribution_chart,
    create_item_category_chart,
    create_top_activities_chart,
)
from src.dashboard.components import (
    module_container,
    render_decision_summary,
    render_kpi_card,
    render_kpi_row,
    render_platform_layers,
    render_quality_status_banner,
    styled_dataframe,
)
from src.dashboard.data_access import OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS


def create_raw_vs_operational_comparison(
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
) -> pd.DataFrame:
    comparison = pd.DataFrame(
        [
            {
                "View": "Raw KPI View",
                "Filter Rule": "No filter",
                "Cases": len(raw_cases),
                "Average Cycle Time": raw_cases["cycle_time_days"].mean(),
                "Median Cycle Time": raw_cases["cycle_time_days"].median(),
                "P90 Cycle Time": raw_cases["cycle_time_days"].quantile(0.90),
                "Max Cycle Time": raw_cases["cycle_time_days"].max(),
            },
            {
                "View": "Operational KPI View",
                "Filter Rule": f"cycle_time_days <= {OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS}",
                "Cases": len(operational_cases),
                "Average Cycle Time": operational_cases["cycle_time_days"].mean(),
                "Median Cycle Time": operational_cases["cycle_time_days"].median(),
                "P90 Cycle Time": operational_cases["cycle_time_days"].quantile(0.90),
                "Max Cycle Time": operational_cases["cycle_time_days"].max(),
            },
        ]
    )

    numeric_columns = [
        "Average Cycle Time",
        "Median Cycle Time",
        "P90 Cycle Time",
        "Max Cycle Time",
    ]

    comparison[numeric_columns] = comparison[numeric_columns].round(2)

    return comparison


def render_raw_vs_operational_table(
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
) -> None:
    comparison = create_raw_vs_operational_comparison(raw_cases, operational_cases)

    st.dataframe(
        styled_dataframe(comparison),
        use_container_width=True,
        hide_index=True,
    )


def render_executive_overview(
    event_log: pd.DataFrame,
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
    data_quality_report: pd.DataFrame,
) -> None:
    render_kpi_row(event_log, raw_cases, operational_cases)
    render_quality_status_banner()
    render_decision_summary(raw_cases, operational_cases)

    top_left, top_right = st.columns([2, 1])

    with top_left:
        with module_container(
            title="Operational Cycle Time Distribution",
            subtitle="Distribution of case durations after applying the operational KPI filter rule.",
            eyebrow="Performance",
        ):
            st.plotly_chart(
                create_cycle_time_distribution_chart(operational_cases),
                use_container_width=True,
            )

    with top_right:
        with module_container(
            title="Data Quality Summary",
            subtitle="Quality checks used to separate operational KPIs from exception analysis.",
            eyebrow="Governance",
        ):
            st.markdown(
                """
                <div class="warning-box">
                    Extreme cycle-time outliers are excluded from operational KPIs,
                    but remain part of the raw dataset for exception analysis.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="table-card-info">Documented quality checks and affected case counts.</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                styled_dataframe(data_quality_report),
                use_container_width=True,
                hide_index=True,
            )

    bottom_left, bottom_right = st.columns([1, 1])

    with bottom_left:
        with module_container(
            title="Cycle Time by Item Category",
            subtitle="Comparison of median cycle time across the main purchase process categories.",
            eyebrow="Segmentation",
        ):
            st.plotly_chart(
                create_item_category_chart(operational_cases),
                use_container_width=True,
            )

            item_category_summary = (
                operational_cases.groupby("item_category")
                .agg(
                    cases=("case_id", "count"),
                    median_cycle_time_days=("cycle_time_days", "median"),
                    p90_cycle_time_days=(
                        "cycle_time_days",
                        lambda values: values.quantile(0.90),
                    ),
                )
                .reset_index()
                .sort_values("cases", ascending=False)
            )

            item_category_summary[
                ["median_cycle_time_days", "p90_cycle_time_days"]
            ] = item_category_summary[
                ["median_cycle_time_days", "p90_cycle_time_days"]
            ].round(2)

            st.markdown(
                """
                <div class="subsection-divider"></div>
                <div class="table-card-info">
                    Supporting table for category-level comparison.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.dataframe(
                styled_dataframe(item_category_summary),
                use_container_width=True,
                hide_index=True,
            )

    with bottom_right:
        with module_container(
            title="Top Activities by Event Count",
            subtitle="Most frequent activities observed in the purchase-to-pay event log.",
            eyebrow="Activity Footprint",
        ):
            st.plotly_chart(
                create_top_activities_chart(event_log),
                use_container_width=True,
            )

    with module_container(
        title="Raw vs Operational KPI View",
        subtitle="Comparison between the unfiltered raw view and the operational reporting view.",
        eyebrow="KPI Governance",
    ):
        render_raw_vs_operational_table(raw_cases, operational_cases)

    st.write("")
    render_module_preview_grid()


def render_data_quality_view(
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
    data_quality_report: pd.DataFrame,
) -> None:
    st.markdown("## Data Quality & KPI Governance")

    with module_container(
        title="Decision Focus",
        subtitle="Separate data quality issues from operational process performance.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            """
            <div class="decision-box">
                The goal is not to hide outliers, but to prevent extreme exceptions from distorting
                management KPIs. Raw data remains available for exception and audit analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Raw vs Operational KPI Comparison",
        subtitle="Operational KPI reporting uses a transparent cycle-time threshold.",
        eyebrow="KPI Governance",
    ):
        render_raw_vs_operational_table(raw_cases, operational_cases)

    with module_container(
        title="Data Quality Checks",
        subtitle="Documented checks and affected cases used for KPI governance.",
        eyebrow="Data Quality",
    ):
        st.dataframe(
            styled_dataframe(data_quality_report),
            use_container_width=True,
            hide_index=True,
        )

    outlier_cases = raw_cases[
        raw_cases["cycle_time_days"] > OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS
    ].sort_values("cycle_time_days", ascending=False)

    with module_container(
        title="Top Outlier Cases",
        subtitle="Largest cycle-time exceptions kept outside operational KPI reporting.",
        eyebrow="Exception Analysis",
    ):
        st.dataframe(
            styled_dataframe(
                outlier_cases[
                    [
                        "case_id",
                        "cycle_time_days",
                        "event_count",
                        "activity_count",
                        "company",
                        "item_category",
                        "document_type",
                    ]
                ].head(20)
            ),
            use_container_width=True,
            hide_index=True,
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


def render_bottleneck_analysis_view(bottleneck_analysis: pd.DataFrame) -> None:
    st.markdown("## Bottleneck Analysis")

    top_bottleneck = bottleneck_analysis.iloc[0]
    top_10_wait_share = bottleneck_analysis.head(10)[
        "share_of_total_waiting_time_pct"
    ].sum()

    with module_container(
        title="Decision Focus",
        subtitle="Identify transitions with high waiting time and high operational impact.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                The strongest bottleneck is <strong>{top_bottleneck["transition"]}</strong>.
                It accounts for <strong>{top_bottleneck["share_of_total_waiting_time_pct"]:.2f}%</strong>
                of total observed waiting time and has a median wait of
                <strong>{top_bottleneck["median_waiting_time_days"]:.2f} days</strong>.
                The Top 10 bottlenecks account for <strong>{top_10_wait_share:.2f}%</strong>
                of total waiting time.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card(
            icon="⏱️",
            label="Relevant Transitions",
            value=f"{len(bottleneck_analysis):,}",
            delta="after frequency threshold",
            positive=True,
        )

    with col2:
        render_kpi_card(
            icon="🔥",
            label="Top Bottleneck Share",
            value=f"{top_bottleneck['share_of_total_waiting_time_pct']:.1f}%",
            delta="of total waiting time",
            positive=False,
        )

    with col3:
        render_kpi_card(
            icon="📌",
            label="Top 10 Wait Share",
            value=f"{top_10_wait_share:.1f}%",
            delta="focus area",
            positive=False,
        )

    st.write("")

    top_by_impact = bottleneck_analysis[
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
    ].head(15)

    with module_container(
        title="Top Bottlenecks by Impact Score",
        subtitle="Transitions prioritized by waiting-time contribution and typical delay.",
        eyebrow="Impact Ranking",
    ):
        st.dataframe(
            styled_dataframe(top_by_impact),
            use_container_width=True,
            hide_index=True,
        )

    top_by_total_wait = (
        bottleneck_analysis[
            [
                "bottleneck_rank",
                "transition",
                "transition_count",
                "median_waiting_time_days",
                "p90_waiting_time_days",
                "total_waiting_time_days",
                "share_of_total_waiting_time_pct",
                "dominant_item_category",
            ]
        ]
        .sort_values("total_waiting_time_days", ascending=False)
        .head(15)
    )

    with module_container(
        title="Top Transitions by Total Waiting Time",
        subtitle="Transitions contributing the largest absolute amount of waiting time.",
        eyebrow="Waiting-Time Contribution",
    ):
        st.dataframe(
            styled_dataframe(top_by_total_wait),
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
            Bottleneck prioritization should focus first on invoice-related transitions.
            The transition from invoice receipt to invoice clearing dominates total waiting time,
            meaning that improvements in invoice clearing, payment block handling or related approval logic
            are likely to have the largest operational leverage.
            """
        )


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


def render_module_preview_grid() -> None:
    st.markdown("## Intelligence Modules")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🧭 Variant Intelligence</div>
                <div class="module-subtitle">Identify frequent and inefficient process paths.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Start → Purchase Order → Goods Receipt → Invoice Receipt → Clear Invoice
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: variant ranking by frequency and cycle time.
                </p>
                <div class="module-button">Explore Variants →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">⏱️ Bottleneck Analysis</div>
                <div class="module-subtitle">Measure waiting times between process steps.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Focus: transitions with high frequency and high average waiting time.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: bottleneck impact ranking.
                </p>
                <div class="module-button">Explore Bottlenecks →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🔎 Root Cause</div>
                <div class="module-subtitle">Find drivers behind slow or exceptional cases.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Dimensions: item category, company, vendor, document type and activities.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Planned: compare normal vs slow cases.
                </p>
                <div class="module-button">Explore Root Causes →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="module-grid-spacer"></div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🎯 Recommendations</div>
                <div class="module-subtitle">Translate findings into prioritized actions.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Active: rule-based recommendations from bottleneck and variant signals.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Active: action priority ranking.
                </p>
                <div class="module-button">View Recommendations →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">⚠️ Prediction & Risk</div>
                <div class="module-subtitle">Predict cases likely to exceed cycle-time thresholds.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Baseline first, PyTorch LSTM later for sequence modeling.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Planned: risk score and model comparison.
                </p>
                <div class="module-button">Open Prediction Center →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            """
            <div class="module-card-small">
                <div class="module-title">🧱 Platform Layers</div>
                <div class="module-subtitle">Explain how raw process data becomes decisions.</div>
                <p style="color:#cbd5e1;font-size:0.78rem;">
                    Data Layer → Analytics Layer → Prediction Layer → Recommendation Layer.
                </p>
                <p style="color:#38bdf8;font-size:0.78rem;">
                    Available as architecture view.
                </p>
                <div class="module-button">View Platform Layers →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_root_cause_placeholder(operational_cases: pd.DataFrame) -> None:
    st.markdown("## Root Cause")

    with module_container(
        title="Decision Focus",
        subtitle="Find factors associated with long-running cases.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            """
            <div class="decision-box">
                Which categories, vendors, companies or document types are associated with slow cases?
            </div>
            """,
            unsafe_allow_html=True,
        )

    threshold = operational_cases["cycle_time_days"].quantile(0.90)
    enriched = operational_cases.copy()
    enriched["is_slow_case"] = enriched["cycle_time_days"] >= threshold

    root_cause = (
        enriched.groupby("item_category")
        .agg(
            cases=("case_id", "count"),
            slow_cases=("is_slow_case", "sum"),
            median_cycle_time_days=("cycle_time_days", "median"),
        )
        .reset_index()
    )

    root_cause["slow_case_share_pct"] = (
        root_cause["slow_cases"] / root_cause["cases"] * 100
    ).round(2)

    root_cause["median_cycle_time_days"] = root_cause["median_cycle_time_days"].round(2)

    with module_container(
        title="Slow Case Concentration by Item Category",
        subtitle="Uses the P90 cycle-time threshold as a first analytical proxy for slow cases.",
        eyebrow="Root Cause Light",
    ):
        st.dataframe(
            styled_dataframe(root_cause.sort_values("slow_case_share_pct", ascending=False)),
            use_container_width=True,
            hide_index=True,
        )


def render_recommendations_view(recommendations: pd.DataFrame) -> None:
    st.markdown("## Recommendations")

    top_recommendation = recommendations.iloc[0]
    high_priority_count = (recommendations["priority"] == "High").sum()
    medium_priority_count = (recommendations["priority"] == "Medium").sum()

    with module_container(
        title="Decision Focus",
        subtitle="Translate process findings into prioritized improvement actions.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                The highest-priority recommendation is:
                <strong>{top_recommendation["focus_area"]}</strong>.
                It is based on <strong>{top_recommendation["source_module"]}</strong>
                and addresses: {top_recommendation["observed_issue"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

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

    st.write("")

    recommendation_table = recommendations[
        [
            "priority_rank",
            "priority",
            "recommendation_type",
            "focus_area",
            "observed_issue",
            "business_rationale",
            "expected_lever",
            "source_module",
        ]
    ]

    with module_container(
        title="Prioritized Recommendation Backlog",
        subtitle="Rule-based improvement priorities derived from bottleneck and variant analysis.",
        eyebrow="Action Prioritization",
    ):
        st.dataframe(
            styled_dataframe(recommendation_table),
            use_container_width=True,
            hide_index=True,
        )

    with module_container(
        title="Interpretation",
        subtitle="How to use these recommendations.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            """
            The recommendation layer does not automate management decisions.
            It prioritizes where process owners should investigate first.
            The strongest recommendations currently point toward invoice clearing,
            payment block handling and high-volume process variants with elevated cycle time.
            """
        )


def render_prediction_placeholder() -> None:
    st.markdown("## Prediction & Risk")

    with module_container(
        title="Decision Focus",
        subtitle="Prioritize running cases before they exceed a critical cycle-time threshold.",
        eyebrow="Decision Question",
    ):
        st.markdown(
            """
            <div class="decision-box">
                Which running cases are likely to exceed a critical cycle-time threshold?
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([1, 2])

    with col1:
        with module_container(
            title="Risk Model Scope",
            subtitle="The prediction layer is intentionally planned after the process analysis baseline.",
            eyebrow="Prediction Setup",
        ):
            st.metric("Planned Risk Label", "cycle_time > 120 days")
            st.metric("Model Stage", "Not implemented yet")
            st.metric("Required Baseline", "Rule-based + Scikit-learn")

    with col2:
        with module_container(
            title="Modeling Roadmap",
            subtitle="PyTorch is only used if it improves prediction quality against simpler baselines.",
            eyebrow="ML Governance",
        ):
            st.markdown(
                """
                Planned modeling sequence:

                1. Rule-based baseline  
                2. Logistic Regression / Random Forest baseline  
                3. PyTorch LSTM for activity sequences  
                4. Optional Transformer benchmark  
                5. Model comparison against baseline  
                """
            )

            st.warning("PyTorch is intentionally planned after stable KPI, variant and bottleneck logic.")