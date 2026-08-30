"""
pandas_stats.py

Descriptive statistics for the 2024 Facebook Presidential Election ads
dataset, computed using Pandas. This is the Pandas-equivalent of
pure_python_stats.py -- same dataset, same questions, different tool.

Usage:
    python pandas_stats.py path/to/fb_ads_president_scored_anon.csv
"""

import sys
import ast
import re
import pandas as pd

DEFAULT_PATH = "fb_ads_president_scored_anon.csv"

RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")

# Columns Meta reports as a {'lower_bound': X, 'upper_bound': Y} range
# rather than a single number. We convert these to numeric midpoints so
# they can be described like any other numeric column -- the same
# decision made explicitly in pure_python_stats.py.
RANGE_COLUMNS = ["estimated_audience_size", "impressions", "spend"]

# Columns that hold a Python-literal list of tags (candidate mentions,
# ad platforms) rather than a single scalar value.
LIST_COLUMNS = ["publisher_platforms", "illuminating_mentions"]


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

    # The 0/1 "illuminating_*" flag columns arrive as strings; coerce the
    # true numeric columns (everything except the range columns already
    # handled, and the list/text columns) to numeric where possible.
    for col in df.columns:
        if col in RANGE_COLUMNS or col in LIST_COLUMNS:
            continue
        coerced = pd.to_numeric(df[col], errors="coerce")
        # Only adopt the numeric dtype if almost every non-null value
        # actually converted -- otherwise keep it as text/categorical.
        non_null = df[col].notna().sum()
        if non_null > 0 and coerced.notna().sum() / non_null >= 0.9:
            df[col] = coerced

    return df


def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    print(f"Loading: {path}\n")
    df = load(path)

    print("=" * 78)
    print("PANDAS DESCRIPTIVE STATISTICS")
    print("2024 Facebook Presidential Election Ads Dataset")
    print("=" * 78)

    section("BASIC STRUCTURE")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("\nColumn dtypes:")
    print(df.dtypes)

    section("DATAFRAME.INFO()")
    df.info()

    section("MISSING VALUES PER COLUMN")
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    missing_report = pd.DataFrame({"missing_count": missing_count,
                                    "missing_pct": missing_pct})
    print(missing_report)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns
                         if c not in numeric_cols and c not in LIST_COLUMNS]

    section(f"DESCRIBE() -- NUMERIC COLUMNS ({len(numeric_cols)})")
    with pd.option_context("display.max_columns", None, "display.width", 160):
        print(df[numeric_cols].describe().T)
        # describe() gives count/mean/std/min/25%/50%/75%/max; median is
        # the 50% row, included here explicitly for a direct comparison
        # against pure_python_stats.py's median field.
        print("\nMedian (== 50th percentile above), shown separately for clarity:")
        print(df[numeric_cols].median())

    section(f"DESCRIBE() -- NON-NUMERIC / CATEGORICAL COLUMNS "
            f"({len(non_numeric_cols)})")
    with pd.option_context("display.max_columns", None, "display.width", 160):
        print(df[non_numeric_cols].describe().T)

    section("CATEGORICAL COLUMNS: nunique() and top value_counts()")
    for col in non_numeric_cols:
        vc = df[col].value_counts().head(5)
        print(f"\n[{col}]  nunique = {df[col].nunique():,}")
        print(vc.to_string())

    section("LIST-VALUED COLUMNS (exploded item frequency)")
    for col in LIST_COLUMNS:
        if col not in df.columns:
            continue
        parsed = df[col].dropna().apply(
            lambda s: ast.literal_eval(s) if isinstance(s, str) and
            s.strip().startswith("[") else []
        )
        exploded = parsed.explode()
        counts = exploded.value_counts()
        print(f"\n[{col}]  unique items = {counts.shape[0]:,}")
        print(counts.head(5).to_string())

    section("CROSS-CHECK: PANDAS vs PURE PYTHON (numeric columns)")
    print("count / mean / min / max / std / median for each numeric column,")
    print("for direct comparison against pure_python_stats.py output:\n")
    for col in numeric_cols:
        s = df[col]
        print(f"[{col}]")
        print(f"  count={s.count():,}  mean={s.mean():.4f}  "
              f"min={s.min():.4f}  max={s.max():.4f}  "
              f"std={s.std():.4f}  median={s.median():.4f}")

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
