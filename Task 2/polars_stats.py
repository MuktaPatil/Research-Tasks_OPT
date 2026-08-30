"""
polars_stats.py  (Task 2 / Milestone A)

Descriptive statistics AND grouped analysis using Polars.
Equivalent to pure_python_stats.py / pandas_stats.py.

NOTE: Polars was not installable in the sandbox this was authored in
(no network access), so this script is written carefully against the
documented Polars API but has NOT been executed here. Run it locally
and diff its numeric output against pandas_output.txt /
pure_python_output.txt before trusting it for submission.

Usage:
    python polars_stats.py path/to/data.csv
"""

import sys
import ast
import re
import polars as pl

DEFAULT_PATH = "fb_ads_president_scored_anon.csv"
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")
RANGE_COLUMNS = ["estimated_audience_size", "impressions", "spend"]
LIST_COLUMNS = ["publisher_platforms", "illuminating_mentions"]
GROUP_KEY_SETS = [["page_id"], ["page_id", "ad_id"]]


def range_to_midpoint(raw):
    """Python-side helper used inside a Polars `map_elements` call to
    convert Meta's {'lower_bound': X, 'upper_bound': Y} range strings
    into a single float midpoint (or the lower bound for the open-ended
    top bucket). Returns None for missing/non-matching values."""
    if raw is None or not RANGE_DICT_RE.match(str(raw)):
        return None
    try:
        d = ast.literal_eval(raw)
        lo = float(d["lower_bound"])
        if "upper_bound" in d:
            return (lo + float(d["upper_bound"])) / 2.0
        return lo
    except (ValueError, SyntaxError, KeyError, TypeError):
        return None


def load(path):
    # Read everything as strings first (Utf8) -- Polars' own type
    # inference has no idea what a lower/upper-bound dict is, so we do
    # our own casting pass below, same as the Pandas script.
    df = pl.read_csv(path, infer_schema_length=0)

    for col in RANGE_COLUMNS:
        if col in df.columns:
            df = df.with_columns(
                pl.col(col)
                .map_elements(range_to_midpoint, return_dtype=pl.Float64)
                .alias(col)
            )

    # Try casting every other column to Float64; keep the cast only if
    # at least 90% of non-null values converted successfully -- mirrors
    # the threshold used in the other two scripts.
    for col in df.columns:
        if col in RANGE_COLUMNS or col in LIST_COLUMNS:
            continue
        casted = df[col].cast(pl.Float64, strict=False)
        non_null = df[col].drop_nulls().len()
        if non_null > 0 and casted.drop_nulls().len() / non_null >= 0.9:
            df = df.with_columns(casted.alias(col))

    return df


def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def numeric_and_categorical_columns(df):
    numeric_cols = [c for c, dt in zip(df.columns, df.dtypes)
                    if dt in (pl.Float64, pl.Int64)]
    categorical_cols = [c for c in df.columns
                         if c not in numeric_cols and c not in LIST_COLUMNS]
    return numeric_cols, categorical_cols


def run_grouped_analysis(df, key_cols, top_n=10):
    section(f"GROUPED BY {key_cols}")
    grouped = (
        df.group_by(key_cols)
        .agg([
            pl.len().alias("row_count"),
            pl.col("spend").sum().alias("spend_sum"),
            pl.col("spend").mean().alias("spend_mean"),
            pl.col("impressions").mean().alias("impressions_mean"),
        ])
    )
    print(f"Number of groups: {grouped.height:,}")
    top = grouped.sort("spend_sum", descending=True).head(top_n)
    print(f"\nTop {top_n} groups by total spend:")
    print(top)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    print(f"Loading: {path}\n")
    df = load(path)

    print("=" * 78)
    print("POLARS DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
    print("=" * 78)

    section("BASIC STRUCTURE")
    print(f"Shape: {df.height:,} rows x {df.width} columns")
    print("\nColumn dtypes:")
    for c, dt in zip(df.columns, df.dtypes):
        print(f"  {c:<40} {dt}")

    section("MISSING / NULL VALUES PER COLUMN")
    null_counts = df.null_count()
    for col in df.columns:
        n_missing = null_counts[col][0]
        pct = (n_missing / df.height * 100) if df.height else 0
        print(f"  {col:<40} {n_missing:>8,} missing ({pct:5.1f}%)")

    numeric_cols, categorical_cols = numeric_and_categorical_columns(df)

    section(f"DESCRIBE() -- NUMERIC COLUMNS ({len(numeric_cols)})")
    print(df.select(numeric_cols).describe())

    section("MEDIAN -- NUMERIC COLUMNS (describe() reports the 50th "
            "percentile as 'median' too; shown separately for parity "
            "with the other two scripts)")
    for col in numeric_cols:
        print(f"  {col:<40} median = {df[col].median()}")

    section(f"CATEGORICAL COLUMNS: n_unique() / value_counts() "
            f"({len(categorical_cols)})")
    for col in categorical_cols:
        print(f"\n[{col}]  n_unique = {df[col].n_unique():,}")
        vc = df[col].value_counts().sort("count", descending=True).head(5)
        print(vc)

    section("LIST-VALUED COLUMNS (exploded item frequency)")
    for col in LIST_COLUMNS:
        if col not in df.columns:
            continue
        parsed = df[col].drop_nulls().map_elements(
            lambda s: ast.literal_eval(s) if isinstance(s, str) and
            s.strip().startswith("[") else [],
            return_dtype=pl.List(pl.Utf8),
        )
        exploded = parsed.explode()
        counts = exploded.value_counts().sort("count", descending=True)
        print(f"\n[{col}]  unique items = {counts.height:,}")
        print(counts.head(5))

    print("\n" + "=" * 78)
    print("GROUPED ANALYSIS")
    print("=" * 78)
    for key_cols in GROUP_KEY_SETS:
        run_grouped_analysis(df, key_cols)

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
