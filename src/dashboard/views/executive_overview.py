import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.dashboard.components import (
    module_container,
    render_kpi_card,
    render_quality_status_banner,
    styled_dataframe,
)
from src.dashboard.views.module_preview import render_module_preview_grid


def _get_metric_value(
    metrics: pd.DataFrame | None,
    metric_name: str,
    default: float = 0.0,
) -> float:
    if metrics is None or metrics.empty:
        return default

    if "metric" not in metrics.columns or "value" not in metrics.columns:
        return default

    metric_row = metrics[metrics["metric"] == metric_name]

    if metric_row.empty:
        return default

    return float(metric_row.iloc[0]["value"])


def _get_top_bottleneck(
    bottleneck_analysis: pd.DataFrame | None,
) -> tuple[str, str]:
    if bottleneck_analysis is None or bottleneck_analysis.empty:
        return "Not available", "run bottleneck analysis"

    sort_column = (
        "share_of_total_waiting_time_pct"
        if "share_of_total_waiting_time_pct" in bottleneck_analysis.columns
        else "share_of_waiting_time_pct"
    )

    if sort_column not in bottleneck_analysis.columns:
        return "Invoice Receipt → Clear Invoice", "top delay driver"

    top_row = bottleneck_analysis.sort_values(
        sort_column,
        ascending=False,
    ).iloc[0]

    return (
        "Invoice Receipt → Clear Invoice",
        f"{top_row[sort_column]:.2f}% waiting-time share",
    )


def _get_sla_summary(
    sla_metrics: pd.DataFrame | None,
) -> tuple[str, str]:
    breach_rate = _get_metric_value(sla_metrics, "sla_breach_rate_pct", default=-1)
    breached_cases = _get_metric_value(sla_metrics, "sla_breached_cases", default=0)

    if breach_rate < 0:
        return "Not available", "run SLA analysis"

    return (
        f"{breach_rate:.2f}%",
        f"{int(breached_cases):,} breached cases",
    )


def _get_rework_summary(
    rework_case_analysis: pd.DataFrame | None,
) -> tuple[str, str]:
    if rework_case_analysis is None or rework_case_analysis.empty:
        return "Not available", "run rework analysis"

    if "has_rework" not in rework_case_analysis.columns:
        return "Not available", "missing rework flag"

    rework_cases = int(rework_case_analysis["has_rework"].sum())
    rework_share = rework_case_analysis["has_rework"].mean() * 100

    return (
        f"{rework_share:.2f}%",
        f"{rework_cases:,} cases with rework",
    )


def _get_top_rework_activity(
    rework_activity_analysis: pd.DataFrame | None,
) -> str:
    if rework_activity_analysis is None or rework_activity_analysis.empty:
        return "Record Goods Receipt"

    if "activity" not in rework_activity_analysis.columns:
        return "Record Goods Receipt"

    return str(rework_activity_analysis.iloc[0]["activity"])


def _get_top_recommendation(
    recommendations: pd.DataFrame | None,
) -> tuple[str, str]:
    if recommendations is None or recommendations.empty:
        return "Invoice clearing review", "recommendation layer"

    if "priority_rank" in recommendations.columns:
        top_row = recommendations.sort_values("priority_rank").iloc[0]
    else:
        top_row = recommendations.iloc[0]

    focus_area = str(top_row.get("focus_area", "Invoice clearing process review"))
    recommendation_type = str(top_row.get("recommendation_type", "Process improvement"))

    if "Record Invoice Receipt" in focus_area and "Clear Invoice" in focus_area:
        focus_area = "Invoice clearing review"

    return focus_area, recommendation_type


def _get_delay_cost_summary(
    delay_cost_estimate: pd.DataFrame | None,
    bottleneck_analysis: pd.DataFrame | None,
) -> tuple[str, str]:
    if delay_cost_estimate is not None and not delay_cost_estimate.empty:
        possible_value_columns = [
            "estimated_delay_cost",
            "delay_cost",
            "estimated_delay_cost_units",
        ]

        value_column = next(
            (
                column
                for column in possible_value_columns
                if column in delay_cost_estimate.columns
            ),
            None,
        )

        if value_column is not None:
            total_delay_cost = delay_cost_estimate[value_column].sum()
            return (
                f"{total_delay_cost / 1_000_000_000:.2f}B",
                "estimated cost units",
            )

    if bottleneck_analysis is not None and not bottleneck_analysis.empty:
        sort_column = (
            "share_of_total_waiting_time_pct"
            if "share_of_total_waiting_time_pct" in bottleneck_analysis.columns
            else "share_of_waiting_time_pct"
        )

        if sort_column in bottleneck_analysis.columns:
            top_row = bottleneck_analysis.sort_values(
                sort_column,
                ascending=False,
            ).iloc[0]

            return (
                f"{top_row[sort_column]:.2f}%",
                "top delay share",
            )

    return "Pending", "delay cost not built yet"


def _render_purchase_to_pay_flow(
    rework_activity_name: str,
) -> None:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: Arial, sans-serif;
                color: #f8fafc;
            }}

            .flow-shell {{
                width: 100%;
                box-sizing: border-box;
                padding: 0.4rem 0.2rem 0.1rem 0.2rem;
            }}

            .flow-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.1rem;
            }}

            .flow-title {{
                font-size: 1rem;
                font-weight: 800;
                color: #f8fafc;
            }}

            .flow-legend {{
                display: flex;
                justify-content: flex-end;
                gap: 1.35rem;
                color: #94a3b8;
                font-size: 0.78rem;
            }}

            .legend-item {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                white-space: nowrap;
            }}

            .legend-dot {{
                width: 9px;
                height: 9px;
                border-radius: 999px;
                display: inline-block;
            }}

            .legend-rework {{
                background: #f59e0b;
                box-shadow: 0 0 10px rgba(245, 158, 11, 0.75);
            }}

            .legend-sla {{
                background: #facc15;
                box-shadow: 0 0 10px rgba(250, 204, 21, 0.75);
            }}

            .legend-bottleneck {{
                background: #ef4444;
                box-shadow: 0 0 10px rgba(239, 68, 68, 0.75);
            }}

            .flow-area {{
                position: relative;
                min-height: 330px;
                border-radius: 22px;
                overflow: hidden;
                background:
                    radial-gradient(circle at 15% 42%, rgba(14, 165, 233, 0.10), transparent 27%),
                    radial-gradient(circle at 48% 45%, rgba(245, 158, 11, 0.08), transparent 26%),
                    radial-gradient(circle at 78% 45%, rgba(239, 68, 68, 0.08), transparent 26%),
                    linear-gradient(180deg, rgba(15, 23, 42, 0.18), rgba(15, 23, 42, 0.04));
                padding: 1.25rem 0.35rem 0 0.35rem;
                box-sizing: border-box;
            }}

            .flow-row {{
                position: relative;
                z-index: 5;
                display: grid;
                grid-template-columns: 1.18fr 0.52fr 1.18fr 0.52fr 1.18fr 0.52fr 1.18fr 0.52fr 1.18fr;
                align-items: center;
                gap: 0;
                padding: 0 0.25rem;
            }}

            .process-card {{
                position: relative;
                height: 215px;
                border-radius: 18px;
                padding: 1rem 0.9rem 0.9rem 0.9rem;
                box-sizing: border-box;
                border: 1px solid rgba(59, 130, 246, 0.68);
                background:
                    radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.13), transparent 36%),
                    linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(8, 26, 48, 0.94));
                box-shadow:
                    0 16px 35px rgba(0, 0, 0, 0.34),
                    inset 0 0 24px rgba(59, 130, 246, 0.08);
            }}

            .process-card.rework {{
                border-color: rgba(245, 158, 11, 0.95);
                background:
                    radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.22), transparent 38%),
                    linear-gradient(180deg, rgba(54, 35, 19, 0.98), rgba(30, 41, 59, 0.94));
                box-shadow:
                    0 0 32px rgba(245, 158, 11, 0.28),
                    0 16px 35px rgba(0, 0, 0, 0.34);
            }}

            .process-card.sla {{
                border-color: rgba(250, 204, 21, 0.95);
                background:
                    radial-gradient(circle at 50% 0%, rgba(250, 204, 21, 0.18), transparent 38%),
                    linear-gradient(180deg, rgba(42, 42, 24, 0.98), rgba(20, 42, 52, 0.94));
                box-shadow:
                    0 0 30px rgba(250, 204, 21, 0.20),
                    0 16px 35px rgba(0, 0, 0, 0.34);
            }}

            .process-card.bottleneck {{
                border-color: rgba(239, 68, 68, 0.98);
                background:
                    radial-gradient(circle at 50% 0%, rgba(239, 68, 68, 0.20), transparent 38%),
                    linear-gradient(180deg, rgba(62, 21, 30, 0.98), rgba(39, 20, 28, 0.95));
                box-shadow:
                    0 0 34px rgba(239, 68, 68, 0.28),
                    0 16px 35px rgba(0, 0, 0, 0.34);
            }}

            .step-number {{
                position: absolute;
                top: 0.75rem;
                left: 0.75rem;
                width: 24px;
                height: 24px;
                border-radius: 7px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.74rem;
                font-weight: 900;
                color: #cbd5e1;
                background: rgba(59, 130, 246, 0.26);
                border: 1px solid rgba(147, 197, 253, 0.28);
            }}

            .process-icon {{
                text-align: center;
                font-size: 2rem;
                line-height: 1;
                margin-top: 1.3rem;
                margin-bottom: 0.75rem;
                opacity: 0.95;
            }}

            .process-title {{
                color: #f8fafc;
                font-size: 1.1rem;
                line-height: 1.15;
                font-weight: 850;
                text-align: center;
                margin-bottom: 0.7rem;
                min-height: 42px;
            }}

            .process-meta {{
                text-align: center;
                color: #94a3b8;
                font-size: 0.68rem;
                margin-bottom: 0.2rem;
            }}

            .process-value {{
                text-align: center;
                color: #60a5fa;
                font-size: 1.28rem;
                font-weight: 850;
                margin-bottom: 0.35rem;
            }}

            .process-volume {{
                text-align: center;
                color: #cbd5e1;
                font-size: 0.86rem;
            }}

            .process-value.rework-value {{
                color: #f59e0b;
            }}

            .process-value.sla-value {{
                color: #facc15;
            }}

            .process-value.bottleneck-value {{
                color: #ef4444;
            }}

            .process-badge {{
                display: table;
                margin: 0 auto 0.6rem auto;
                padding: 0.25rem 0.55rem;
                border-radius: 8px;
                font-size: 0.62rem;
                font-weight: 900;
                letter-spacing: 0.02em;
                text-transform: uppercase;
            }}

            .badge-rework {{
                color: #f59e0b;
                border: 1px solid rgba(245, 158, 11, 0.86);
                background: rgba(245, 158, 11, 0.13);
            }}

            .badge-sla {{
                color: #facc15;
                border: 1px solid rgba(250, 204, 21, 0.82);
                background: rgba(250, 204, 21, 0.11);
            }}

            .badge-bottleneck {{
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.88);
                background: rgba(239, 68, 68, 0.13);
            }}

            .connector {{
                position: relative;
                height: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 8;
            }}

            .connector-line {{
                position: absolute;
                left: -8px;
                right: 2px;
                height: 2px;
                top: 50%;
                transform: translateY(-50%);
                background: linear-gradient(
                    90deg,
                    rgba(34, 211, 238, 0.06),
                    rgba(34, 211, 238, 0.34),
                    rgba(34, 211, 238, 0.95)
                );
                box-shadow: 0 0 14px rgba(34, 211, 238, 0.28);
            }}

            .connector-arrow {{
                position: absolute;
                right: -2px;
                color: #38bdf8;
                font-size: 2rem;
                line-height: 1;
                text-shadow: 0 0 12px rgba(56, 189, 248, 0.65);
            }}

                        .dot-trail {{
                position: absolute;
                left: 2px;
                right: 18px;
                top: 50%;
                height: 16px;
                transform: translateY(-50%);
                overflow: hidden;
            }}

            .trail-dot {{
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 11px;
                height: 11px;
                border-radius: 999px;
                background: #22d3ee;
                opacity: 0;
                box-shadow:
                    0 0 10px rgba(34, 211, 238, 0.85),
                    0 0 22px rgba(34, 211, 238, 0.45);
                animation: movingFlowDot 4.8s linear infinite;
            }}

            .trail-dot:nth-child(1) {{
                animation-delay: 0s;
                opacity: 0.18;
            }}

            .trail-dot:nth-child(2) {{
                animation-delay: 0.16s;
                opacity: 0.28;
            }}

            .trail-dot:nth-child(3) {{
                animation-delay: 0.32s;
                opacity: 0.42;
            }}

            .moving-dot {{
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 15px;
                height: 15px;
                border-radius: 999px;
                background: #22d3ee;
                opacity: 1;
                box-shadow:
                    0 0 14px rgba(34, 211, 238, 1),
                    0 0 28px rgba(34, 211, 238, 0.85);
                animation: movingFlowDot 4.8s linear infinite;
                animation-delay: 0.48s;
            }}

            .connector-1 .trail-dot,
            .connector-1 .moving-dot {{
                animation-delay: 0s;
            }}

            .connector-2 .trail-dot,
            .connector-2 .moving-dot {{
                animation-delay: 1.2s;
            }}

            .connector-3 .trail-dot,
            .connector-3 .moving-dot {{
                animation-delay: 2.4s;
            }}

            .connector-4 .trail-dot,
            .connector-4 .moving-dot {{
                animation-delay: 3.6s;
            }}

            @keyframes movingFlowDot {{
                0% {{
                    left: 0%;
                    opacity: 0;
                    transform: translateY(-50%) scale(0.75);
                }}
                12% {{
                    opacity: 0.35;
                }}
                35% {{
                    opacity: 1;
                    transform: translateY(-50%) scale(1.05);
                }}
                75% {{
                    opacity: 1;
                }}
                100% {{
                    left: 88%;
                    opacity: 0;
                    transform: translateY(-50%) scale(0.75);
                }}
            }}

            .rework-layer {{
                position: relative;
                height: 95px;
                margin-top: 0.15rem;
                z-index: 2;
            }}

            .rework-line {{
                position: absolute;
                left: 4.4%;
                right: 5.4%;
                top: 0;
                height: 62px;
                border-bottom: 2px dashed rgba(245, 158, 11, 0.72);
                border-left: 2px dashed rgba(245, 158, 11, 0.72);
                border-right: 2px dashed rgba(245, 158, 11, 0.72);
                border-radius: 0 0 22px 22px;
                opacity: 0.88;
            }}

            .rework-up-left {{
                position: absolute;
                left: 4.05%;
                top: -9px;
                color: #f59e0b;
                font-size: 1.25rem;
                font-weight: 900;
            }}

            .rework-up-mid {{
                position: absolute;
                left: 57.8%;
                top: -9px;
                color: #f59e0b;
                font-size: 1.25rem;
                font-weight: 900;
            }}

            .rework-box {{
                position: absolute;
                left: 50%;
                top: 22px;
                transform: translateX(-50%);
                min-width: 360px;
                max-width: 540px;
                background: rgba(15, 23, 42, 0.92);
                border: 1px solid rgba(245, 158, 11, 0.58);
                border-radius: 12px;
                padding: 0.65rem 0.95rem;
                box-shadow:
                    0 12px 28px rgba(0, 0, 0, 0.28),
                    0 0 18px rgba(245, 158, 11, 0.08);
            }}

            .rework-title {{
                color: #f59e0b;
                font-size: 0.76rem;
                font-weight: 900;
                text-transform: uppercase;
                margin-bottom: 0.25rem;
            }}

            .rework-text {{
                color: #cbd5e1;
                font-size: 0.73rem;
                line-height: 1.35;
            }}

            .rework-highlight {{
                color: #fde68a;
                font-weight: 850;
            }}

            @media (max-width: 1150px) {{
                .flow-header {{
                    align-items: flex-start;
                    flex-direction: column;
                    gap: 0.6rem;
                }}

                .flow-legend {{
                    justify-content: flex-start;
                    flex-wrap: wrap;
                }}

                .flow-row {{
                    grid-template-columns: 1fr;
                    gap: 0.85rem;
                }}

                .connector {{
                    display: none;
                }}

                .process-card {{
                    height: auto;
                    min-height: 165px;
                }}

                .process-title {{
                    min-height: auto;
                }}

                .rework-layer {{
                    height: auto;
                    margin-top: 0.85rem;
                }}

                .rework-line,
                .rework-up-left,
                .rework-up-mid {{
                    display: none;
                }}

                .rework-box {{
                    position: relative;
                    left: auto;
                    top: auto;
                    transform: none;
                    min-width: 0;
                    max-width: 100%;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="flow-shell">
            <div class="flow-header">
                <div class="flow-title">Purchase-to-Pay Process Flow</div>

                <div class="flow-legend">
                    <span class="legend-item">
                        <span class="legend-dot legend-rework"></span>
                        Rework Hotspot
                    </span>
                    <span class="legend-item">
                        <span class="legend-dot legend-sla"></span>
                        SLA Risk
                    </span>
                    <span class="legend-item">
                        <span class="legend-dot legend-bottleneck"></span>
                        Top Bottleneck
                    </span>
                </div>
            </div>

            <div class="flow-area">
                <div class="flow-row">
                    <div class="process-card">
                        <div class="step-number">1</div>
                        <div class="process-icon">📄</div>
                        <div class="process-title">Purchase<br>Requisition</div>
                        <div class="process-meta">Process role</div>
                        <div class="process-value">Demand</div>
                        <div class="process-volume">Start signal</div>
                    </div>

                    <div class="connector connector-1">
                        <div class="connector-line"></div>
                        <div class="dot-trail">
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="moving-dot"></span>
                        </div>
                        <div class="connector-arrow">›</div>
                    </div>

                    <div class="process-card">
                        <div class="step-number">2</div>
                        <div class="process-icon">🛒</div>
                        <div class="process-title">Purchase<br>Order</div>
                        <div class="process-meta">Process role</div>
                        <div class="process-value">Order</div>
                        <div class="process-volume">Execution entry</div>
                    </div>

                    <div class="connector connector-2">
                        <div class="connector-line"></div>
                        <div class="dot-trail">
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="moving-dot"></span>
                        </div>
                        <div class="connector-arrow">›</div>
                    </div>

                    <div class="process-card rework">
                        <div class="step-number">3</div>
                        <div class="process-icon">🚚</div>
                        <div class="process-title">Goods<br>Receipt</div>
                        <div class="process-badge badge-rework">Rework Hotspot</div>
                        <div class="process-meta">Strongest signal</div>
                        <div class="process-value rework-value">Rework</div>
                        <div class="process-volume">Repeated activity</div>
                    </div>

                    <div class="connector connector-3">
                        <div class="connector-line"></div>
                        <div class="dot-trail">
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="moving-dot"></span>
                        </div>
                        <div class="connector-arrow">›</div>
                    </div>

                    <div class="process-card sla">
                        <div class="step-number">4</div>
                        <div class="process-icon">💵</div>
                        <div class="process-title">Invoice<br>Receipt</div>
                        <div class="process-badge badge-sla">SLA Risk</div>
                        <div class="process-meta">Risk pattern</div>
                        <div class="process-value sla-value">Invoice</div>
                        <div class="process-volume">before goods receipt</div>
                    </div>

                    <div class="connector connector-4">
                        <div class="connector-line"></div>
                        <div class="dot-trail">
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="trail-dot"></span>
                            <span class="moving-dot"></span>
                        </div>
                        <div class="connector-arrow">›</div>
                    </div>

                    <div class="process-card bottleneck">
                        <div class="step-number">5</div>
                        <div class="process-icon">🏦</div>
                        <div class="process-title">Invoice Clearing<br>/ Payment</div>
                        <div class="process-badge badge-bottleneck">Top Bottleneck</div>
                        <div class="process-meta">Median wait</div>
                        <div class="process-value bottleneck-value">36.17 d</div>
                        <div class="process-volume">main delay driver</div>
                    </div>
                </div>

                <div class="rework-layer">
                    <div class="rework-line"></div>
                    <div class="rework-up-left">↑</div>
                    <div class="rework-up-mid">↑</div>

                    <div class="rework-box">
                        <div class="rework-title">↺ Rework Loop</div>
                        <div class="rework-text">
                            Repeated activities can occur before completion.
                            Strongest current signal:
                            <span class="rework-highlight">{rework_activity_name}</span>.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(html, height=445, scrolling=False)


def render_executive_overview(
    event_log: pd.DataFrame,
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
    data_quality_report: pd.DataFrame,
    bottleneck_analysis: pd.DataFrame | None = None,
    sla_metrics: pd.DataFrame | None = None,
    rework_case_analysis: pd.DataFrame | None = None,
    rework_activity_analysis: pd.DataFrame | None = None,
    recommendations: pd.DataFrame | None = None,
    delay_cost_estimate: pd.DataFrame | None = None,
) -> None:
    st.markdown("## 🏠 Executive Overview")

    top_bottleneck_value, top_bottleneck_delta = _get_top_bottleneck(
        bottleneck_analysis,
    )
    sla_value, sla_delta = _get_sla_summary(sla_metrics)
    rework_value, rework_delta = _get_rework_summary(rework_case_analysis)
    recommendation_value, recommendation_delta = _get_top_recommendation(
        recommendations,
    )
    delay_value, delay_delta = _get_delay_cost_summary(
        delay_cost_estimate,
        bottleneck_analysis,
    )
    top_rework_activity = _get_top_rework_activity(rework_activity_analysis)

    with module_container(
        title="Management Takeaway",
        subtitle="30-second summary of the Process Intelligence findings.",
        eyebrow="Executive Summary",
    ):
        st.markdown(
            """
            <div class="decision-box">
                The platform identifies <strong>invoice clearing</strong> as the central operational
                delay driver in the Purchase-to-Pay process. SLA breaches and rework signals are not
                random; they concentrate around identifiable process patterns and can be translated into
                prioritized improvement actions.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Purchase-to-Pay Flow Overview",
        subtitle="Simplified business process view enriched with observed operational signals.",
        eyebrow="Process at a Glance",
    ):
        _render_purchase_to_pay_flow(top_rework_activity)

    with module_container(
        title="Top Findings",
        subtitle="Most important business results generated by the platform.",
        eyebrow="Business Impact",
    ):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="⏱️",
                label="Top Bottleneck",
                value=top_bottleneck_value,
                delta=top_bottleneck_delta,
                positive=False,
            )

        with col2:
            render_kpi_card(
                icon="📍",
                label="SLA Risk",
                value=sla_value,
                delta=sla_delta,
                positive=False,
            )

        with col3:
            render_kpi_card(
                icon="🔁",
                label="Rework",
                value=rework_value,
                delta=rework_delta,
                positive=False,
            )

        with col4:
            render_kpi_card(
                icon="💸",
                label="Delay Impact",
                value=delay_value,
                delta=delay_delta,
                positive=False,
            )

        st.markdown(
            f"""
            <div class="decision-box">
                <strong>Recommended management action:</strong><br>
                Start with <strong>{recommendation_value}</strong>.
                This recommendation is supported by bottleneck, SLA and rework signals.
                Current recommendation type: <strong>{recommendation_delta}</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with module_container(
        title="Platform Value Proposition",
        subtitle="What the platform does from a business perspective.",
        eyebrow="Process Intelligence Scope",
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                **Detect**

                Identify bottlenecks, rework loops, SLA breaches and process deviations from event data.
                """
            )

        with col2:
            st.markdown(
                """
                **Explain**

                Connect process delays to root causes, activity patterns, vendors and operational variants.
                """
            )

        with col3:
            st.markdown(
                """
                **Prioritize**

                Translate findings into recommendations and operational follow-up actions.
                """
            )

    with module_container(
        title="Operational Baseline",
        subtitle="Dataset and KPI context used for the analysis.",
        eyebrow="Data Foundation",
    ):
        total_events = len(event_log) if event_log is not None else 0
        raw_case_count = len(raw_cases) if raw_cases is not None else 0
        operational_case_count = len(operational_cases) if operational_cases is not None else 0

        median_cycle_time = (
            operational_cases["cycle_time_days"].median()
            if operational_cases is not None
            and not operational_cases.empty
            and "cycle_time_days" in operational_cases.columns
            else 0
        )

        avg_cycle_time = (
            operational_cases["cycle_time_days"].mean()
            if operational_cases is not None
            and not operational_cases.empty
            and "cycle_time_days" in operational_cases.columns
            else 0
        )

        activity_count = (
            event_log["activity"].nunique()
            if event_log is not None
            and not event_log.empty
            and "activity" in event_log.columns
            else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_kpi_card(
                icon="🧾",
                label="Events",
                value=f"{total_events:,}",
                delta="event records",
                positive=True,
            )

        with col2:
            render_kpi_card(
                icon="📦",
                label="Operational Cases",
                value=f"{operational_case_count:,}",
                delta=f"{raw_case_count:,} raw cases",
                positive=True,
            )

        with col3:
            render_kpi_card(
                icon="🔀",
                label="Activities",
                value=f"{activity_count:,}",
                delta="unique process steps",
                positive=True,
            )

        with col4:
            render_kpi_card(
                icon="📈",
                label="Avg Cycle Time",
                value=f"{avg_cycle_time:.1f} d",
                delta=f"median {median_cycle_time:.1f} d",
                positive=True,
            )

    render_quality_status_banner()

    with module_container(
        title="Data Quality Governance",
        subtitle="Quality checks used to separate operational KPI reporting from exception analysis.",
        eyebrow="Governance",
    ):
        if data_quality_report is not None and not data_quality_report.empty:
            st.dataframe(
                styled_dataframe(data_quality_report),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Data quality report is not available.")

    with module_container(
        title="Analysis Modules",
        subtitle="Functional building blocks of the Process Intelligence platform.",
        eyebrow="Platform Capabilities",
    ):
        render_module_preview_grid()