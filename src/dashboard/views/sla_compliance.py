import pandas as pd
import streamlit as st

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    styled_dataframe,
)


def get_sla_metric_value(
    sla_metrics: pd.DataFrame,
    metric_name: str,
    default: float = 0.0,
) -> float:
    if sla_metrics is None or sla_metrics.empty:
        return default

    metric_row = sla_metrics[sla_metrics["metric"] == metric_name]

    if metric_row.empty:
        return default

    return float(metric_row.iloc[0]["value"])


def prepare_sla_breakdown_table(sla_breakdown: pd.DataFrame) -> pd.DataFrame:
    display_columns = [
        "sla_rank",
        "dimension",
        "dimension_value",
        "cases",
        "sla_breaches",
        "sla_breach_rate_pct",
        "sla_breach_contribution_pct",
        "median_cycle_time_days",
        "p90_cycle_time_days",
        "impact_score",
    ]

    existing_columns = [
        column for column in display_columns if column in sla_breakdown.columns
    ]

    table = sla_breakdown[existing_columns].head(15).copy()

    table = table.rename(
        columns={
            "sla_rank": "Rank",
            "dimension": "Dimension",
            "dimension_value": "Value",
            "cases": "Cases",
            "sla_breaches": "SLA Breaches",
            "sla_breach_rate_pct": "Breach Rate %",
            "sla_breach_contribution_pct": "Breach Contribution %",
            "median_cycle_time_days": "Median Cycle Time Days",
            "p90_cycle_time_days": "P90 Cycle Time Days",
            "impact_score": "Impact Score",
        }
    )

    return table


def get_top_signal(
    sla_breakdown: pd.DataFrame,
    dimension: str,
) -> pd.Series | None:
    if sla_breakdown is None or sla_breakdown.empty:
        return None

    signals = sla_breakdown[sla_breakdown["dimension"] == dimension].copy()

    if signals.empty:
        return None

    return signals.sort_values("impact_score", ascending=False).iloc[0]


def render_signal_card(
    title: str,
    signal: pd.Series | None,
    fallback_text: str,
) -> None:
    if signal is None:
        st.info(fallback_text)
        return

    st.markdown(
        f"""
        <div class="hero-card">
            <h2>{title}</h2>
            <p style="font-size:1.05rem;margin-top:0.6rem;">
                <strong>{signal["dimension_value"]}</strong>
            </p>
            <p>
                <strong>{int(signal["sla_breaches"]):,}</strong> SLA breaches ·
                <strong>{signal["sla_breach_rate_pct"]:.2f}%</strong> breach rate ·
                <strong>{signal["sla_breach_contribution_pct"]:.2f}%</strong> contribution
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sla_compliance_view(
    sla_metrics: pd.DataFrame,
    sla_breakdown: pd.DataFrame,
) -> None:
    st.markdown("## 📍 SLA Compliance")

    if sla_metrics is None or sla_metrics.empty:
        with module_container(
            title="SLA Compliance not available",
            subtitle="The required SLA metrics output is missing or empty.",
            eyebrow="Missing Data",
        ):
            st.warning("Run `python scripts/10_calculate_sla_metrics.py` first.")
        return

    sla_threshold = get_sla_metric_value(
        sla_metrics,
        "analytical_sla_threshold_days",
    )
    operational_cases = get_sla_metric_value(
        sla_metrics,
        "total_operational_cases",
    )
    sla_fulfilled_cases = get_sla_metric_value(
        sla_metrics,
        "sla_fulfilled_cases",
    )
    sla_breached_cases = get_sla_metric_value(
        sla_metrics,
        "sla_breached_cases",
    )
    sla_compliance_rate = get_sla_metric_value(
        sla_metrics,
        "sla_compliance_rate_pct",
    )
    sla_breach_rate = get_sla_metric_value(
        sla_metrics,
        "sla_breach_rate_pct",
    )

    top_vendor_driver = get_top_signal(sla_breakdown, "vendor")
    top_category_driver = get_top_signal(sla_breakdown, "item_category")
    top_document_driver = get_top_signal(sla_breakdown, "document_type")

    with module_container(
        title="Executive SLA Summary",
        subtitle="Business-oriented view of service-level performance in the Purchase-to-Pay process.",
        eyebrow="Management View",
    ):
        st.markdown(
            f"""
            <div class="decision-box">
                <strong>{sla_breach_rate:.2f}%</strong> of operational cases breach the analytical
                <strong>{sla_threshold:.0f}-day SLA threshold</strong>.
                The breach pattern is not random: SLA risk is concentrated around specific vendors,
                document types and invoice-before-goods-receipt process patterns.
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="✅",
                label="SLA Compliance",
                value=f"{sla_compliance_rate:.2f}%",
                delta=f"{int(sla_fulfilled_cases):,} fulfilled cases",
                positive=True,
            )

        with col2:
            render_kpi_card(
                icon="⚠️",
                label="SLA Breach Rate",
                value=f"{sla_breach_rate:.2f}%",
                delta=f"{int(sla_breached_cases):,} breached cases",
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="🎯",
                label="SLA Threshold",
                value=f"{sla_threshold:.0f} d",
                delta="analytical target",
                positive=True,
            )

        with col4:
            render_kpi_card(
                icon="📦",
                label="Operational Cases",
                value=f"{int(operational_cases):,}",
                delta="cases analyzed",
                positive=True,
            )

    with module_container(
        title="Where SLA Risk Concentrates",
        subtitle="The most relevant drivers behind SLA breaches.",
        eyebrow="Root Cause Signals",
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            render_signal_card(
                title="Top Vendor Driver",
                signal=top_vendor_driver,
                fallback_text="No vendor-level SLA signal available.",
            )

        with col2:
            render_signal_card(
                title="Top Process Category",
                signal=top_category_driver,
                fallback_text="No item-category SLA signal available.",
            )

        with col3:
            render_signal_card(
                title="Top Document Type",
                signal=top_document_driver,
                fallback_text="No document-type SLA signal available.",
            )

        st.markdown(
            """
            <div class="info-box">
                Management implication: SLA improvement should not start with the whole process equally.
                The first review should focus on the vendor and invoice-before-goods-receipt patterns
                that explain a disproportionate share of SLA breaches.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Recommended Management Action",
        subtitle="How the SLA findings should be used.",
        eyebrow="Decision Support",
    ):
        st.markdown(
            """
            <div class="decision-box">
                <strong>Recommended next action:</strong><br>
                Review the invoice-before-goods-receipt flow and the highest-impact vendor group first.
                These signals should be compared with bottleneck findings around
                <strong>Record Invoice Receipt → Clear Invoice</strong> and root-cause findings
                before defining process-improvement measures.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Show detailed SLA breakdown table", expanded=False):
        if sla_breakdown is not None and not sla_breakdown.empty:
            breakdown_table = prepare_sla_breakdown_table(sla_breakdown)

            st.dataframe(
                styled_dataframe(breakdown_table),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("SLA breakdown output is not available.")