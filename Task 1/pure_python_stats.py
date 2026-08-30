"""
pure_python_stats.py

Descriptive statistics for the 2024 Facebook Presidential Election ads
dataset, computed using ONLY the Python standard library (csv, math,
collections, statistics, re, ast). No Pandas, no NumPy.

Usage:
    python pure_python_stats.py path/to/fb_ads_president_scored_anon.csv

If no path is given, it defaults to ./fb_ads_president_scored_anon.csv
"""

import csv
import sys
import math
import ast
import re
from collections import Counter, defaultdict

DEFAULT_PATH = "fb_ads_president_scored_anon.csv"

# Treated as missing/null when found in a raw cell.
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}

# Matches strings like: {'lower_bound': '200', 'upper_bound': '299'}
# or the open-ended top bucket Meta reports as just {'lower_bound': '1000001'}
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")


# --------------------------------------------------------------------------
# Value parsing helpers
# --------------------------------------------------------------------------

def is_missing(raw):
    return raw is None or raw.strip().lower() in MISSING_TOKENS


def try_parse_range_dict(raw):
    """Meta's ad-transparency API reports spend/impressions/audience size
    as a {'lower_bound': X, 'upper_bound': Y} range rather than a single
    number, to protect advertiser/user privacy. We convert each range to
    its numeric midpoint so the column can be treated as numeric. This is
    a deliberate, documented modeling choice, not a hidden Pandas default.
    Returns a float midpoint, or None if the string isn't a range dict.
    """
    if not RANGE_DICT_RE.match(raw):
        return None
    try:
        d = ast.literal_eval(raw)
        lo = float(d["lower_bound"])
        # Meta's top bucket (e.g. audience size > 1,000,000) is reported
        # with only a lower_bound and no upper_bound. We treat that open
        # top bucket's value as the lower_bound itself rather than
        # guessing an upper limit.
        if "upper_bound" in d:
            hi = float(d["upper_bound"])
            return (lo + hi) / 2.0
        return lo
    except (ValueError, SyntaxError, KeyError, TypeError):
        return None


def try_parse_float(raw):
    """Try to coerce a raw string into a float, stripping common
    formatting noise like '$', ',', and '%'. Returns None on failure."""
    cleaned = raw.strip().replace("$", "").replace(",", "").replace("%", "")
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def try_parse_list(raw):
    """Detect Python-literal list strings, e.g. "['Kamala Harris', 'Tim
    Walz']" or "['facebook', 'instagram']". Returns a list, or None."""
    s = raw.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    try:
        val = ast.literal_eval(s)
        if isinstance(val, list):
            return val
    except (ValueError, SyntaxError):
        pass
    return None


# --------------------------------------------------------------------------
# Column loading
# --------------------------------------------------------------------------

def load_columns(path):
    """Read the CSV once and return (columns, row_count), where `columns`
    is a dict: column_name -> list of raw string values (missing entries
    kept as None so positions/counts stay aligned with the row count)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        columns = {name: [] for name in fieldnames}
        row_count = 0
        for row in reader:
            row_count += 1
            for name in fieldnames:
                raw = row.get(name)
                if raw is None or is_missing(raw):
                    columns[name].append(None)
                else:
                    columns[name].append(raw)
    return columns, row_count, fieldnames


# --------------------------------------------------------------------------
# Type inference
# --------------------------------------------------------------------------

def infer_column_type(values):
    """Look at the non-missing values in a column and decide whether the
    column is best treated as 'numeric', 'range_numeric' (Meta's
    lower/upper-bound dict, converted to a midpoint), 'list' (a
    Python-literal list of tags), or 'categorical' (free text / IDs /
    dates). We require at least 90% of non-missing values to parse
    cleanly as a type before committing to it -- this mirrors the kind
    of threshold Pandas' dtype inference makes for you silently."""
    non_missing = [v for v in values if v is not None]
    n = len(non_missing)
    if n == 0:
        return "empty"

    range_hits = sum(1 for v in non_missing if RANGE_DICT_RE.match(v))
    if range_hits / n >= 0.9:
        return "range_numeric"

    list_hits = sum(1 for v in non_missing if try_parse_list(v) is not None)
    if list_hits / n >= 0.9:
        return "list"

    numeric_hits = sum(1 for v in non_missing if try_parse_float(v) is not None)
    if numeric_hits / n >= 0.9:
        return "numeric"

    return "categorical"


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def compute_numeric_stats(values):
    """values: list of floats (already parsed, no None/NaN).
    Returns a dict of count, mean, min, max, stdev (sample), median.
    Handles the empty-list and single-value edge cases explicitly."""
    n = len(values)
    if n == 0:
        return {"count": 0, "mean": None, "min": None, "max": None,
                "stdev": None, "median": None}

    total = sum(values)
    mean = total / n

    variance_sum = sum((x - mean) ** 2 for x in values)
    # Sample standard deviation (n-1 denominator); undefined for n == 1.
    stdev = math.sqrt(variance_sum / (n - 1)) if n > 1 else 0.0

    sorted_vals = sorted(values)
    mid = n // 2
    if n % 2 == 0:
        median = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
    else:
        median = sorted_vals[mid]

    return {
        "count": n,
        "mean": mean,
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "stdev": stdev,
        "median": median,
    }


def compute_categorical_stats(values, top_n=5):
    """values: list of raw non-missing strings.
    Returns count, nunique, mode (+ its frequency), and top-N by frequency."""
    n = len(values)
    if n == 0:
        return {"count": 0, "nunique": 0, "mode": None, "mode_freq": None,
                "top_values": []}

    counts = Counter(values)
    top = counts.most_common(top_n)
    mode_val, mode_freq = top[0]

    return {
        "count": n,
        "nunique": len(counts),
        "mode": mode_val,
        "mode_freq": mode_freq,
        "top_values": top,
    }


def compute_list_stats(values, top_n=5):
    """values: list of raw strings that parse as Python lists (e.g. tag
    lists like candidate mentions or platforms). We flatten every list
    and treat each individual item as one occurrence for frequency
    counting -- this is different from treating the whole list as one
    categorical value, and is the more useful view for tag-style data."""
    n = len(values)
    flat = []
    for raw in values:
        parsed = try_parse_list(raw)
        if parsed:
            flat.extend(str(item) for item in parsed)

    counts = Counter(flat)
    top = counts.most_common(top_n)
    mode_val, mode_freq = (top[0] if top else (None, None))

    return {
        "count": n,
        "nunique_items": len(counts),
        "mode_item": mode_val,
        "mode_item_freq": mode_freq,
        "top_items": top,
    }


# --------------------------------------------------------------------------
# Report formatting
# --------------------------------------------------------------------------

def fmt(x, decimals=2):
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:,.{decimals}f}"
    return str(x)


def print_report(columns, fieldnames, row_count):
    print("=" * 78)
    print("PURE PYTHON DESCRIPTIVE STATISTICS")
    print("2024 Facebook Presidential Election Ads Dataset")
    print("=" * 78)
    print(f"\nTotal rows:    {row_count:,}")
    print(f"Total columns: {len(fieldnames)}\n")

    print("-" * 78)
    print("MISSING VALUES PER COLUMN")
    print("-" * 78)
    for name in fieldnames:
        missing = sum(1 for v in columns[name] if v is None)
        pct = (missing / row_count * 100) if row_count else 0
        print(f"  {name:<40} {missing:>8,} missing ({pct:5.1f}%)")

    print("\n" + "-" * 78)
    print("PER-COLUMN ANALYSIS")
    print("-" * 78)

    for name in fieldnames:
        raw_values = columns[name]
        non_missing = [v for v in raw_values if v is not None]
        col_type = infer_column_type(raw_values)

        print(f"\n[{name}]")
        print(f"  Inferred type: {col_type}")

        if col_type == "empty":
            print("  All values missing -- no statistics available.")

        elif col_type in ("numeric", "range_numeric"):
            if col_type == "range_numeric":
                parsed = [try_parse_range_dict(v) for v in non_missing]
            else:
                parsed = [try_parse_float(v) for v in non_missing]
            parsed = [p for p in parsed if p is not None]
            stats = compute_numeric_stats(parsed)
            note = " (midpoint of Meta's reported lower/upper bound range)" \
                if col_type == "range_numeric" else ""
            print(f"  Count:  {stats['count']:,}{note}")
            print(f"  Mean:   {fmt(stats['mean'])}")
            print(f"  Min:    {fmt(stats['min'])}")
            print(f"  Max:    {fmt(stats['max'])}")
            print(f"  Stdev:  {fmt(stats['stdev'])}")
            print(f"  Median: {fmt(stats['median'])}")

        elif col_type == "list":
            stats = compute_list_stats(non_missing)
            print(f"  Count (non-null rows): {stats['count']:,}")
            print(f"  Unique items:          {stats['nunique_items']:,}")
            print(f"  Most frequent item:    {stats['mode_item']} "
                  f"({stats['mode_item_freq']:,} occurrences)")
            print("  Top 5 items by frequency:")
            for item, freq in stats["top_items"]:
                print(f"    - {item}: {freq:,}")

        else:  # categorical
            stats = compute_categorical_stats(non_missing)
            print(f"  Count:         {stats['count']:,}")
            print(f"  Unique values: {stats['nunique']:,}")
            print(f"  Mode:          {stats['mode']} "
                  f"({stats['mode_freq']:,} occurrences)")
            print("  Top 5 values by frequency:")
            for val, freq in stats["top_values"]:
                display = val if len(val) <= 60 else val[:57] + "..."
                print(f"    - {display}: {freq:,}")

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    print(f"Loading: {path}\n")
    columns, row_count, fieldnames = load_columns(path)
    print_report(columns, fieldnames, row_count)


if __name__ == "__main__":
    main()
