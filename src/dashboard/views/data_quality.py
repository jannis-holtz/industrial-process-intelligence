import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
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


def render_data_quality_view(
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
    data_quality_report: pd.DataFrame,
) -> None:
    st.markdown("## Data Quality & KPI Governance")

    raw_case_count = len(raw_cases)
    operational_case_count = len(operational_cases)
    excluded_case_count = raw_case_count - operational_case_count
    excluded_case_share = excluded_case_count / raw_case_count * 100

    raw_avg_cycle_time = raw_cases["cycle_time_days"].mean()
    operational_avg_cycle_time = operational_cases["cycle_time_days"].mean()
    avg_cycle_time_delta = raw_avg_cycle_time - operational_avg_cycle_time

    raw_median_cycle_time = raw_cases["cycle_time_days"].median()
    operational_median_cycle_time = operational_cases["cycle_time_days"].median()

    raw_max_cycle_time = raw_cases["cycle_time_days"].max()
    operational_max_cycle_time = operational_cases["cycle_time_days"].max()

    outlier_cases = raw_cases[
        raw_cases["cycle_time_days"] > OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS
    ].sort_values("cycle_time_days", ascending=False)

    with module_container(
        title="Decision Focus",
        subtitle="Separate operational performance from extreme data-quality exceptions.",
        eyebrow="KPI Governance",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                Only <strong>{excluded_case_count:,}</strong> out of
                <strong>{raw_case_count:,}</strong> cases are excluded from operational KPI reporting
                using a transparent threshold of
                <strong>{OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS} days</strong>.
                This keeps management KPIs stable while preserving all raw cases for audit and exception analysis.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            icon="🧾",
            label="Raw Cases",
            value=f"{raw_case_count:,}",
            delta="full dataset",
            positive=True,
        )

    with col2:
        render_kpi_card(
            icon="✅",
            label="Operational Cases",
            value=f"{operational_case_count:,}",
            delta="used for KPI reporting",
            positive=True,
        )

    with col3:
        render_kpi_card(
            icon="⚠️",
            label="Excluded Cases",
            value=f"{excluded_case_count:,}",
            delta=f"{excluded_case_share:.2f}% of raw cases",
            positive=False,
        )

    with col4:
        render_kpi_card(
            icon="📉",
            label="Avg KPI Adjustment",
            value=f"{avg_cycle_time_delta:.1f} days",
            delta="raw avg minus operational avg",
            positive=True,
        )

    st.write("")

    left, right = st.columns([1, 1])

    with left:
        with module_container(
            title="Raw KPI View",
            subtitle="Unfiltered dataset including extreme exceptions.",
            eyebrow="Before Governance",
        ):
            st.markdown(
                f"""
                <div class="hero-card">
                    <h2>{raw_avg_cycle_time:.2f} days average cycle time</h2>
                    <p>
                        Median cycle time:
                        <strong>{raw_median_cycle_time:.2f} days</strong>.
                    </p>
                    <p>
                        Maximum observed cycle time:
                        <strong>{raw_max_cycle_time:,.2f} days</strong>.
                    </p>
                    <p>
                        This view is retained for audit, exception and data-quality analysis.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        with module_container(
            title="Operational KPI View",
            subtitle="Management KPI view after applying the transparent threshold.",
            eyebrow="After Governance",
        ):
            st.markdown(
                f"""
                <div class="hero-card">
                    <h2>{operational_avg_cycle_time:.2f} days average cycle time</h2>
                    <p>
                        Median cycle time:
                        <strong>{operational_median_cycle_time:.2f} days</strong>.
                    </p>
                    <p>
                        Maximum operational cycle time:
                        <strong>{operational_max_cycle_time:,.2f} days</strong>.
                    </p>
                    <p>
                        This view is used for stable operational process reporting.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    tab1, tab2, tab3 = st.tabs(
        [
            "Governance Summary",
            "Quality Checks",
            "Outlier Cases",
        ]
    )

    with tab1:
        with module_container(
            title="Raw vs Operational KPI Comparison",
            subtitle="Transparent comparison between the full raw view and the operational reporting view.",
            eyebrow="KPI Governance",
        ):
            render_raw_vs_operational_table(raw_cases, operational_cases)

    with tab2:
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

    with tab3:
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

    with module_container(
        title="Interpretation",
        subtitle="How to read this governance layer.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            f"""
            The platform does not delete or hide data. It separates two analytical purposes:
            operational KPI reporting and exception analysis.

            Operational KPIs use the transparent rule
            <strong>cycle_time_days <= {OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS}</strong>.
            Cases above this threshold remain available as outliers and can be reviewed separately.
            This makes the dashboard more reliable for management decisions while keeping the raw-data
            audit trail intact.
            """,
            unsafe_allow_html=True,
        )