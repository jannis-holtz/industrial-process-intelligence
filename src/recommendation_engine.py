import pandas as pd


def generate_bottleneck_recommendations(bottlenecks: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    if bottlenecks.empty:
        return pd.DataFrame(columns=["priority", "recommendation", "business_rationale"])

    top_bottlenecks = bottlenecks.head(top_n).copy()
    recommendations = []

    for priority, row in enumerate(top_bottlenecks.itertuples(index=False), start=1):
        recommendations.append(
            {
                "priority": priority,
                "recommendation": f"Prioritize process transition: {row.transition}",
                "business_rationale": (
                    f"This transition has an average waiting time of "
                    f"{row.average_waiting_time_days:.2f} days across "
                    f"{row.transition_count} observed occurrences."
                ),
            }
        )

    return pd.DataFrame(recommendations)
