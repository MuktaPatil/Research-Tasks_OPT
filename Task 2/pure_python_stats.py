"""
pure_python_stats.py  (Task 2 / Milestone A)

Descriptive statistics AND grouped analysis for the Facebook political
ads dataset, using ONLY the Python standard library (csv, math,
collections, ast, re). No Pandas, no Polars.

Extends Task 1's column-level analysis with:
  - grouped-by-page_id statistics
  - grouped-by-(page_id, ad_id) statistics

Usage:
    python pure_python_stats.py path/to/data.csv
"""

import csv
import sys
import math
import ast
import re
from collections import Counter, defaultdict

DEFAULT_PATH = "fb_ads_president_scored_anon.csv"
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")

GROUP_KEYS = [("page_id",), ("page_id", "ad_id")]


# --------------------------------------------------------------------------
# Value parsing helpers (shared logic, same as Task 1)
# --------------------------------------------------------------------------

def is_missing(raw):
    return raw is None or raw.strip().lower() in MISSING_TOKENS


def try_parse_range_dict(raw):
    """Meta reports spend/impressions/audience size as a
    {'lower_bound': X, 'upper_bound': Y} range. We convert to the
    numeric midpoint (or just the lower bound for the open-ended top
    bucket) so the column can be treated as numeric."""
    if not RANGE_DICT_RE.match(raw):
        return None
    try:
        d = ast.literal_eval(raw)
        lo = float(d["lower_bound"])
        if "upper_bound" in d:
            return (lo + float(d["upper_bound"])) / 2.0
        return lo
    except (ValueError, SyntaxError, KeyError, TypeError):
        return None


def try_parse_float(raw):
    cleaned = raw.strip().replace("$", "").replace(",", "").replace("%", "")
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def try_parse_list(raw):
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
# Loading
# --------------------------------------------------------------------------

def load_rows(path):
    """Read the CSV once into a list of dicts (raw strings, missing
    tokens normalized to None) plus the fieldnames, in file order."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = []
        for row in reader:
            clean = {}
            for name in fieldnames:
                raw = row.get(name)
                clean[name] = None if (raw is None or is_missing(raw)) else raw
            rows.append(clean)
    return rows, fieldnames


# --------------------------------------------------------------------------
# Type inference (same thresholded approach as Task 1)
# --------------------------------------------------------------------------

def infer_column_type(values):
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
    n = len(values)
    if n == 0:
        return {"count": 0, "mean": None, "min": None, "max": None,
                "stdev": None, "median": None}
    total = sum(values)
    mean = total / n
    variance_sum = sum((x - mean) ** 2 for x in values)
    stdev = math.sqrt(variance_sum / (n - 1)) if n > 1 else 0.0
    sorted_vals = sorted(values)
    mid = n // 2
    median = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0 if n % 2 == 0 \
        else sorted_vals[mid]
    return {"count": n, "mean": mean, "min": sorted_vals[0],
            "max": sorted_vals[-1], "stdev": stdev, "median": median}


def compute_categorical_stats(values, top_n=5):
    n = len(values)
    if n == 0:
        return {"count": 0, "nunique": 0, "mode": None, "mode_freq": None,
                "top_values": []}
    counts = Counter(values)
    top = counts.most_common(top_n)
    mode_val, mode_freq = top[0]
    return {"count": n, "nunique": len(counts), "mode": mode_val,
            "mode_freq": mode_freq, "top_values": top}


def compute_list_stats(values, top_n=5):
    n = len(values)
    flat = []
    for raw in values:
        parsed = try_parse_list(raw)
        if parsed:
            flat.extend(str(item) for item in parsed)
    counts = Counter(flat)
    top = counts.most_common(top_n)
    mode_val, mode_freq = (top[0] if top else (None, None))
    return {"count": n, "nunique_items": len(counts), "mode_item": mode_val,
            "mode_item_freq": mode_freq, "top_items": top}


def columns_from_rows(rows, fieldnames):
    """Pivot a list-of-dicts into dict: column_name -> list of values."""
    columns = {name: [] for name in fieldnames}
    for row in rows:
        for name in fieldnames:
            columns[name].append(row[name])
    return columns


def analyze_columns(columns, fieldnames):
    """Returns a dict: column_name -> (col_type, stats_dict)."""
    results = {}
    for name in fieldnames:
        raw_values = columns[name]
        non_missing = [v for v in raw_values if v is not None]
        col_type = infer_column_type(raw_values)

        if col_type == "empty":
            results[name] = (col_type, {})
        elif col_type in ("numeric", "range_numeric"):
            if col_type == "range_numeric":
                parsed = [try_parse_range_dict(v) for v in non_missing]
            else:
                parsed = [try_parse_float(v) for v in non_missing]
            parsed = [p for p in parsed if p is not None]
            results[name] = (col_type, compute_numeric_stats(parsed))
        elif col_type == "list":
            results[name] = (col_type, compute_list_stats(non_missing))
        else:
            results[name] = (col_type, compute_categorical_stats(non_missing))
    return results


# --------------------------------------------------------------------------
# Grouped analysis
# --------------------------------------------------------------------------

def group_rows(rows, key_cols):
    """Organize rows into a dict keyed by a tuple of the grouping
    column(s) -- exactly what Pandas' groupby()/Polars' group_by() do
    internally, made explicit."""
    groups = defaultdict(list)
    for row in rows:
        key = tuple(row.get(k) for k in key_cols)
        groups[key].append(row)
    return groups


def summarize_group(group_rows_list, fieldnames):
    """For one group's rows, compute a compact summary: row count, plus
    numeric-column means/sums for the key numeric fields. We keep this
    focused (not a full per-column breakdown) since a group can be as
    small as a single row."""
    numeric_targets = ["spend", "impressions", "estimated_audience_size"]
    summary = {"row_count": len(group_rows_list)}
    for col in numeric_targets:
        parsed = []
        for row in group_rows_list:
            raw = row.get(col)
            if raw is None:
                continue
            val = try_parse_range_dict(raw) if RANGE_DICT_RE.match(raw) else \
                try_parse_float(raw)
            if val is not None:
                parsed.append(val)
        stats = compute_numeric_stats(parsed)
        summary[f"{col}_sum"] = sum(parsed) if parsed else None
        summary[f"{col}_mean"] = stats["mean"]
    return summary


def run_grouped_analysis(rows, fieldnames, key_cols, top_n=10):
    groups = group_rows(rows, key_cols)
    summaries = []
    for key, grp_rows in groups.items():
        summary = summarize_group(grp_rows, fieldnames)
        summary["key"] = key
        summaries.append(summary)

    # Sort by total spend (descending) to surface the biggest groups.
    summaries.sort(key=lambda s: (s["spend_sum"] or 0), reverse=True)

    print(f"\nGrouped by {key_cols}: {len(groups):,} groups total")
    print(f"Top {top_n} groups by total spend:\n")
    header = " | ".join(key_cols) + " | rows | spend_sum | spend_mean | impressions_mean"
    print(header)
    print("-" * len(header))
    for s in summaries[:top_n]:
        key_str = " | ".join(str(k) for k in s["key"])
        print(f"{key_str} | {s['row_count']:,} | "
              f"{fmt(s['spend_sum'])} | {fmt(s['spend_mean'])} | "
              f"{fmt(s['impressions_mean'])}")

    return summaries


# --------------------------------------------------------------------------
# Formatting / report
# --------------------------------------------------------------------------

def fmt(x, decimals=2):
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:,.{decimals}f}"
    return str(x)


def print_column_report(results, fieldnames, row_count):
    print("-" * 78)
    print("PER-COLUMN ANALYSIS")
    print("-" * 78)
    for name in fieldnames:
        col_type, stats = results[name]
        print(f"\n[{name}]")
        print(f"  Inferred type: {col_type}")
        if col_type == "empty":
            print("  All values missing -- no statistics available.")
        elif col_type in ("numeric", "range_numeric"):
            note = " (midpoint of Meta's reported range)" \
                if col_type == "range_numeric" else ""
            print(f"  Count:  {stats['count']:,}{note}")
            print(f"  Mean:   {fmt(stats['mean'])}")
            print(f"  Min:    {fmt(stats['min'])}")
            print(f"  Max:    {fmt(stats['max'])}")
            print(f"  Stdev:  {fmt(stats['stdev'])}")
            print(f"  Median: {fmt(stats['median'])}")
        elif col_type == "list":
            print(f"  Count (non-null rows): {stats['count']:,}")
            print(f"  Unique items:          {stats['nunique_items']:,}")
            print(f"  Most frequent item:    {stats['mode_item']} "
                  f"({stats['mode_item_freq']:,})")
            print("  Top 5 items:")
            for item, freq in stats["top_items"]:
                print(f"    - {item}: {freq:,}")
        else:
            print(f"  Count:         {stats['count']:,}")
            print(f"  Unique values: {stats['nunique']:,}")
            print(f"  Mode:          {stats['mode']} ({stats['mode_freq']:,})")
            print("  Top 5 values:")
            for val, freq in stats["top_values"]:
                display = val if len(val) <= 60 else val[:57] + "..."
                print(f"    - {display}: {freq:,}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    print(f"Loading: {path}\n")
    rows, fieldnames = load_rows(path)
    row_count = len(rows)
    columns = columns_from_rows(rows, fieldnames)

    print("=" * 78)
    print("PURE PYTHON DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
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

    results = analyze_columns(columns, fieldnames)
    print()
    print_column_report(results, fieldnames, row_count)

    print("\n" + "=" * 78)
    print("GROUPED ANALYSIS")
    print("=" * 78)
    for key_cols in GROUP_KEYS:
        run_grouped_analysis(rows, fieldnames, key_cols)

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
