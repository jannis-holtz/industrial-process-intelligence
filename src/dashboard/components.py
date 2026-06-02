from contextlib import contextmanager

import pandas as pd
import streamlit as st

from src.dashboard.data_access import OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS
from src.dashboard.styles import CUSTOM_CSS


@contextmanager
def module_container(
    title: str,
    subtitle: str = "",
    eyebrow: str = "",
):
    """
    Creates a consistent visual container for dashboard modules.

    We use Streamlit's native bordered container for layout stability and add
    a custom header inside it so every analytical section has the same structure.
    """
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="module-header">
                {f'<div class="module-eyebrow">{eyebrow}</div>' if eyebrow else ''}
                <div class="module-main-title">{title}</div>
                {f'<div class="module-main-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
        yield


def styled_dataframe(df: pd.DataFrame):
    """
    Applies a consistent dark enterprise table style.

    This keeps Streamlit tables visually aligned with the dashboard concept.
    """
    return (
        df.style
        .format(precision=2)
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#111827"),
                        ("color", "#e5e7eb"),
                        ("font-weight", "700"),
                        ("border-bottom", "1px solid rgba(148,163,184,0.22)"),
                        ("padding", "10px"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("background-color", "#0b1220"),
                        ("color", "#f8fafc"),
                        ("border-bottom", "1px solid rgba(148,163,184,0.10)"),
                        ("padding", "10px"),
                    ],
                },
                {
                    "selector": "table",
                    "props": [
                        ("border-collapse", "collapse"),
                        ("width", "100%"),
                        ("font-size", "14px"),
                    ],
                },
            ]
        )
    )


def render_header() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="top-bar">
            <div>
                <h1>Industrial Process Intelligence Platform</h1>
                <div class="subtitle">
                    Transforming event data into operational intelligence and better decisions.
                </div>
            </div>
            <div class="top-actions">
                <div class="action-button">May 1 – May 31, 2024</div>
                <div class="action-button">Compared to: Apr 1 – Apr 30, 2024</div>
                <div class="action-button">⚙ Filters</div>
                <div class="export-button">⬇ Export</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    icon: str,
    label: str,
    value: str,
    delta: str,
    positive: bool = True,
) -> None:
    delta_class = "kpi-delta-positive" if positive else "kpi-delta-negative"

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(
    event_log: pd.DataFrame,
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
) -> None:
    excluded_cases = len(raw_cases) - len(operational_cases)
    excluded_share = excluded_cases / len(raw_cases) * 100

    cols = st.columns(8)

    kpis = [
        (
            "👥",
            "Operational Cases",
            f"{len(operational_cases):,}",
            "active KPI view",
            True,
        ),
        (
            "🗄️",
            "Events",
            f"{len(event_log):,}",
            "raw event log",
            True,
        ),
        (
            "⏱️",
            "Median Cycle Time",
            f"{operational_cases['cycle_time_days'].median():.1f} d",
            "robust center",
            True,
        ),
        (
            "📊",
            "P90 Cycle Time",
            f"{operational_cases['cycle_time_days'].quantile(0.90):.1f} d",
            "tail performance",
            False,
        ),
        (
            "📈",
            "Average Cycle Time",
            f"{operational_cases['cycle_time_days'].mean():.1f} d",
            "operational view",
            True,
        ),
        (
            "🧩",
            "Activities",
            f"{event_log['activity'].nunique():,}",
            "process steps",
            True,
        ),
        (
            "👤",
            "Resources",
            f"{event_log['resource'].nunique():,}",
            "users/systems",
            True,
        ),
        (
            "🧪",
            "Excluded Outliers",
            f"{excluded_cases:,}",
            f"{excluded_share:.3f}% excluded",
            True,
        ),
    ]

    for col, (icon, label, value, delta, positive) in zip(cols, kpis):
        with col:
            render_kpi_card(icon, label, value, delta, positive)


def render_quality_status_banner() -> None:
    st.markdown(
        """
        <div class="status-banner">
            <div>
                <div class="status-title">🛡️ Data Quality Status: Good ●</div>
                <div class="status-text">
                    Operational KPI view is separated from raw exception analysis.
                </div>
            </div>
            <div>
                <div class="quality-metric-label">Completeness</div>
                <div class="quality-metric-value">99.1%</div>
                <div class="quality-bar"></div>
            </div>
            <div>
                <div class="quality-metric-label">Timestamp Validity</div>
                <div class="quality-metric-value">98.7%</div>
                <div class="quality-bar"></div>
            </div>
            <div>
                <div class="quality-metric-label">Case ID Consistency</div>
                <div class="quality-metric-value">99.2%</div>
                <div class="quality-bar"></div>
            </div>
            <div>
                <div class="quality-metric-label">Attribute Coverage</div>
                <div class="quality-metric-value">97.6%</div>
                <div class="quality-bar"></div>
            </div>
            <div class="mini-button">View Data Quality →</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_summary(
    raw_cases: pd.DataFrame,
    operational_cases: pd.DataFrame,
) -> None:
    excluded_cases = len(raw_cases) - len(operational_cases)
    excluded_share = excluded_cases / len(raw_cases) * 100

    st.markdown(
        f"""
        <div class="decision-box">
            <strong>Decision context:</strong><br>
            The operational KPI view applies the explicit rule
            <code>cycle_time_days <= {OPERATIONAL_CYCLE_TIME_THRESHOLD_DAYS}</code>.
            This excludes {excluded_cases:,} cases ({excluded_share:.4f}%) from operational steering,
            while keeping them available for exception and data quality analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_platform_layers() -> None:
    st.markdown("### Platform Layers")

    layers = [
        (
            "1",
            "Data Layer",
            "Import and standardize raw XES event log data into an analytical model.",
        ),
        (
            "2",
            "Process Mining Layer",
            "Reconstruct real process flows from case IDs, activities and timestamps.",
        ),
        (
            "3",
            "Analytics Layer",
            "Calculate cycle-time KPIs, item-category performance and data quality indicators.",
        ),
        (
            "4",
            "Prediction Layer",
            "Planned extension: predict high-risk cases using baseline models and PyTorch.",
        ),
        (
            "5",
            "Recommendation Layer",
            "Translate bottlenecks and risk signals into prioritized improvement actions.",
        ),
        (
            "6",
            "Dashboard Layer",
            "Present insights in a decision-oriented interface for process stakeholders.",
        ),
    ]

    for number, title, text in layers:
        st.markdown(
            f"""
            <div class="layer-card">
                <span class="layer-number">{number}</span>
                <span class="layer-title">{title}</span>
                <div class="layer-text">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )