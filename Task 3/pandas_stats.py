"""
pandas_stats.py  (Task 3 / Milestone B)

A GENERALIZED descriptive-statistics + grouped-analysis system using
Pandas. Works on any of the three 2024 election social-media datasets
(Facebook Ads, Facebook Posts, Twitter/X Posts) without dataset-specific
hardcoding: column types, grouping keys, and grouping metrics are all
detected from the data, using the same heuristics as pure_python_stats.py
so the two scripts' outputs can be compared directly.

Usage:
    python pandas_stats.py path/to/any_dataset.csv
"""

import sys
import os
import re
import ast
import pandas as pd

MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan", "-"}
RANGE_DICT_RE = re.compile(r"^\s*\{.*lower_bound.*\}\s*$")
SAMPLE_SIZE = 5000
TOP_N = 5
MAX_GROUP_METRICS = 3


# --------------------------------------------------------------------------
# Shared detection helpers (same logic as pure_python_stats.py)
# --------------------------------------------------------------------------

def is_id_like(col_name):
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", col_name)
    tokens = [t for t in re.split(r"[_\s]+", camel_split) if t]
    return bool(tokens) and tokens[-1].lower() == "id"


def looks_like_dict(raw):
    s = str(raw).strip()
    return s.startswith("{") and s.endswith("}")


def looks_like_list(raw):
    s = str(raw).strip()
    return s.startswith("[") and s.endswith("]")


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


def infer_column_type(series_sample):
    """series_sample: a pandas Series of raw (string) values, already
    stripped of missing tokens. Mirrors pure_python_stats.py's
    infer_column_type so the two scripts agree on typing."""
    n = len(series_sample)
    if n == 0:
        return "empty"
    s = series_sample.astype(str)

    if (s.str.match(RANGE_DICT_RE).sum() / n) >= 0.9:
        return "range_numeric"
    if (s.str.lower().isin(["true", "false"]).sum() / n) >= 0.9:
        return "boolean"
    if (s.apply(looks_like_list).sum() / n) >= 0.9:
        return "list"
    if (s.apply(looks_like_dict).sum() / n) >= 0.9:
        return "dict"
    numeric_hits = pd.to_numeric(
        s.str.replace(r"[\$,%]", "", regex=True), errors="coerce"
    ).notna().sum()
    if (numeric_hits / n) >= 0.9:
        return "numeric"
    return "categorical"


def choose_group_key_sets(sample_df, columns):
    """Same strategy as pure_python_stats.py: prefer a low-cardinality
    'entity' id-like column (+ a per-record id-like column as a second
    grouping level); fall back to a categorical column if no id-like
    column looks like an entity at all."""
    n_sample = len(sample_df)

    def missing_rate(col):
        return sample_df[col].isna().mean()

    id_cols = [c for c in columns if is_id_like(c) and missing_rate(c) <= 0.5]
    cardinality = {c: sample_df[c].nunique(dropna=True) for c in id_cols}
    non_missing_counts = {c: sample_df[c].notna().sum() for c in id_cols}
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
        vals = sample_df[c].dropna()
        if vals.empty:
            continue
        card = vals.nunique()
        if 2 <= card <= max(50, len(vals) // 20):
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
    df = pd.read_csv(path, dtype=str, keep_default_na=True,
                      na_values=list(MISSING_TOKENS))
    sample = df.head(SAMPLE_SIZE)

    col_types = {}
    for c in df.columns:
        non_null_sample = sample[c].dropna()
        col_types[c] = infer_column_type(non_null_sample)

    for col, ctype in col_types.items():
        if ctype == "range_numeric":
            df[col] = df[col].apply(range_to_midpoint)
        elif ctype == "numeric":
            df[col] = pd.to_numeric(
                df[col].str.replace(r"[\$,%]", "", regex=True), errors="coerce"
            )
        elif ctype == "boolean":
            df[col] = df[col].str.lower().map({"true": True, "false": False})
        # list / dict / categorical columns are left as raw strings

    return df, col_types


def section(title):
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def run_grouped_analysis(df, key_cols, metrics, top_n=10):
    section(f"GROUPED BY {key_cols}")
    grouped = df.groupby(key_cols, dropna=False)
    print(f"Number of groups: {grouped.ngroups:,}")
    if not metrics:
        print("No numeric metric columns detected for aggregation.")
        return

    agg_dict = {}
    for m in metrics:
        agg_dict[f"{m}_sum"] = (m, "sum")
        agg_dict[f"{m}_mean"] = (m, "mean")
    agg = grouped.agg(row_count=(key_cols[0], "size"), **agg_dict).reset_index()

    sort_col = f"{metrics[0]}_sum"
    top = agg.sort_values(sort_col, ascending=False).head(top_n)
    print(f"\nTop {top_n} groups by {sort_col}:")
    print(top.to_string(index=False))


def main():
    if len(sys.argv) < 2:
        print("Usage: python pandas_stats.py path/to/data.csv")
        sys.exit(1)
    path = sys.argv[1]
    dataset_name = os.path.basename(path)

    print("=" * 78)
    print("PANDAS DESCRIPTIVE STATISTICS + GROUPED ANALYSIS")
    print(f"Dataset: {dataset_name}")
    print("=" * 78)

    print("\nLoading and inferring schema...")
    df, col_types = load(path)
    columns = list(df.columns)

    group_key_sets = choose_group_key_sets(df.head(SAMPLE_SIZE), columns)
    group_metrics = choose_group_metrics(col_types, columns)

    print(f"Detected grouping key set(s): {group_key_sets}")
    print(f"Detected grouping metric column(s): {group_metrics}")

    section("BASIC STRUCTURE")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    section("MISSING VALUES PER COLUMN")
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    print(pd.DataFrame({"missing_count": missing_count,
                         "missing_pct": missing_pct,
                         "inferred_type": pd.Series(col_types)}))

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
        with pd.option_context("display.max_columns", None, "display.width", 160):
            print(df[numeric_cols].describe().T)

    section(f"BOOLEAN COLUMNS ({len(boolean_cols)})")
    for c in boolean_cols:
        vc = df[c].value_counts(dropna=False)
        print(f"[{c}] {vc.to_dict()}  true_rate={df[c].mean():.3f}")

    section(f"DESCRIBE() -- CATEGORICAL COLUMNS ({len(categorical_cols)})")
    if categorical_cols:
        with pd.option_context("display.max_columns", None, "display.width", 160):
            print(df[categorical_cols].describe().T)

    section("CATEGORICAL COLUMNS: nunique() / top value_counts()")
    for col in categorical_cols:
        print(f"\n[{col}]  nunique = {df[col].nunique():,}")
        print(df[col].value_counts().head(TOP_N).to_string())

    section(f"LIST-VALUED COLUMNS ({len(list_cols)}) -- exploded item frequency")
    for col in list_cols:
        parsed = df[col].dropna().apply(
            lambda s: ast.literal_eval(s) if isinstance(s, str) and
            s.strip().startswith("[") else []
        )
        counts = parsed.explode().value_counts()
        print(f"\n[{col}]  unique items = {counts.shape[0]:,}")
        print(counts.head(TOP_N).to_string())

    section(f"DICT / NESTED-STRUCTURE COLUMNS ({len(dict_cols)})")
    for col in dict_cols:
        non_null = df[col].notna().sum()
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
