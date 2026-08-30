# Task_03_Descriptive_Stats

A generalized descriptive-statistics and grouped-analysis **system**
(not dataset-specific scripts) for the three 2024 U.S. election social
media datasets: Facebook Ads, Facebook Posts, and Twitter/X Posts.

## Project description

Each of the three core scripts —

- **`pure_python_stats.py`** (standard library only)
- **`pandas_stats.py`**
- **`polars_stats.py`**

— accepts *any* CSV path as a command-line argument and adapts to it:

- **Column types are detected, not assumed.** Each column is sampled
  and classified as numeric, a Meta-style privacy range (`{'lower_bound':
  ..., 'upper_bound': ...}`), boolean (`True`/`False` strings), a
  Python-literal list (tag columns like candidate mentions), a nested
  dict/structure (e.g. per-region spend breakdowns), or categorical
  text — using the same thresholded logic in all three scripts, so
  their outputs can be compared directly.
- **Grouping columns are detected, not hardcoded.** Each script looks
  for "id-like" column names (by tokenizing the name, so it recognizes
  `page_id`, `Facebook_Id`, and `quoteId` alike), discards sparse
  foreign keys (e.g. Twitter's `inReplyToId`, null ~88% of the time),
  and picks a low-cardinality "entity" column plus a per-record id
  column where both exist. Where no id-like column looks like an
  entity (this is the actual situation for the Twitter dataset here —
  it has no account/page identifier column at all), the system falls
  back to a low/medium-cardinality categorical column (e.g. `source`).
- **Grouping metrics are detected, not hardcoded.** Each script picks
  up to three numeric columns to sum/average per group.

A fourth script, **`cross_dataset_compare.py`**, reads all three files
and compares the 27 `illuminating_*` scored columns that are common to
every dataset — see the "cross-platform findings" section below and
`CROSS_DATASET.md` for the full write-up.

## Setup

**Get the data.** Not included in this repo (three files). Download and
place in the repo root:

- Source: [Google Drive: 2024 Election Social Media Data](https://drive.google.com/file/d/1Jq0fPb-tq76Ee_RtM58fT0_M3o-JDBwe/view?usp=sharing)
- Expected filenames: `2024_fb_ads_president_scored_anon.csv`,
  `2024_fb_posts_president_scored_anon.csv`,
  `2024_tw_posts_president_scored_anon.csv`

**Install dependencies:**

```bash
pip install -r requirements.txt
```

## Running the scripts

The same script runs on all three files, unmodified:

```bash
python pure_python_stats.py 2024_fb_ads_president_scored_anon.csv
python pure_python_stats.py 2024_fb_posts_president_scored_anon.csv
python pure_python_stats.py 2024_tw_posts_president_scored_anon.csv

python pandas_stats.py 2024_fb_ads_president_scored_anon.csv
python pandas_stats.py 2024_fb_posts_president_scored_anon.csv
python pandas_stats.py 2024_tw_posts_president_scored_anon.csv

python polars_stats.py 2024_fb_ads_president_scored_anon.csv
python polars_stats.py 2024_fb_posts_president_scored_anon.csv
python polars_stats.py 2024_tw_posts_president_scored_anon.csv

python cross_dataset_compare.py 2024_fb_ads_president_scored_anon.csv \
    2024_fb_posts_president_scored_anon.csv \
    2024_tw_posts_president_scored_anon.csv
```

**Important — verify `polars_stats.py` before submitting.** It was
written against the documented Polars API but could not be executed in
the sandbox this was built in (no network access to install the
`polars` package). Run it locally and diff its output against
`*_pandas_output.txt` / `*_pure_python_output.txt` in this repo before
relying on its numbers. `pure_python_stats.py`, `pandas_stats.py`, and
`cross_dataset_compare.py` were all run against the real files, and
their outputs (`*_output.txt`) are included — the pure-Python and
Pandas numbers match exactly on every dataset, including the ~500MB
ads file.

## A note on the ads dataset's size and structure

This milestone's ads file (`2024_fb_ads_president_scored_anon.csv`) is
a *different export* than the one used in Tasks 1–2: `estimated_spend`,
`estimated_impressions`, and `estimated_audience_size` are now plain
numbers, not privacy-range dicts — but two new columns,
`delivery_by_region` and `demographic_distribution`, hold deeply nested
per-row breakdowns instead, making the file ~500MB for the same
246,745 rows. `pure_python_stats.py` deliberately never loads the full
file into memory as a list of row-dicts: it streams the file once,
updating running per-column and per-group accumulators (counts, sums,
`Counter`s for categorical/tag columns), and only holds full value
lists for genuinely numeric columns (needed for exact median). Nested
dict-type columns are detected and counted, but not parsed in bulk —
see the comments at the top of that script for the reasoning.

## Summary of findings per dataset

- **Facebook Ads**: 246,745 rows. Spend is concentrated: the top
  page-level entity accounts for over $82M of total spend, more than 3x
  the next-highest. See Task 1/2's `FINDINGS.md`/`README.md` for a
  fuller narrative on ad spend and timing (based on the earlier ads
  export, which has the same underlying spend/timing patterns).
- **Facebook Posts**: 19,009 rows across only 21 distinct Facebook
  pages, so this file is a curated set of high-profile pages rather
  than a broad sample. `cta_msg_type_illuminating` fires far less often
  here (13.3%) than in ads (57.3%) — organic posts ask for
  clicks/donations/votes much less often than paid ads do.
- **Twitter/X Posts**: 27,304 rows, no account/page identifier column
  at all (only the tweet's own id) — the system falls back to grouping
  by `source` (the posting client, e.g. "Twitter Web App", "Sprout
  Social") as the closest thing to an "entity" grouping available.
  `issue_msg_type_illuminating` is the single highest of any platform
  here (50.8%), higher than both Facebook posts (46.0%) and ads
  (38.2%).

## Cross-dataset comparison

27 `illuminating_*` scored columns are shared across all three files.
See `CROSS_DATASET.md` for the full write-up. Headline: **calls to
action are almost exclusively an ads phenomenon** —
`cta_msg_type_illuminating` is set on 57.3% of ads vs. only ~11-13% of
organic Facebook/Twitter posts — while **advocacy messaging is
strikingly consistent across all three platforms** (54.9%, 54.9%, and
56.4%).

## Reflection on the three approaches at this stage

See `REFLECTION.md`.

## A note on a real data-quality issue found while generalizing

The Facebook Posts CSV header has a genuine formatting bug: two column
names are concatenated with no comma between them
(`illuminating_scored_messageelection_integrity_Truth_illuminating`),
so `election_integrity_Truth_illuminating` doesn't parse out as its own
column the way it does in the other two files. Rather than silently
"fixing" this with a dataset-specific hardcoded split (which would
undermine the point of a generalized system), it's surfaced by
`cross_dataset_compare.py`'s "columns unique to fb_posts" section and
documented here — a real researcher would need to go back to the data
provider or manually repair that one header cell before this column
could be compared across platforms.
