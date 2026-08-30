# COMPARISON.md

## Do the results agree?

Yes. Every numeric column's count, mean, min, max, standard deviation,
and median match between `pure_python_stats.py` and `pandas_stats.py`
to the precision floats support. For example, `spend`: both scripts
report count 246,745, mean 1,061.79, min 49.50, max 474,999.50, and
median 49.50. Same story for `impressions`, `estimated_audience_size`,
and every `illuminating_*` flag column.

They agree because both scripts make the *same explicit decision* about
how to handle Meta's range-valued columns (convert to midpoint) before
computing anything — that decision, not the computation itself, is
where disagreement would actually come from if the two scripts handled
it differently.

## Where pure Python forced decisions that Pandas hides

- **What counts as numeric.** `pandas.read_csv` will happily infer a
  dtype for you, but it has no way to know that
  `{'lower_bound': '200', 'upper_bound': '299'}` is "secretly" a number.
  Left alone, Pandas would treat `spend` as a plain object/string column
  and `describe()` would report it as categorical — the mean, stdev, etc.
  would silently be missing rather than wrong. Writing the pure-Python
  version first is what surfaced this: `try_parse_float` failed on every
  row of `spend`, which forced me to actually look at a raw cell and
  notice the range-dict format before I could compute anything.

- **What counts as missing.** The standard library gives you a raw
  string and nothing else. I had to define `MISSING_TOKENS` myself
  (`""`, `"na"`, `"n/a"`, `"null"`, `"none"`, `"nan"`, `"-"`) — Pandas'
  `read_csv` recognizes a broader, slightly different default set of NA
  strings automatically. In this dataset it didn't change any counts,
  but on a messier dataset it could.

- **Sample vs. population standard deviation.** Both scripts use the
  sample standard deviation (`n-1` denominator) to match
  `pandas.Series.std()`'s default — but that's a choice I had to know to
  make explicitly in the pure-Python version; Pandas just calls it `std()`
  and moves on.

- **Single-value edge cases.** For a column with exactly one non-missing
  value, sample stdev is undefined (would require dividing by zero).
  `pure_python_stats.py` returns `0.0` for that case explicitly; Pandas'
  `.std()` returns `NaN`. This is one place the two tools genuinely
  differ by default — worth knowing if either script is ever pointed at
  a smaller or more fragmented dataset than this one.

## Where Pandas made things faster without hiding meaning

Pandas' `value_counts()`, `nunique()`, `describe()`, and `.explode()`
(for the list-valued mention/platform columns) do exactly what the
hand-written `Counter`-based equivalents do in the pure-Python script,
just in one line instead of a small function. Once the type-inference
and range-parsing decisions were made explicitly (and shared between
both scripts' logic), Pandas didn't hide anything meaningful here — it
just executed the same idea faster and with less code.

## What writing the pure-Python version taught me that Pandas alone wouldn't have

Writing `try_parse_float` and watching it fail on `spend` is what made
the range-dict format visible at all. If I'd started with
`pd.read_csv().describe()`, `spend` would have quietly shown up as a
non-numeric column with no mean or stdev, and it would have been easy to
assume that was simply because spend data wasn't available for this ad
type — not because the values needed one extra parsing step first. The
manual version forces you to look at a raw cell before you can move on;
Pandas lets you move on without looking.
