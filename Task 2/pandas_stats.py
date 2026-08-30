"""
pandas_stats.py  (Task 2 / Milestone A)

Descriptive statistics AND grouped analysis using Pandas.
Equivalent to pure_python_stats.py -- same dataset, same questions.

Usage:
    python pandas_stats.py path/to/data.csv
"""

import sys
import ast
import re
import pandas as pd

DEFAULT_PATH = "fb_ads_president_scored_anon.csv"
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")
RANGE_COLUMNS = ["estimated_audience_size", "impressions", "spend"]
LIST_COLUMNS = ["publisher_platforms", "illuminating_mentions"]
GROUP_KEY_SETS = [["page_id"], ["page_id", "ad_id"]]


def range_to_midpoint(raw):
    if pd.isna(raw) or not RANGE_DICT_RE.match(str(raw)):
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
    df = pd.read_csv(path, dtype=str, keep_default_na=True)

    for col in RANGE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(range_to_midpoint)

    for col in df.columns:
        if col in RANGE_COLUMNS or col in LIST_COLUMNS:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        non_null = df[col].notna().sum()
        if non_null > 0 and coerced.notna().sum() / non_null >= 0.9:
            df[col] = coerced

    return df


def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def run_grouped_analysis(df, key_cols, top_n=10):
    section(f"GROUPED BY {key_cols}")
    grouped = df.groupby(key_cols, dropna=False)
    print(f"Number of groups: {grouped.ngroups:,}")

    agg = grouped.agg(
        row_count=("page_id", "size"),
        spend_sum=("spend", "sum"),
        spend_mean=("spend", "mean"),
        impressions_mean=("impressions", "mean"),
    ).reset_index()

    top = agg.sort_values("spend_sum", ascending=False).head(top_n)
    print(f"\nTop {top_n} groups by total spend:")
    print(top.to_string(index=False))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    print(f"Loading: {path}\n")
    df = load(path)

    print("=" * 78)
    print("PANDAS DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
    print("=" * 78)

    section("BASIC STRUCTURE")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("\nColumn dtypes:")
    print(df.dtypes)

    section("MISSING VALUES PER COLUMN")
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    print(pd.DataFrame({"missing_count": missing_count,
                         "missing_pct": missing_pct}))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns
                         if c not in numeric_cols and c not in LIST_COLUMNS]

    section(f"DESCRIBE() -- NUMERIC COLUMNS ({len(numeric_cols)})")
    with pd.option_context("display.max_columns", None, "display.width", 160):
        print(df[numeric_cols].describe().T)

    section(f"DESCRIBE() -- NON-NUMERIC COLUMNS ({len(non_numeric_cols)})")
    with pd.option_context("display.max_columns", None, "display.width", 160):
        print(df[non_numeric_cols].describe().T)

    section("CATEGORICAL COLUMNS: nunique() / value_counts()")
    for col in non_numeric_cols:
        print(f"\n[{col}]  nunique = {df[col].nunique():,}")
        print(df[col].value_counts().head(5).to_string())

    section("LIST-VALUED COLUMNS (exploded item frequency)")
    for col in LIST_COLUMNS:
        if col not in df.columns:
            continue
        parsed = df[col].dropna().apply(
            lambda s: ast.literal_eval(s) if isinstance(s, str) and
            s.strip().startswith("[") else []
        )
        counts = parsed.explode().value_counts()
        print(f"\n[{col}]  unique items = {counts.shape[0]:,}")
        print(counts.head(5).to_string())

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
