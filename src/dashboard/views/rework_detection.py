import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def get_rework_summary(
    rework_case_analysis: pd.DataFrame,
) -> dict:
    if rework_case_analysis is None or rework_case_analysis.empty:
        return {
            "total_cases": 0,
            "rework_cases": 0,
            "rework_share": 0.0,
            "avg_with_rework": 0.0,
            "avg_without_rework": 0.0,
            "cycle_time_gap": 0.0,
        }

    total_cases = len(rework_case_analysis)

    if "has_rework" not in rework_case_analysis.columns:
        return {
            "total_cases": total_cases,
            "rework_cases": 0,
            "rework_share": 0.0,
            "avg_with_rework": 0.0,
            "avg_without_rework": 0.0,
            "cycle_time_gap": 0.0,
        }

    rework_cases_df = rework_case_analysis[
        rework_case_analysis["has_rework"] == 1
    ]
    non_rework_cases_df = rework_case_analysis[
        rework_case_analysis["has_rework"] == 0
    ]

    rework_cases = len(rework_cases_df)
    rework_share = rework_cases / total_cases * 100 if total_cases > 0 else 0.0

    if "cycle_time_days" in rework_case_analysis.columns:
        avg_with_rework = rework_cases_df["cycle_time_days"].mean()
        avg_without_rework = non_rework_cases_df["cycle_time_days"].mean()
    else:
        avg_with_rework = 0.0
        avg_without_rework = 0.0

    cycle_time_gap = avg_with_rework - avg_without_rework

    return {
        "total_cases": total_cases,
        "rework_cases": rework_cases,
        "rework_share": rework_share,
        "avg_with_rework": avg_with_rework,
        "avg_without_rework": avg_without_rework,
        "cycle_time_gap": cycle_time_gap,
    }


def get_top_rework_activity(
    rework_activity_analysis: pd.DataFrame,
) -> pd.Series | None:
    if rework_activity_analysis is None or rework_activity_analysis.empty:
        return None

    if "activity" not in rework_activity_analysis.columns:
        return None

    return rework_activity_analysis.iloc[0]


def get_column_value(
    row: pd.Series,
    column: str,
    default: float | str = "n/a",
) -> float | str:
    if row is None:
        return default

    if column not in row.index:
        return default

    return row[column]


def prepare_rework_activity_table(
    rework_activity_analysis: pd.DataFrame,
) -> pd.DataFrame:
    if rework_activity_analysis is None or rework_activity_analysis.empty:
        return pd.DataFrame()

    table = rework_activity_analysis.head(15).copy()

    rename_map = {
        "rework_activity_rank": "Rank",
        "activity": "Activity",
        "rework_cases": "Rework Cases",
        "total_rework_events": "Total Rework Events",
        "average_occurrences_when_repeated": "Avg Occurrences when Repeated",
        "share_of_rework_cases_pct": "Share of Rework Cases %",
        "impact_score": "Impact Score",
    }

    table = table.rename(
        columns={
            old_name: new_name
            for old_name, new_name in rename_map.items()
            if old_name in table.columns
        }
    )

    preferred_columns = [
        "Rank",
        "Activity",
        "Rework Cases",
        "Total Rework Events",
        "Avg Occurrences when Repeated",
        "Share of Rework Cases %",
        "Impact Score",
    ]

    existing_columns = [
        column for column in preferred_columns if column in table.columns
    ]

    if existing_columns:
        table = table[existing_columns]

    return table


def prepare_rework_case_sample(
    rework_case_analysis: pd.DataFrame,
) -> pd.DataFrame:
    if rework_case_analysis is None or rework_case_analysis.empty:
        return pd.DataFrame()

    display_columns = [
        "case_id",
        "cycle_time_days",
        "has_rework",
        "rework_activity_count",
        "total_rework_events",
        "unique_rework_activities",
    ]

    existing_columns = [
        column for column in display_columns if column in rework_case_analysis.columns
    ]

    if not existing_columns:
        return rework_case_analysis.head(20).copy()

    table = rework_case_analysis[existing_columns].head(20).copy()

    table = table.rename(
        columns={
            "case_id": "Case ID",
            "cycle_time_days": "Cycle Time Days",
            "has_rework": "Has Rework",
            "rework_activity_count": "Rework Activity Count",
            "total_rework_events": "Total Rework Events",
            "unique_rework_activities": "Unique Rework Activities",
        }
    )

    return table


def render_rework_activity_cards(
    rework_activity_analysis: pd.DataFrame,
) -> None:
    if rework_activity_analysis is None or rework_activity_analysis.empty:
        st.info("Rework activity analysis output is not available.")
        return

    top_activities = rework_activity_analysis.head(5).copy()

    columns = st.columns(5)

    for index, (_, row) in enumerate(top_activities.iterrows()):
        activity = str(get_column_value(row, "activity", "Unknown activity"))
        rework_cases = get_column_value(row, "rework_cases", 0)
        share = get_column_value(row, "share_of_rework_cases_pct", 0.0)

        with columns[index]:
            st.markdown(
                f"""
                <div class="hero-card" style="min-height: 180px;">
                    <p style="color:#60a5fa;font-size:0.75rem;font-weight:800;margin-bottom:0.45rem;">
                        #{index + 1} Rework Driver
                    </p>
                    <h3 style="font-size:1rem;line-height:1.25;margin-bottom:0.85rem;">
                        {activity}
                    </h3>
                    <p style="font-size:0.86rem;margin-bottom:0.25rem;">
                        <strong>{int(rework_cases):,}</strong> cases
                    </p>
                    <p style="font-size:0.82rem;color:#cbd5e1;">
                        {float(share):.2f}% of rework cases
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_rework_detection_view(
    rework_case_analysis: pd.DataFrame,
    rework_activity_analysis: pd.DataFrame,
) -> None:
    st.markdown("## 🔁 Rework Detection")

    if rework_case_analysis is None or rework_case_analysis.empty:
        with module_container(
            title="Rework Detection not available",
            subtitle="The required rework output is missing or empty.",
            eyebrow="Missing Data",
        ):
            st.warning("Run `python scripts/11_calculate_rework_detection.py` first.")
        return

    summary = get_rework_summary(rework_case_analysis)
    top_rework_activity = get_top_rework_activity(rework_activity_analysis)

    top_activity_name = (
        str(top_rework_activity["activity"])
        if top_rework_activity is not None
        and "activity" in top_rework_activity.index
        else "Not available"
    )

    top_activity_cases = (
        int(top_rework_activity["rework_cases"])
        if top_rework_activity is not None
        and "rework_cases" in top_rework_activity.index
        else 0
    )

    top_activity_share = (
        float(top_rework_activity["share_of_rework_cases_pct"])
        if top_rework_activity is not None
        and "share_of_rework_cases_pct" in top_rework_activity.index
        else 0.0
    )

    with module_container(
        title="Executive Rework Summary",
        subtitle="Business view of repeated activities and their cycle-time impact.",
        eyebrow="Management View",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                <strong>{summary["rework_share"]:.2f}%</strong> of operational cases contain
                repeated activities. Rework cases take on average
                <strong>{summary["cycle_time_gap"]:.2f} additional days</strong>
                compared with cases without rework.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="🔁",
                label="Rework Share",
                value=f"{summary['rework_share']:.2f}%",
                delta=f"{summary['rework_cases']:,} cases with rework",
                positive=False,
            )

        with col2:
            render_kpi_card(
                icon="⏱️",
                label="Cycle Time Impact",
                value=f"+{summary['cycle_time_gap']:.2f} d",
                delta="with rework vs. without rework",
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="📈",
                label="Avg with Rework",
                value=f"{summary['avg_with_rework']:.2f} d",
                delta="average cycle time",
                positive=False,
            )

        with col4:
            render_kpi_card(
                icon="✅",
                label="Avg without Rework",
                value=f"{summary['avg_without_rework']:.2f} d",
                delta="baseline cases",
                positive=True,
            )

    with module_container(
        title="Primary Rework Hotspot",
        subtitle="Most relevant repeated activity in the analyzed process.",
        eyebrow="Rework Hotspot",
    ):
        left, right = st.columns([1.1, 0.9])

        with left:
            st.markdown(
                f"""
                <div class="hero-card">
                    <p style="color:#f59e0b;font-size:0.82rem;font-weight:800;margin-bottom:0.6rem;">
                        Strongest Rework Signal
                    </p>
                    <h2>{top_activity_name}</h2>
                    <p>
                        This activity appears repeatedly in
                        <strong>{top_activity_cases:,}</strong> cases and explains
                        <strong>{top_activity_share:.2f}%</strong> of all rework cases.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            st.markdown(
                """
                <div class="info-box">
                    <strong>Interpretation:</strong><br>
                    Rework is not treated as a data-quality issue here. It is interpreted as
                    an operational signal for repeated checks, corrections, missing information,
                    quantity changes or process loops.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with module_container(
        title="Top Rework Drivers",
        subtitle="The five most relevant activities behind repeated execution.",
        eyebrow="Driver Overview",
    ):
        render_rework_activity_cards(rework_activity_analysis)

    with module_container(
        title="Management Interpretation",
        subtitle="What the rework findings mean for process improvement.",
        eyebrow="Business Insight",
    ):
        st.markdown(
            f"""
            The most important signal is **{top_activity_name}**. This suggests that improvement
            work should start by reviewing why this activity is repeated and whether the repetition
            is caused by missing information, process exceptions, quantity changes, goods-receipt
            corrections or invoice-matching issues.

            From a management perspective, the key message is simple:
            **rework is measurable, concentrated and linked to longer cycle times.**
            """
        )

    with st.expander("Show detailed rework activity table", expanded=False):
        activity_table = prepare_rework_activity_table(rework_activity_analysis)

        if not activity_table.empty:
            st.dataframe(
                styled_dataframe(activity_table),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Rework activity analysis output is not available.")

    with st.expander("Show case-level rework sample", expanded=False):
        case_sample = prepare_rework_case_sample(rework_case_analysis)

        if not case_sample.empty:
            st.dataframe(
                styled_dataframe(case_sample),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No case-level rework sample available.")