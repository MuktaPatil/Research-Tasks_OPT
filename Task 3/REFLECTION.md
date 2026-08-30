# REFLECTION.md

## How much of the Milestone A code could I reuse without modification?

Very little of Milestone A's code ran unmodified, but almost all of its
*logic* transferred. Milestone A's scripts hardcoded column names
(`page_id`, `ad_id`, `spend`) and one specific range-dict parsing rule.
Pointed at this milestone's ads file, that would have broken
immediately: this export's `estimated_spend` is a plain number, not a
range dict, and the range-dict pattern instead shows up nowhere in this
file at all (though the detection logic for it is still in this
milestone's scripts, in case a future dataset needs it). Pointed at the
Facebook Posts or Twitter files, hardcoded ads-specific column names
would fail outright — those files don't have a `page_id` or `spend`
column at all. What *did* transfer directly: the missing-value
handling, the numeric-stats math (mean/stdev/median), and the general
shape of "sample the data, infer a type per column, branch on that
type" — Milestone A already did this, just with dataset-specific
trigger conditions instead of a general classifier.

## What strategies made the code dataset-agnostic?

Three things, in order of how much they mattered:

1. **Type detection by sampling and thresholding**, not by column name.
   A column is "numeric" if ~90%+ of a sample parses as a float,
   regardless of whether it's called `spend`, `Likes`, or `viewCount`.
2. **Grouping-key detection by tokenizing column names**, not by
   knowing `page_id` exists. Splitting `Facebook_Id`, `quoteId`, and
   `page_id` into tokens and checking whether the last token is `id`
   generalizes across three very different naming conventions in this
   project's own three files.
3. **A documented fallback path for "no good grouping key exists."**
   Twitter's dataset genuinely has no account-level identifier — that's
   a fact about the data, not a bug in the detection logic — so the
   system falls back to a categorical column (`source`) instead of
   either crashing or silently grouping by something meaningless.

## Did the three platforms tell the same story or different ones?

Both, depending on the column — see `CROSS_DATASET.md` for the full
comparison. The short version: baseline advocacy messaging is nearly
identical across all three platforms (~55%), but calls-to-action are
overwhelmingly concentrated in paid ads (57% vs. ~11-13% on organic
posts), and issue-based/attack messaging is actually *highest* on
Twitter, not on ads — which cut against my initial assumption that ads
would be the most aggressive/persuasive channel across every dimension.

## What would a colleague need to change to point this at a totally different dataset (e.g. a health survey)?

Very little of the core logic, honestly — that's the point of building
it this way. They'd need to: (1) confirm the type-inference thresholds
(90% for numeric/list/dict/boolean) still make sense for their data's
messiness level, since a much noisier survey export might need a lower
threshold; (2) check that the grouping-key tokenizer's "ends in the
token 'id'" heuristic actually finds their entity columns, or add a
manual override if their identifier columns use an unusual naming
convention (e.g. `patient_num` instead of `patient_id`); and (3) sanity
check the "pick numeric columns for grouping metrics" step, since a
financial log's numeric columns (transaction amounts) are probably more
interesting to sum/average than, say, a numeric "row sequence number"
column, which this system has no way to know to exclude on its own.

## How has my opinion of pure Python vs. Pandas vs. Polars evolved?

After three tasks, my take has shifted from "Pandas is just more
convenient" to "each tool makes a different bet about what you'll need
to see explicitly." Pure Python forces you to write down every
decision (what's numeric, what's missing, how groups are keyed) as
code you can point to and defend — valuable for exactly the kind of
generalization work this milestone asked for, because writing the
type-inference and grouping-key logic by hand in pure Python is what
made it obvious those decisions needed to be made at all, before I
wrote the Pandas/Polars equivalents. Pandas remains the fastest to get
something working. Polars' stricter typing would, in a real (executed)
run, likely surface schema problems earlier and more loudly than
Pandas does by default — Pandas will often silently coerce a mixed
column to `object` and let you find out later; Polars tends to error
or require an explicit cast. I can't confirm that from an actual run
this time (see the README's note on `polars_stats.py` not being
executable in this environment), which is itself a useful data point:
Polars' comparatively newer, more narrowly-scoped ecosystem means it's
not always the safe default to reach for in an environment where you
can't freely install packages.

## Can AI tools produce useful code for the generalization problem, or do they default to dataset-specific solutions?

In my experience working through this, the default failure mode is
exactly dataset-specific solutions: asked to "compute descriptive
statistics," an AI tool's first draft tends to reach for concrete
column names it can see in a sample of the data, which is exactly the
Milestone-A-style hardcoding this milestone is designed to move past.
Getting genuinely dataset-agnostic code requires explicitly asking for
sampling-based type inference and name-pattern-based (not
literal-name-based) key detection — the generalization has to be
requested as a requirement, not assumed to happen by default just
because the tool is capable of writing it.
