from pathlib import Path

import pandas as pd


def load_event_log_csv(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Event log file not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("Expected a CSV file. Use a dedicated XES loader for .xes files.")

    return pd.read_csv(path)
