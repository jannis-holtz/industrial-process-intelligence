from pathlib import Path

import pandas as pd
import pm4py


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_XES_PATH = PROJECT_ROOT / "data" / "raw" / "bpi_challenge_2019.xes"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "event_log.parquet"


COLUMN_MAPPING = {
    "case:concept:name": "case_id",
    "concept:name": "activity",
    "time:timestamp": "timestamp",
    "org:resource": "resource",
    "User": "user",
    "Cumulative net worth (EUR)": "cumulative_net_worth_eur",
    "case:Company": "company",
    "case:Document Type": "document_type",
    "case:Purchasing Document": "purchasing_document",
    "case:Vendor": "vendor",
    "case:Item Type": "item_type",
    "case:Item Category": "item_category",
    "case:Spend area text": "spend_area",
    "case:Sub spend area text": "sub_spend_area",
    "case:Spend classification text": "spend_classification",
    "case:Source": "source",
    "case:GR-Based Inv. Verif.": "gr_based_invoice_verification",
    "case:Goods Receipt": "goods_receipt",
    "case:Item": "item",
}


def convert_xes_to_parquet() -> None:
    if not RAW_XES_PATH.exists():
        raise FileNotFoundError(
            f"Raw XES file not found: {RAW_XES_PATH}\n"
            "Expected file: data/raw/bpi_challenge_2019.xes"
        )

    print(f"Loading XES file: {RAW_XES_PATH}")
    event_log = pm4py.read_xes(str(RAW_XES_PATH))

    print("Converting XES event log to dataframe...")
    df = pm4py.convert_to_dataframe(event_log)

    print("Standardizing column names...")
    available_mapping = {
        source_column: target_column
        for source_column, target_column in COLUMN_MAPPING.items()
        if source_column in df.columns
    }

    df = df.rename(columns=available_mapping)

    required_columns = ["case_id", "activity", "timestamp", "resource"]
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns after mapping: {missing_columns}")

    selected_columns = [
        "case_id",
        "activity",
        "timestamp",
        "resource",
        "user",
        "cumulative_net_worth_eur",
        "company",
        "document_type",
        "purchasing_document",
        "vendor",
        "item_type",
        "item_category",
        "spend_area",
        "sub_spend_area",
        "spend_classification",
        "source",
        "gr_based_invoice_verification",
        "goods_receipt",
        "item",
    ]

    selected_columns = [column for column in selected_columns if column in df.columns]
    df = df[selected_columns].copy()

    print("Cleaning timestamps and sorting event log...")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    if df["timestamp"].isna().any():
        invalid_rows = int(df["timestamp"].isna().sum())
        raise ValueError(f"Timestamp conversion failed for {invalid_rows} rows.")

    df = df.sort_values(["case_id", "timestamp", "activity"]).reset_index(drop=True)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving processed event log to: {PROCESSED_PATH}")
    df.to_parquet(PROCESSED_PATH, index=False)

    print("\nConversion completed.")
    print(f"Rows: {len(df):,}")
    print(f"Cases: {df['case_id'].nunique():,}")
    print(f"Activities: {df['activity'].nunique():,}")
    print(f"Timestamp min: {df['timestamp'].min()}")
    print(f"Timestamp max: {df['timestamp'].max()}")
    print(f"Output file: {PROCESSED_PATH}")


if __name__ == "__main__":
    convert_xes_to_parquet()