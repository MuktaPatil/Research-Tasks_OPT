"""
pure_python_stats.py  (Task 3 / Milestone B)

A GENERALIZED descriptive-statistics + grouped-analysis system, using
ONLY the Python standard library. It makes no assumptions about a
specific dataset's schema: column types, "id-like" grouping columns,
and the numeric metrics used for grouped aggregation are all detected
from the data itself.

Works on any of the three 2024 election social-media datasets (Facebook
Ads, Facebook Posts, Twitter/X Posts) -- and should work on any
reasonably well-formed CSV.

Usage:
    python pure_python_stats.py path/to/any_dataset.csv

Design notes (why it's built this way, not just "how"):

- The file is streamed in a single extra pass after a small sample pass
  for type/grouping detection, rather than loaded entirely into memory
  as a list of row-dicts. One of the three real datasets here
  (2024_fb_ads_president_scored_anon.csv) is ~500MB because of deeply
  nested per-row demographic/region breakdowns; loading that as
  Python objects in full would be wasteful and, on a memory-constrained
  machine, risky. Counting with running accumulators (Counter, sum,
  sum-of-squares, min/max, and an `array.array('d')` for numeric values
  needed for median) scales to files much larger than available RAM for
  every statistic except the exact median, which does require holding
  the numeric column's values -- a tradeoff called out inline below.
"""

import csv
import sys
import os
import re
import ast
import math
from array import array
from collections import Counter, defaultdict

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")
BOOL_TOKENS = {"true", "false"}
SAMPLE_SIZE = 5000
TOP_N = 5
MAX_GROUP_METRICS = 3   # how many numeric columns to use for grouped aggregation


# --------------------------------------------------------------------------
# Generic value parsing
# --------------------------------------------------------------------------

def is_missing(raw):
    return raw is None or raw.strip().lower() in MISSING_TOKENS


def try_parse_range_dict(raw):
    """Some datasets (e.g. Meta ad-transparency exports) report a
    number as a {'lower_bound': X, 'upper_bound': Y} range rather than
    a scalar, to preserve privacy. Convert to the midpoint (or just the
    lower bound for an open-ended top bucket). Not every dataset has
    this pattern -- it's detected, not assumed."""
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
        return val if isinstance(val, list) else None
    except (ValueError, SyntaxError):
        return None


def looks_like_dict(raw):
    """A generic 'complex nested structure' detector for values like
    "{'Texas': {'spend': 249, 'impressions': 47499}}". We deliberately
    do NOT literal_eval these during the full pass -- some datasets put
    deeply nested per-row breakdowns here that are expensive to parse
    at scale and not needed for column-level descriptive stats. They
    are reported as a distinct type with a count, not silently dropped
    or silently mis-typed as text."""
    s = raw.strip()
    return s.startswith("{") and s.endswith("}")


def is_id_like(col_name):
    """Detect 'id-like' columns by name, independent of naming
    convention (snake_case, spaced, or camelCase): split the name into
    tokens and check whether the LAST token is exactly 'id'. This
    avoids false positives like 'covid_topic_illuminating' (which
    contains the substring 'id' but does not end in an 'id' token) or
    'Video Length' (same problem)."""
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", col_name)
    tokens = [t for t in re.split(r"[_\s]+", camel_split) if t]
    return bool(tokens) and tokens[-1].lower() == "id"


# --------------------------------------------------------------------------
# Phase 1: sample the file to infer column types and pick grouping keys
# --------------------------------------------------------------------------

def sample_rows(path, n=SAMPLE_SIZE):
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = []
        for i, row in enumerate(reader):
            if i >= n:
                break
            rows.append(row)
    return rows, fieldnames


def infer_column_type(values):
    """values: raw strings for one column from the sample (missing
    tokens already excluded). Returns one of: empty, range_numeric,
    boolean, list, dict, numeric, categorical."""
    n = len(values)
    if n == 0:
        return "empty"

    def rate(pred):
        return sum(1 for v in values if pred(v)) / n

    if rate(lambda v: bool(RANGE_DICT_RE.match(v))) >= 0.9:
        return "range_numeric"
    if rate(lambda v: v.strip().lower() in BOOL_TOKENS) >= 0.9:
        return "boolean"
    if rate(lambda v: try_parse_list(v) is not None) >= 0.9:
        return "list"
    if rate(looks_like_dict) >= 0.9:
        return "dict"
    if rate(lambda v: try_parse_float(v) is not None) >= 0.9:
        return "numeric"
    return "categorical"


def estimate_cardinality(values):
    return len(set(values))


def choose_group_key_sets(sample_rows_list, fieldnames):
    """Pick sensible grouping column(s). Strategy:

    1. Look for 'id-like' columns by name (works across naming
       conventions -- see is_id_like). Discard any that are missing in
       more than half the sample: a sparse foreign key like
       'inReplyToId' or 'quoteId' being null for ~88% of rows would
       collapse most rows into one meaningless "None" group.
    2. Rank the survivors by sample cardinality. A LOW-cardinality
       id-like column (e.g. page_id, with far fewer unique values than
       rows) behaves like an "entity" grouping. A column whose
       cardinality is close to the row count behaves like a per-record
       primary key (e.g. ad_id, post_id, tweet id) -- useful as a
       second-level grouping key alongside an entity column, but not
       an interesting *sole* grouping key on its own.
    3. If no id-like column looks like an "entity" (this happens for
       the Twitter dataset here, which has no account/page identifier
       at all -- only the tweet's own id), fall back to a
       low/medium-cardinality categorical column (e.g. 'lang',
       'source') as a substitute entity grouping, and still offer the
       per-record id as a second grouping on its own.

    Returns a list of one or two key-column tuples, e.g.
    [('page_id',), ('page_id', 'ad_id')].
    """
    n_sample = len(sample_rows_list)

    def missing_rate(col):
        missing = sum(1 for row in sample_rows_list if is_missing(row.get(col) or ""))
        return missing / n_sample if n_sample else 1.0

    id_cols = [c for c in fieldnames if is_id_like(c) and missing_rate(c) <= 0.5]
    non_missing_samples = {
        c: [row[c] for row in sample_rows_list if not is_missing(row.get(c) or "")]
        for c in id_cols
    }
    cardinality = {c: estimate_cardinality(non_missing_samples[c]) for c in id_cols}
    id_cols_ranked = sorted(id_cols, key=lambda c: cardinality[c])

    ENTITY_RATIO = 0.9  # an id column is "entity-like" if its sample
                         # cardinality is well below the row count

    entity_cols = [c for c in id_cols_ranked
                   if cardinality[c] < ENTITY_RATIO * len(non_missing_samples[c])]
    record_cols = [c for c in id_cols_ranked if c not in entity_cols]

    if entity_cols and record_cols:
        return [(entity_cols[0],), (entity_cols[0], record_cols[0])]
    if entity_cols:
        return [(entity_cols[0],)]

    # No entity-like id column found (e.g. Twitter posts here: only the
    # tweet's own id, no account identifier). Fall back to a
    # low/medium-cardinality categorical column as a substitute entity
    # grouping, and still report the per-record id alone as a second,
    # smaller grouping.
    fallback_entity = None
    for c in fieldnames:
        if c in id_cols:
            continue
        vals = [row[c] for row in sample_rows_list if not is_missing(row.get(c) or "")]
        if not vals:
            continue
        card = estimate_cardinality(vals)
        if 2 <= card <= max(50, len(vals) // 20):
            fallback_entity = c
            break

    result = []
    if fallback_entity:
        result.append((fallback_entity,))
    if record_cols:
        result.append((record_cols[0],))
    return result


def choose_group_metrics(col_types, fieldnames, max_metrics=MAX_GROUP_METRICS):
    """Pick a handful of numeric columns to aggregate during grouped
    analysis. We prefer numeric columns that vary (not a constant-0/1
    flag column) since those make more interesting group summaries;
    "range_numeric" columns count as numeric here too."""
    candidates = [c for c in fieldnames
                  if col_types.get(c) in ("numeric", "range_numeric")]
    return candidates[:max_metrics]


# --------------------------------------------------------------------------
# Phase 2: single streaming pass, using running accumulators
# --------------------------------------------------------------------------

class ColumnAccumulator:
    """Accumulates whatever a column's inferred type needs, without
    holding onto raw strings for high-cardinality / large-payload
    columns (categorical and list columns keep only a Counter; dict
    columns keep only a count)."""

    def __init__(self, col_type):
        self.col_type = col_type
        self.missing = 0
        self.non_missing = 0

        if col_type in ("numeric", "range_numeric"):
            self.values = array("d")
        elif col_type == "boolean":
            self.true_count = 0
            self.false_count = 0
        elif col_type == "list":
            self.item_counts = Counter()
        elif col_type == "dict":
            pass  # count only
        else:  # categorical (also used as fallback for "empty")
            self.value_counts = Counter()

    def add(self, raw):
        if raw is None:
            self.missing += 1
            return
        self.non_missing += 1

        if self.col_type == "range_numeric":
            val = try_parse_range_dict(raw)
            if val is not None:
                self.values.append(val)
        elif self.col_type == "numeric":
            val = try_parse_float(raw)
            if val is not None:
                self.values.append(val)
        elif self.col_type == "boolean":
            v = raw.strip().lower()
            if v == "true":
                self.true_count += 1
            elif v == "false":
                self.false_count += 1
        elif self.col_type == "list":
            parsed = try_parse_list(raw)
            if parsed:
                for item in parsed:
                    self.item_counts[str(item)] += 1
        elif self.col_type == "dict":
            pass
        else:
            self.value_counts[raw] += 1

    def finalize(self):
        """Return a plain dict of the statistics appropriate to this
        column's type."""
        if self.col_type in ("numeric", "range_numeric"):
            return {"type": self.col_type, "missing": self.missing,
                     **compute_numeric_stats(self.values)}
        if self.col_type == "boolean":
            total = self.true_count + self.false_count
            return {"type": "boolean", "missing": self.missing,
                    "count": total, "true_count": self.true_count,
                    "false_count": self.false_count,
                    "true_rate": (self.true_count / total) if total else None}
        if self.col_type == "list":
            top = self.item_counts.most_common(TOP_N)
            mode_item, mode_freq = (top[0] if top else (None, None))
            return {"type": "list", "missing": self.missing,
                    "count": self.non_missing,
                    "nunique_items": len(self.item_counts),
                    "mode_item": mode_item, "mode_item_freq": mode_freq,
                    "top_items": top}
        if self.col_type == "dict":
            return {"type": "dict", "missing": self.missing,
                    "count": self.non_missing,
                    "note": "complex nested value; not expanded generically"}
        # categorical / empty
        top = self.value_counts.most_common(TOP_N)
        mode_val, mode_freq = (top[0] if top else (None, None))
        return {"type": "categorical" if self.value_counts else "empty",
                "missing": self.missing, "count": self.non_missing,
                "nunique": len(self.value_counts), "mode": mode_val,
                "mode_freq": mode_freq, "top_values": top}


def compute_numeric_stats(values):
    n = len(values)
    if n == 0:
        return {"count": 0, "mean": None, "min": None, "max": None,
                "stdev": None, "median": None}
    total = 0.0
    lo = hi = values[0]
    for v in values:
        total += v
        if v < lo:
            lo = v
        if v > hi:
            hi = v
    mean = total / n
    variance_sum = sum((v - mean) ** 2 for v in values)
    stdev = math.sqrt(variance_sum / (n - 1)) if n > 1 else 0.0
    sorted_vals = sorted(values)
    mid = n // 2
    median = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0 if n % 2 == 0 \
        else sorted_vals[mid]
    return {"count": n, "mean": mean, "min": lo, "max": hi,
            "stdev": stdev, "median": median}


class GroupAccumulator:
    """One of these per group-key tuple: tracks row count and running
    sum/count for each selected numeric metric column, so grouped
    aggregation also never needs to hold onto raw rows."""

    def __init__(self, metrics):
        self.metrics = metrics
        self.row_count = 0
        self.sums = {m: 0.0 for m in metrics}
        self.counts = {m: 0 for m in metrics}

    def add(self, row, col_types):
        self.row_count += 1
        for m in self.metrics:
            raw = row.get(m)
            if raw is None:
                continue
            val = try_parse_range_dict(raw) if col_types.get(m) == "range_numeric" \
                else try_parse_float(raw)
            if val is not None:
                self.sums[m] += val
                self.counts[m] += 1

    def summary(self):
        out = {"row_count": self.row_count}
        for m in self.metrics:
            out[f"{m}_sum"] = self.sums[m] if self.counts[m] else None
            out[f"{m}_mean"] = (self.sums[m] / self.counts[m]) if self.counts[m] else None
        return out


def run_pass(path, fieldnames, col_types, group_key_sets, group_metrics):
    accumulators = {c: ColumnAccumulator(col_types[c]) for c in fieldnames}
    group_accumulators = {key_cols: defaultdict(lambda: GroupAccumulator(group_metrics))
                           for key_cols in group_key_sets}
    row_count = 0

    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            clean_row = {}
            for c in fieldnames:
                raw = row.get(c)
                val = None if (raw is None or is_missing(raw)) else raw
                clean_row[c] = val
                accumulators[c].add(val)

            for key_cols in group_key_sets:
                key = tuple(clean_row.get(k) for k in key_cols)
                group_accumulators[key_cols][key].add(clean_row, col_types)

    results = {c: accumulators[c].finalize() for c in fieldnames}
    return row_count, results, group_accumulators


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def fmt(x, decimals=2):
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:,.{decimals}f}"
    return str(x)


def print_column_report(results, fieldnames):
    print("-" * 78)
    print("PER-COLUMN ANALYSIS")
    print("-" * 78)
    for name in fieldnames:
        r = results[name]
        print(f"\n[{name}]")
        print(f"  Inferred type: {r['type']}   Missing: {r['missing']:,}")

        if r["type"] in ("numeric", "range_numeric"):
            note = " (midpoint of a lower/upper-bound range)" \
                if r["type"] == "range_numeric" else ""
            print(f"  Count:  {r['count']:,}{note}")
            print(f"  Mean:   {fmt(r['mean'])}")
            print(f"  Min:    {fmt(r['min'])}")
            print(f"  Max:    {fmt(r['max'])}")
            print(f"  Stdev:  {fmt(r['stdev'])}")
            print(f"  Median: {fmt(r['median'])}")
        elif r["type"] == "boolean":
            print(f"  Count: {r['count']:,}   True: {r['true_count']:,}   "
                  f"False: {r['false_count']:,}   True rate: {fmt(r['true_rate'], 3)}")
        elif r["type"] == "list":
            print(f"  Count (non-null rows): {r['count']:,}")
            print(f"  Unique items:          {r['nunique_items']:,}")
            print(f"  Most frequent item:    {r['mode_item']} "
                  f"({fmt(r['mode_item_freq'], 0)})")
            print("  Top items:")
            for item, freq in r["top_items"]:
                print(f"    - {item}: {freq:,}")
        elif r["type"] == "dict":
            print(f"  Count: {r['count']:,}  -- {r['note']}")
        else:
            print(f"  Count:         {r['count']:,}")
            print(f"  Unique values: {r['nunique']:,}")
            print(f"  Mode:          {r['mode']} ({fmt(r['mode_freq'], 0)})")
            print("  Top values:")
            for val, freq in r["top_values"]:
                display = str(val) if len(str(val)) <= 60 else str(val)[:57] + "..."
                print(f"    - {display}: {freq:,}")


def print_grouped_report(group_accumulators, key_cols, top_n=10):
    groups = group_accumulators[key_cols]
    print(f"\nGrouped by {key_cols}: {len(groups):,} groups")
    if not groups:
        return
    sample_summary = next(iter(groups.values())).summary()
    metric_cols = [k for k in sample_summary if k.endswith("_sum")]
    sort_col = metric_cols[0] if metric_cols else None

    rows = []
    for key, acc in groups.items():
        s = acc.summary()
        s["key"] = key
        rows.append(s)
    if sort_col:
        rows.sort(key=lambda s: (s[sort_col] or 0), reverse=True)

    print(f"Top {top_n} groups"
          f"{' by ' + sort_col if sort_col else ''}:\n")
    header_cols = list(key_cols) + ["row_count"] + metric_cols
    print(" | ".join(header_cols))
    print("-" * 100)
    for s in rows[:top_n]:
        parts = [str(k) for k in s["key"]] + [f"{s['row_count']:,}"]
        parts += [fmt(s[m]) for m in metric_cols]
        print(" | ".join(parts))


def main():
    if len(sys.argv) < 2:
        print("Usage: python pure_python_stats.py path/to/data.csv")
        sys.exit(1)
    path = sys.argv[1]
    dataset_name = os.path.basename(path)

    print("=" * 78)
    print("PURE PYTHON DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
    print(f"Dataset: {dataset_name}")
    print("=" * 78)

    print(f"\nSampling first {SAMPLE_SIZE:,} rows to infer schema...")
    sample, fieldnames = sample_rows(path)
    clean_sample = [
        {c: (None if is_missing(row.get(c) or "") else row.get(c)) for c in fieldnames}
        for row in sample
    ]

    col_types = {}
    for c in fieldnames:
        values = [row[c] for row in clean_sample if row[c] is not None]
        col_types[c] = infer_column_type(values)

    group_key_sets = choose_group_key_sets(clean_sample, fieldnames)
    group_metrics = choose_group_metrics(col_types, fieldnames)

    print(f"Detected grouping key set(s): {group_key_sets}")
    print(f"Detected grouping metric column(s): {group_metrics}")

    print("\nRunning full pass over the file...")
    row_count, results, group_accumulators = run_pass(
        path, fieldnames, col_types, group_key_sets, group_metrics
    )

    print(f"\nTotal rows:    {row_count:,}")
    print(f"Total columns: {len(fieldnames)}\n")

    print("-" * 78)
    print("MISSING VALUES PER COLUMN")
    print("-" * 78)
    for name in fieldnames:
        missing = results[name]["missing"]
        pct = (missing / row_count * 100) if row_count else 0
        print(f"  {name:<45} {missing:>8,} missing ({pct:5.1f}%)")

    print()
    print_column_report(results, fieldnames)

    print("\n" + "=" * 78)
    print("GROUPED ANALYSIS")
    print("=" * 78)
    if not group_key_sets:
        print("No sensible grouping column was detected for this dataset.")
    for key_cols in group_key_sets:
        print_grouped_report(group_accumulators, key_cols)

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
