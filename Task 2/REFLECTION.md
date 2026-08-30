# REFLECTION.md

## Was it a challenge to produce identical numerical results across all three approaches?

Less than expected, because the hard part (deciding how to turn Meta's
range-dict `spend`/`impressions`/`estimated_audience_size` fields into
numbers) was already solved in Task 1. Once that conversion logic is
pinned down identically in all three scripts, the actual aggregation —
sum, mean, count per group — is arithmetic that pure Python, Pandas, and
Polars all agree on exactly. Where I'd expect real discrepancies to
creep in on a messier dataset: different default null-handling in
`groupby`/`group_by` (Pandas drops rows with a null grouping key by
default; Polars keeps a null group unless told otherwise), and
different default ddof in standard deviation — I standardized on sample
stdev (n-1) everywhere to keep parity with Pandas' `.std()` default.

## Do I find one approach easier or more performant than the others?

This is developer-experience-based, not benchmarked. Pandas felt fastest
to write correct code in, because its groupby/agg API is the one I
already know well. Polars' expression syntax (`pl.col(...).sum()` inside
`.agg([...])`) is more verbose to write the first time but reads more
predictably once you're used to it — it's harder to accidentally trigger
an implicit index-alignment bug the way you sometimes can in Pandas.
Pure Python is the slowest to write and the most verbose, but it's the
only one where every step (what counts as a group, what counts as
missing, how mean/stdev are computed) is fully visible in the code
itself rather than delegated to a library.

## If coaching a junior analyst who's never used any of these tools, which would I recommend first?

Pandas, still — its API is the most-documented, most Stack-Overflow'd,
and most likely to be the one their future coworkers already know. But
I'd have them write at least one pure-Python version of something small
first, for the same reason Task 1 assigned it: it's the only way to
build an intuition for what "the library did something reasonable here"
actually means, so they can recognize when a library's default silently
doesn't apply to their data.

## Can AI tools produce useful template code for each approach?

Yes, with caveats. Asked cold for "descriptive statistics on a CSV,"
AI tools default to Pandas with `df.describe()` — which is a reasonable
default for a *clean* CSV of plain numbers and strings, but it does
nothing special for this dataset's range-dict spend/impressions fields
or its list-valued mention/platform columns. That gap is exactly where
independently thinking through the data (per Task 1's instructions) had
to come before any code got written, AI-assisted or not. I'd treat
AI-generated statistical code the way I treat a stats library's default:
useful for structure, but something to verify against a manual
calculation before trusting the numbers.

## Data cleaning required before meaningful statistics were possible

Same as Task 1: the range-dict spend/impressions/audience-size columns
needed explicit parsing into numeric midpoints before any of the three
tools could treat them as numeric, and the `illuminating_mentions` /
`publisher_platforms` columns needed to be recognized as tag lists
rather than opaque strings before frequency counts were meaningful. All
three approaches handle *doing* that parsing about equally easily once
you know it's needed (regex + `ast.literal_eval` works fine in pure
Python, `.apply()` in Pandas, `.map_elements()` in Polars) — the harder
part in every case was *noticing* the parsing was needed at all, which
came from actually looking at raw cell values rather than trusting any
tool's default type inference.
