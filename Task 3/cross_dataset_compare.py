"""
cross_dataset_compare.py  (Task 3 / Milestone B)

Compares the 27 "illuminating_*" scored flag columns shared across all
three datasets (Facebook Ads, Facebook Posts, Twitter/X Posts) and
reports where the platforms tell the same story vs. a different one.

This is a support script, not one of the three required per-dataset
approaches -- it uses Pandas for convenience, reading all three CSVs
directly rather than re-parsing the other scripts' text output.

Usage:
    python cross_dataset_compare.py ads.csv fb_posts.csv tw_posts.csv
"""

import sys
import pandas as pd

DEFAULT_PATHS = {
    "ads": "2024_fb_ads_president_scored_anon.csv",
    "fb_posts": "2024_fb_posts_president_scored_anon.csv",
    "tw_posts": "2024_tw_posts_president_scored_anon.csv",
}


def find_shared_columns(paths):
    header_sets = {}
    for name, path in paths.items():
        with open(path, encoding="utf-8", errors="replace") as f:
            header = f.readline().strip()
        header_sets[name] = set(header.split(","))
    names = list(header_sets)
    shared = set.intersection(*header_sets.values())
    only = {}
    for i, a in enumerate(names):
        for b in names:
            if a == b:
                continue
        only[a] = header_sets[a] - set.union(*[header_sets[b] for b in names if b != a])
    return sorted(shared), only, header_sets


def compare_shared_flag_columns(paths, shared_cols):
    """For every shared column, compute the mean (i.e. the rate at
    which the flag is set, since these are 0/1 scored columns) in each
    dataset, coercing to numeric and ignoring anything that doesn't
    parse -- some shared columns may be stored as '0'/'1' strings in
    one dataset and '0.0'/'1.0' floats in another."""
    rates = {}
    for name, path in paths.items():
        df = pd.read_csv(path, usecols=lambda c: c in shared_cols, dtype=str)
        rates[name] = {c: pd.to_numeric(df[c], errors="coerce").mean()
                        for c in shared_cols if c in df.columns}
    result = pd.DataFrame(rates)
    result["spread"] = result.max(axis=1) - result.min(axis=1)
    return result.sort_values("spread", ascending=False)


def main():
    if len(sys.argv) == 4:
        paths = {"ads": sys.argv[1], "fb_posts": sys.argv[2], "tw_posts": sys.argv[3]}
    else:
        paths = DEFAULT_PATHS
        print("No paths given on the command line -- using default filenames "
              "in the current directory:")
        for k, v in paths.items():
            print(f"  {k}: {v}")

    print("\n" + "=" * 78)
    print("CROSS-DATASET COMPARISON")
    print("=" * 78)

    shared, _, header_sets = find_shared_columns(paths)
    print(f"\nColumns shared by ALL THREE datasets: {len(shared)}")
    for c in shared:
        print(f"  - {c}")

    for name in paths:
        unique_to = header_sets[name] - set.union(
            *[header_sets[o] for o in paths if o != name]
        )
        print(f"\nColumns unique to {name} ({len(unique_to)}):")
        for c in sorted(unique_to)[:15]:
            print(f"  - {c}")
        if len(unique_to) > 15:
            print(f"  ... and {len(unique_to) - 15} more")

    print("\n" + "-" * 78)
    print("RATE OF EACH SHARED FLAG BEING SET, PER DATASET (0.0-1.0)")
    print("Sorted by spread (max - min across the three platforms)")
    print("-" * 78)
    comparison = compare_shared_flag_columns(paths, shared)
    with pd.option_context("display.max_rows", None, "display.width", 160):
        print(comparison.round(3))

    print("\n" + "=" * 78)
    print("END OF REPORT")
    print("=" * 78)


if __name__ == "__main__":
    main()
