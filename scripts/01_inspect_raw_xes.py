from pathlib import Path

import pandas as pd
import pm4py


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "bpi_challenge_2019.xes"


def inspect_xes_event_log(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(
            f"XES file not found: {file_path}\n"
            "Place the BPI Challenge 2019 XES file in data/raw and name it "
            "bpi_challenge_2019.xes"
        )

    print(f"Loading XES event log: {file_path}")
    print("This can take a few minutes because the dataset is large.")

    event_log = pm4py.read_xes(str(file_path))
    df = pm4py.convert_to_dataframe(event_log)

    print("\n=== Shape ===")
    print(df.shape)

    print("\n=== Columns ===")
    for column in df.columns:
        print(column)

    print("\n=== Data types ===")
    print(df.dtypes)

    print("\n=== Missing values top 20 ===")
    print(df.isna().sum().sort_values(ascending=False).head(20))

    print("\n=== First rows ===")
    print(df.head())

    print("\n=== Core event log columns check ===")
    expected_columns = [
        "case:concept:name",
        "concept:name",
        "time:timestamp",
        "org:resource",
    ]

    for column in expected_columns:
        status = "FOUND" if column in df.columns else "MISSING"
        print(f"{column}: {status}")

    print("\n=== Basic process stats ===")

    if "case:concept:name" in df.columns:
        print(f"Cases: {df['case:concept:name'].nunique():,}")

    if "concept:name" in df.columns:
        print(f"Activities: {df['concept:name'].nunique():,}")
        print("\nTop 10 activities:")
        print(df["concept:name"].value_counts().head(10))

    if "org:resource" in df.columns:
        print(f"\nResources: {df['org:resource'].nunique():,}")
        print("\nTop 10 resources:")
        print(df["org:resource"].value_counts().head(10))

    if "time:timestamp" in df.columns:
        print("\nTimestamp range:")
        print(df["time:timestamp"].min())
        print(df["time:timestamp"].max())


if __name__ == "__main__":
    inspect_xes_event_log(RAW_DATA_PATH)