"""
polars_stats.py  (Task 3 / Milestone B)

A GENERALIZED descriptive-statistics + grouped-analysis system using
Polars. Mirrors pure_python_stats.py / pandas_stats.py's detection
heuristics (column typing, grouping-key selection, grouping metrics) so
all three scripts can be compared directly on any of the three
datasets.

NOTE: Polars was not installable in the sandbox this was authored in
(no network access to PyPI), so this script is written carefully
against the documented Polars API but has NOT been executed. Run it
locally and diff its numeric output against pandas_stats.py's and
pure_python_stats.py's output before trusting it for submission.

Usage:
    python polars_stats.py path/to/any_dataset.csv
"""

import sys
import os
import re
import ast
import polars as pl

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")
SAMPLE_SIZE = 5000
TOP_N = 5
MAX_GROUP_METRICS = 3


# --------------------------------------------------------------------------
# Shared detection helpers (same logic as the other two scripts)
# --------------------------------------------------------------------------

def is_id_like(col_name):
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", col_name)
    tokens = [t for t in re.split(r"[_\s]+", camel_split) if t]
    return bool(tokens) and tokens[-1].lower() == "id"


def looks_like_dict(raw):
    if raw is None:
        return False
    s = str(raw).strip()
    return s.startswith("{") and s.endswith("}")


def looks_like_list(raw):
    if raw is None:
        return False
    s = str(raw).strip()
    return s.startswith("[") and s.endswith("]")


def range_to_midpoint(raw):
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


def infer_column_type(values):
    """values: a Python list of non-null raw strings sampled from one
    column. Mirrors the other two scripts' infer_column_type."""
    n = len(values)
    if n == 0:
        return "empty"

    def rate(pred):
        return sum(1 for v in values if pred(v)) / n

    if rate(lambda v: bool(RANGE_DICT_RE.match(str(v)))) >= 0.9:
        return "range_numeric"
    if rate(lambda v: str(v).strip().lower() in ("true", "false")) >= 0.9:
        return "boolean"
    if rate(looks_like_list) >= 0.9:
        return "list"
    if rate(looks_like_dict) >= 0.9:
        return "dict"

    def parses_numeric(v):
        cleaned = str(v).strip().replace("$", "").replace(",", "").replace("%", "")
        if cleaned == "":
            return False
        try:
            float(cleaned)
            return True
        except ValueError:
            return False

    if rate(parses_numeric) >= 0.9:
        return "numeric"
    return "categorical"


def choose_group_key_sets(sample_df, columns):
    n_sample = sample_df.height

    def missing_rate(col):
        return sample_df[col].null_count() / n_sample if n_sample else 1.0

    id_cols = [c for c in columns if is_id_like(c) and missing_rate(c) <= 0.5]
    cardinality = {c: sample_df[c].n_unique() for c in id_cols}
    non_missing_counts = {c: sample_df[c].drop_nulls().len() for c in id_cols}
    id_cols_ranked = sorted(id_cols, key=lambda c: cardinality[c])

    ENTITY_RATIO = 0.9
    entity_cols = [c for c in id_cols_ranked
                   if non_missing_counts[c] > 0
                   and cardinality[c] < ENTITY_RATIO * non_missing_counts[c]]
    record_cols = [c for c in id_cols_ranked if c not in entity_cols]

    if entity_cols and record_cols:
        return [[entity_cols[0]], [entity_cols[0], record_cols[0]]]
    if entity_cols:
        return [[entity_cols[0]]]

    fallback_entity = None
    for c in columns:
        if c in id_cols:
            continue
        vals = sample_df[c].drop_nulls()
        if vals.len() == 0:
            continue
        card = vals.n_unique()
        if 2 <= card <= max(50, vals.len() // 20):
            fallback_entity = c
            break

    result = []
    if fallback_entity:
        result.append([fallback_entity])
    if record_cols:
        result.append([record_cols[0]])
    return result


def choose_group_metrics(col_types, columns, max_metrics=MAX_GROUP_METRICS):
    candidates = [c for c in columns
                  if col_types.get(c) in ("numeric", "range_numeric")]
    return candidates[:max_metrics]


# --------------------------------------------------------------------------
# Loading + typed conversion
# --------------------------------------------------------------------------

def load(path):
    df = pl.read_csv(path, infer_schema_length=0, null_values=list(MISSING_TOKENS))
    sample = df.head(SAMPLE_SIZE)

    col_types = {}
    for c in df.columns:
        non_null_sample = sample[c].drop_nulls().to_list()
        col_types[c] = infer_column_type(non_null_sample)

    for col, ctype in col_types.items():
        if ctype == "range_numeric":
            df = df.with_columns(
                pl.col(col).map_elements(range_to_midpoint,
                                          return_dtype=pl.Float64).alias(col)
            )
        elif ctype == "numeric":
            cleaned = (pl.col(col)
                       .str.replace_all(r"[\$,%]", "")
                       .cast(pl.Float64, strict=False))
            df = df.with_columns(cleaned.alias(col))
        elif ctype == "boolean":
            df = df.with_columns(
                (pl.col(col).str.to_lowercase() == "true").alias(col)
            )
        # list / dict / categorical columns left as raw strings

    return df, col_types


def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def run_grouped_analysis(df, key_cols, metrics, top_n=10):
    section(f"GROUPED BY {key_cols}")
    n_groups = df.select(key_cols).unique().height
    print(f"Number of groups: {n_groups:,}")
    if not metrics:
        print("No numeric metric columns detected for aggregation.")
        return

    aggs = [pl.len().alias("row_count")]
    for m in metrics:
        aggs.append(pl.col(m).sum().alias(f"{m}_sum"))
        aggs.append(pl.col(m).mean().alias(f"{m}_mean"))

    grouped = df.group_by(key_cols).agg(aggs)
    sort_col = f"{metrics[0]}_sum"
    top = grouped.sort(sort_col, descending=True).head(top_n)
    print(f"\nTop {top_n} groups by {sort_col}:")
    print(top)


def main():
    if len(sys.argv) < 2:
        print("Usage: python polars_stats.py path/to/data.csv")
        sys.exit(1)
    path = sys.argv[1]
    dataset_name = os.path.basename(path)

    print("=" * 78)
    print("POLARS DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
    print(f"Dataset: {dataset_name}")
    print("=" * 78)

    print("\nLoading and inferring schema...")
    df, col_types = load(path)
    columns = df.columns

    group_key_sets = choose_group_key_sets(df.head(SAMPLE_SIZE), columns)
    group_metrics = choose_group_metrics(col_types, columns)

    print(f"Detected grouping key set(s): {group_key_sets}")
    print(f"Detected grouping metric column(s): {group_metrics}")

    section("BASIC STRUCTURE")
    print(f"Shape: {df.height:,} rows x {df.width} columns")

    section("MISSING / NULL VALUES PER COLUMN")
    null_counts = df.null_count()
    for col in columns:
        n_missing = null_counts[col][0]
        pct = (n_missing / df.height * 100) if df.height else 0
        print(f"  {col:<45} {n_missing:>8,} missing ({pct:5.1f}%)  "
              f"type={col_types[col]}")

    numeric_cols = [c for c in columns
                    if col_types[c] in ("numeric", "range_numeric")]
    boolean_cols = [c for c in columns if col_types[c] == "boolean"]
    list_cols = [c for c in columns if col_types[c] == "list"]
    dict_cols = [c for c in columns if col_types[c] == "dict"]
    categorical_cols = [c for c in columns
                        if c not in numeric_cols + boolean_cols
                        + list_cols + dict_cols]

    section(f"DESCRIBE() -- NUMERIC COLUMNS ({len(numeric_cols)})")
    if numeric_cols:
        print(df.select(numeric_cols).describe())

    section(f"BOOLEAN COLUMNS ({len(boolean_cols)})")
    for c in boolean_cols:
        vc = df[c].value_counts()
        true_rate = df[c].cast(pl.Float64, strict=False).mean()
        print(f"[{c}] {vc}  true_rate={true_rate}")

    section(f"CATEGORICAL COLUMNS: n_unique() / value_counts() "
            f"({len(categorical_cols)})")
    for col in categorical_cols:
        print(f"\n[{col}]  n_unique = {df[col].n_unique():,}")
        vc = df[col].value_counts().sort("count", descending=True).head(TOP_N)
        print(vc)

    section(f"LIST-VALUED COLUMNS ({len(list_cols)}) -- exploded item frequency")
    for col in list_cols:
        parsed = df[col].drop_nulls().map_elements(
            lambda s: ast.literal_eval(s) if isinstance(s, str) and
            s.strip().startswith("[") else [],
            return_dtype=pl.List(pl.Utf8),
        )
        exploded = parsed.explode()
        counts = exploded.value_counts().sort("count", descending=True)
        print(f"\n[{col}]  unique items = {counts.height:,}")
        print(counts.head(TOP_N))

    section(f"DICT / NESTED-STRUCTURE COLUMNS ({len(dict_cols)})")
    for col in dict_cols:
        non_null = df[col].drop_nulls().len()
        print(f"[{col}]  count={non_null:,}  "
              f"-- complex nested value, not expanded generically")

    print("\n" + "=" * 78)
    print("GROUPED ANALYSIS")
    print("=" * 78)
    if not group_key_sets:
        print("No sensible grouping column was detected for this dataset.")
    for key_cols in group_key_sets:
        run_grouped_analysis(df, key_cols, group_metrics)

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
