import pandas as pd


REQUIRED_COLUMNS = ["case_id", "activity", "timestamp"]


def validate_event_log(df: pd.DataFrame) -> None:
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required event log columns: {missing_columns}")


def prepare_event_log(df: pd.DataFrame) -> pd.DataFrame:
    validate_event_log(df)

    processed = df.copy()
    processed["timestamp"] = pd.to_datetime(processed["timestamp"], errors="coerce")

    if processed["timestamp"].isna().any():
        raise ValueError("Timestamp conversion failed for at least one row.")

    processed = processed.sort_values(["case_id", "timestamp"]).reset_index(drop=True)

    return processed
