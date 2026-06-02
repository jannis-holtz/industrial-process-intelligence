import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.styles import PLOTLY_TEMPLATE


def create_cycle_time_distribution_chart(operational_cases: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        operational_cases,
        x="cycle_time_days",
        nbins=70,
        template=PLOTLY_TEMPLATE,
        labels={"cycle_time_days": "Cycle Time in Days"},
    )

    fig.update_traces(
        marker_color="#38bdf8",
        marker_line_color="#0f172a",
        marker_line_width=0.5,
        opacity=0.85,
    )

    fig.update_layout(
        title="Operational Cycle Time Distribution",
        yaxis_title="Number of Cases",
        xaxis_title="Cycle Time in Days",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        margin=dict(l=20, r=20, t=55, b=35),
        height=360,
    )

    return fig


def create_item_category_chart(operational_cases: pd.DataFrame) -> go.Figure:
    item_category_summary = (
        operational_cases.groupby("item_category")
        .agg(median_cycle_time_days=("cycle_time_days", "median"))
        .reset_index()
        .sort_values("median_cycle_time_days", ascending=False)
    )

    fig = px.bar(
        item_category_summary,
        x="item_category",
        y="median_cycle_time_days",
        template=PLOTLY_TEMPLATE,
        labels={
            "item_category": "Item Category",
            "median_cycle_time_days": "Median Cycle Time in Days",
        },
    )

    fig.update_traces(marker_color="#14b8a6")

    fig.update_layout(
        title="Median Cycle Time by Item Category",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        margin=dict(l=20, r=20, t=55, b=80),
        height=360,
    )

    return fig


def create_top_activities_chart(event_log: pd.DataFrame) -> go.Figure:
    top_activities = event_log["activity"].value_counts().head(10).reset_index()
    top_activities.columns = ["activity", "event_count"]

    fig = px.bar(
        top_activities,
        x="event_count",
        y="activity",
        orientation="h",
        template=PLOTLY_TEMPLATE,
        labels={
            "event_count": "Number of Events",
            "activity": "Activity",
        },
    )

    fig.update_traces(marker_color="#60a5fa")

    fig.update_layout(
        title="Top Activities by Event Count",
        yaxis={"categoryorder": "total ascending"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        margin=dict(l=20, r=20, t=55, b=35),
        height=420,
    )

    return fig