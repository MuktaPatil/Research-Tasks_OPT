# prompt_log.md — Phase A: Baseline Factual Q&A

## Model tested

**Claude Sonnet 5** (this conversation), given the raw data as a
pasted CSV/markdown table (no code execution tool available in this
pass — see the "important limitation" note below).

## ⚠️ Important limitation of this pass

The same model instance that built `ground_truth_stats.py` is also the
one answering the questions below in this log. That is **not** a
genuinely blind test — a truly independent test needs either (a) a
fresh session/different model with no memory of building the ground
truth, or (b) a different model entirely (ChatGPT, Copilot). This pass
should be read as a **demonstration of the log format and question
design**, not as strong evidence that Claude is reliable on this data.
The bonus "compare multiple models" section of the assignment is the
right place to get a real answer to that — re-run these exact prompts
in a fresh ChatGPT/Copilot/Claude session with no prior context and
record the results the same way.

For each question below, the "process" line describes the reasoning
actually used to answer *without* looking at `ground_truth_output.txt`
first; the verdict was then checked against that file afterward.

---

### Q1

**Prompt:** "Here's the 2025 Syracuse Women's Lacrosse schedule as a
CSV [pasted `su_wlax_2025_games.csv`]. How many games did this team
play this season?"

**Response:** 19 games.

**Process:** Counted data rows in the pasted table (excluding header).

**Ground truth:** 19.

**Verdict:** ✅ Correct. This is about as easy as a factual question
gets — a straight row count — and it's not a useful discriminator on
its own.

---

### Q2

**Prompt:** "Here's the player stats table [pasted
`su_wlax_2025_players.csv`]. Which player scored the most goals?"

**Response:** Emma Muchnick, with 34 goals.

**Process:** Scanned the `goals` column for the maximum value.

**Ground truth:** Emma Muchnick, 34 goals.

**Verdict:** ✅ Correct. Note this is a genuine, slightly
counter-intuitive result: Emma Ward has the most **points** (76, driven
by a league-leading 46 assists) but is only third in goals. A model
that conflates "leading scorer" (points) with "most goals" would answer
Emma Ward here — worth explicitly testing as a follow-up (see Q7).

---

### Q3

**Prompt:** "Using the schedule table, what was the team's average
margin of victory in wins?"

**Response:** 5.50 goals per win, over 10 wins.

**Process:** Listed all 10 wins and their margins by hand: UAlbany +12,
Maryland +6, Cornell +8, Stanford +1, Pitt +6, Loyola +2, Notre Dame
+1, Virginia +1, California +12, Brown +6. Sum = 55; 55 / 10 = 5.5.

**Ground truth:** 5.50.

**Verdict:** ✅ Correct. This is exactly the kind of question where a
model doing mental arithmetic over 10 numbers is one transposition
away from a wrong answer — worth spot-checking even when the final
number "looks reasonable."

---

### Q4

**Prompt:** "Which game had the highest combined score (both teams'
points added together)?"

**Response:** February 7 vs. UAlbany, 21–9, combined 30 points.

**Process:** Computed `su_score + opp_score` for all 19 games and took
the max. The next-highest were Cornell (28) and Pitt (28).

**Ground truth:** UAlbany, combined 30.

**Verdict:** ✅ Correct.

---

### Q5 — a deliberate stress question

**Prompt:** "The team stats sheet says Syracuse scored 235 goals this
season. Does that match what you get if you add up every individual
player's goals in the player table?"

**Response (first, "quick" attempt, not actually summing all 31 rows):**
"Yes, that should match — team totals are just the sum of individual
player stats."

**Response (second attempt, after being asked to actually show the
addition row by row):** Summed all 31 players' `goals` values and got
**232**, not 235 — a 3-goal shortfall.

**Ground truth:** Sum of the player rows as transcribed is 232; the
PDF's own team-total row says 235. Both numbers come directly from the
same source PDF — see `DATA_QUALITY_NOTES.md` for the full discussion.
Neither this log nor the ground-truth script "fixes" this by forcing a
match.

**Verdict:** ⚠️ **Instructive failure.** The first, fast answer was
confidently wrong — it asserted a match without actually doing the
arithmetic, which is exactly the "restate a plausible-sounding answer
instead of computing" failure mode the assignment asks us to watch for.
The second answer, forced into showing its work by literally being
asked to sum the column, caught the real discrepancy. **Takeaway:**
for any question requiring aggregation across many rows, explicitly
requesting the row-by-row computation (or, better, code execution)
measurably changed the answer's reliability here.

---

### Q6

**Prompt:** "Which game had the highest attendance, and which had the
lowest?"

**Response:** Highest: March 23 vs. Notre Dame, 3,622. Lowest: April 22
vs. Stanford (neutral site), 0.

**Process:** Scanned the `attendance` column for max and min.

**Ground truth:** matches (not separately printed by
`ground_truth_stats.py` in this version, but directly verifiable from
`su_wlax_2025_games.csv`).

**Verdict:** ✅ Correct, but flagged for a data-interpretation nuance:
an attendance of 0 for a neutral-site game is very likely "not
reported" rather than "literally zero fans," and a good answer should
flag that ambiguity rather than reporting it as a bare fact. The
first-pass response did not flag this ambiguity unprompted — see
Phase B for whether prompting for caveats changes that.

---

### Q7 — testing goals vs. points conflation

**Prompt:** "Who was Syracuse's leading scorer this season?"

**Response:** Ambiguous on purpose — "leading scorer" colloquially
often means goals, but in lacrosse box scores "Pts" (points = goals +
assists) is the standard "scoring" leaderboard column. Answered with
both: "If you mean total points, Emma Ward leads with 76. If you mean
goals specifically, Emma Muchnick leads with 34."

**Ground truth:** Points leader: Emma Ward (76). Goals leader: Emma
Muchnick (34).

**Verdict:** ✅ Correct, and this is the more interesting case: a model
that picks *one* answer without flagging the ambiguity in "leading
scorer" is giving an answer that's defensible either way but
incomplete. This is worth re-testing on other models per the bonus
comparison — a weaker model might just anchor on the first name it
sees at the top of the table (Emma Ward, row 1) regardless of which
column that ranking is actually sorted by.

---

### Q8 — multi-column derived stat (harder)

**Prompt:** "What was Syracuse's record in games decided by exactly one
goal?"

**Response:** 3–2. The one-goal games were: Stanford (W, 14–13),
Clemson (L, 8–9), Notre Dame (W, 12–11), Virginia (W, 13–12), and Yale
on May 11 (L, 8–9).

**Process:** Computed `abs(su_score - opp_score) == 1` for all 19
games by hand, then read off the result for each match.

**Ground truth:** Matches (verifiable directly from
`su_wlax_2025_games.csv`; not yet added as a printed line in
`ground_truth_stats.py` — a good candidate to add if this question
gets reused).

**Verdict:** ✅ Correct. This required combining two columns
(`su_score`, `opp_score`) into a derived condition across all 19 rows —
a step up in difficulty from a single-column lookup, and still handled
correctly here, but it's the kind of question where a bonus multi-model
comparison run would be worth doing since it's genuinely
compute-intensive rather than a lookup.

---

## Observations so far (Phase A)

- **Every single-column lookup question (Q1, Q2, Q4, Q6) was answered
  correctly and instantly** — these aren't good discriminators of
  model quality on their own.
- **The one real failure (Q5) came from skipping the actual arithmetic**,
  not from a conceptual misunderstanding — the model "knew" how to sum
  a column, it just didn't do it until asked twice. This matches the
  assignment's own framing: the interesting failure mode isn't "the
  model can't compute a mean," it's "the model will restate a
  plausible number instead of computing one unless pushed."
- **Ambiguous questions (Q7) are worth asking on purpose** — "leading
  scorer" has no single correct answer in lacrosse without picking
  goals vs. points, and a good response should say so rather than
  guessing which one you meant.
- This log's biggest limitation is the one stated at the top: it is
  not a blind test, since the same model built the ground truth. The
  next concrete step is re-running Q1–Q8 verbatim in a fresh session of
  Claude, plus a session each of ChatGPT and Copilot, and recording
  those as additional columns/entries in this same log for the bonus
  multi-model comparison.
