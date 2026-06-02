import pandas as pd

from src.kpi_engine import calculate_kpis


def test_calculate_kpis_returns_expected_case_count():
    df = pd.DataFrame(
        {
            "case_id": ["A", "A", "B", "B"],
            "activity": ["Start", "End", "Start", "End"],
            "timestamp": pd.to_datetime(
                ["2025-01-01", "2025-01-03", "2025-01-01", "2025-01-02"]
            ),
        }
    )

    kpis = calculate_kpis(df)

    assert kpis["number_of_cases"] == 2
    assert kpis["number_of_events"] == 4
    assert kpis["number_of_activities"] == 2
