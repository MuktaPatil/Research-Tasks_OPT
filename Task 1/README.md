# Task_01_Descriptive_Stats

Descriptive statistics on real 2024 U.S. Presidential election Facebook
ad purchases, computed two independent ways: with only Python's standard
library, and with Pandas.

## Project description

This project explores `fb_ads_president_scored_anon.csv`, a dataset of
Facebook/Instagram ad purchases from organizations whose ads mentioned a
2024 U.S. presidential candidate. Each row is one ad: who ran it, how
much they reported spending, how many impressions it got, when it ran,
which candidates it mentioned, and a set of message-type/topic flags.

Two scripts independently compute the same descriptive statistics:

- **`pure_python_stats.py`** — uses only `csv`, `math`, `ast`, `re`, and
  `collections`. No third-party packages.
- **`pandas_stats.py`** — the same analysis using Pandas.

Comparing their output is the point of the exercise (see
`COMPARISON.md`), and `FINDINGS.md` has the narrative write-up of what
the data actually shows.

## Setup

**Get the data.** The dataset is not included in this repo. Download it
from the source and place it in the repo root:

- Source: [Google Drive: 2024 Facebook Political Ads](https://drive.google.com/file/d/1gvtvX8fATFrrzraPmTSf205U8u3JExUR/view?usp=sharing)
- Expected filename: `fb_ads_president_scored_anon.csv`

**Install dependencies** (only needed for the Pandas script):

```bash
pip install -r requirements.txt
```

## Running the scripts

```bash
# Standard-library-only analysis
python pure_python_stats.py fb_ads_president_scored_anon.csv

# Pandas analysis
python pandas_stats.py fb_ads_president_scored_anon.csv
```

Both scripts default to looking for `fb_ads_president_scored_anon.csv`
in the current directory if no path is given, and both print a full
report to stdout — redirect to a file if you want to save it
(`python pandas_stats.py data.csv > pandas_output.txt`).

## A note on the data's quirks

Meta's Ad Library API doesn't report `spend`, `impressions`, or
`estimated_audience_size` as exact numbers — it reports each as a
privacy-preserving range, e.g. `{'lower_bound': '200', 'upper_bound':
'299'}`. The top bucket for audience size has no upper bound at all
(`{'lower_bound': '1000001'}`). **Both scripts convert these ranges to
their numeric midpoint** (or the lower bound itself, for the open-ended
top bucket) so they can be described like ordinary numeric columns. This
is a deliberate, documented modeling decision — see the top of each
script for the exact logic — not something either tool did silently.
Because of this, every dollar figure in this analysis is an
approximation, not Meta's ground truth.

`illuminating_mentions` and `publisher_platforms` hold a Python-literal
list per row (e.g. `['Kamala Harris', 'Tim Walz']`). Both scripts treat
these as tag columns: they flatten every row's list and count individual
items, rather than treating the whole list as one categorical value.

## Summary of findings

See `FINDINGS.md` for the full narrative. Headline numbers:

- 246,745 ads from 4,546 distinct pages, roughly Sept 22 – Nov 5, 2024.
- Spending is heavily concentrated: the top 10 spenders account for
  about **63%** of total estimated ad spend.
- Kamala Harris's own page alone accounts for roughly a third of all
  spend in the dataset.
- Ad spend climbs steadily through October and spikes hard in the final
  days before the election (Oct 27–28), then falls off a cliff on Oct
  29 and stays near zero through Election Day — consistent with Meta's
  policy of blocking new political ads in the week before the election.
- Donald Trump is the most-mentioned candidate in ad copy (78,324
  mentions) even though his own campaign page is not the top spender —
  Harris-aligned pages spent heavily on ads that also named Trump.

## Comparison of approaches

See `COMPARISON.md`. Short version: the two scripts agree on every
numeric statistic to the precision Python's floats support. The
pure-Python version forced explicit decisions (what counts as "missing",
how to detect a numeric column, how to parse the range-dict fields) that
Pandas would otherwise make silently via `read_csv` type inference and
`NaN` handling.
