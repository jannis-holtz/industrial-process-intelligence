import pandas as pd


def extract_variants(df: pd.DataFrame) -> pd.DataFrame:
    variants = (
        df.sort_values(["case_id", "timestamp"])
        .groupby("case_id")["activity"]
        .apply(lambda activities: " → ".join(activities))
        .reset_index(name="variant")
    )

    variant_summary = (
        variants.groupby("variant")
        .agg(case_count=("case_id", "count"))
        .reset_index()
        .sort_values("case_count", ascending=False)
    )

    variant_summary["variant_rank"] = range(1, len(variant_summary) + 1)

    return variant_summary
