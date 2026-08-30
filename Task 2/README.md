# Task_02_Descriptive_Stats

Descriptive statistics and grouped analysis on 2024 U.S. Presidential
election Facebook ad purchases, computed three independent ways: pure
Python, Pandas, and Polars.

## Project description

This builds on Task 1 by adding:

1. **Polars** as a third analytical approach alongside pure Python and
   Pandas.
2. **Grouped analysis** — statistics computed per `page_id`, and per
   `(page_id, ad_id)` combination, not just across the whole dataset.

- **`pure_python_stats.py`** — standard library only (`csv`, `math`,
  `ast`, `re`, `collections`).
- **`pandas_stats.py`** — the same analysis using Pandas.
- **`polars_stats.py`** — the same analysis using Polars.

## Setup

**Get the data.** Not included in this repo. Download and place in the
repo root as `fb_ads_president_scored_anon.csv`:

- Source: [Google Drive: 2024 Facebook Political Ads](https://drive.google.com/file/d/1UPo11lH2Mlk2cnLtjv8P9XqlKitms-gp/view?usp=sharing)

**Install dependencies:**

```bash
pip install -r requirements.txt
```

## Running the scripts

```bash
python pure_python_stats.py fb_ads_president_scored_anon.csv
python pandas_stats.py fb_ads_president_scored_anon.csv
python polars_stats.py fb_ads_president_scored_anon.csv
```

Each script defaults to `fb_ads_president_scored_anon.csv` in the
current directory if no path is given. Redirect output to a file if you
want to save it (`python pandas_stats.py data.csv > pandas_output.txt`).

**Important — verify polars_stats.py before submitting.** It was
written against the documented Polars API but could not be executed or
tested in the environment this was built in (no internet access to
install the `polars` package). Run it locally, and diff its numeric
output against `pandas_output.txt` and `pure_python_output.txt` to
confirm it agrees before you rely on it. `pure_python_stats.py` and
`pandas_stats.py` were both run against the real dataset and their
outputs are included (`pure_python_output.txt`, `pandas_output.txt`) —
their numbers match exactly.

## A note on the data's quirks (same as Task 1)

`spend`, `impressions`, and `estimated_audience_size` arrive as
Meta privacy-preserving ranges, e.g. `{'lower_bound': '200',
'upper_bound': '299'}`, with an open-ended top bucket for audience size
(`{'lower_bound': '1000001'}`). All three scripts convert these to a
numeric midpoint (or the lower bound itself for the open-ended bucket)
before computing statistics — a documented decision, not a silent
default. `publisher_platforms` and `illuminating_mentions` hold a
Python-literal list per row; all three scripts flatten these and count
individual items.

## Summary of findings

Grouped by `page_id`, spend is extremely concentrated: the top page
(Kamala Harris's own page, 55,503 ads) accounts for **$82.8M** of total
spend, more than 3x the next-highest page. Grouped by `(page_id,
ad_id)` — i.e., looking at individual ads rather than pages — the
highest-spending single ads cluster near Meta's reported maximum range
(several individual ads report an estimated spend around $275K–$475K
and reach the platform's top impressions bucket of 1,000,000). This
tells a different story than the page-level view: a handful of pages
dominate *aggregate* spend, but a handful of specific *ads* dominate at
the top of the per-ad spend distribution, and they aren't necessarily
run by the same pages that dominate in aggregate.

See `REFLECTION.md` for the comparison of the three approaches and
answers to the milestone's research questions.
