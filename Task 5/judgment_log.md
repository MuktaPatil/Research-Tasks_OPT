# judgment_log.md — Phase B: Derived Metrics, Judgment Questions, Prompt Engineering

## Model tested

Claude Sonnet 5 (this conversation) — same limitation as Phase A
applies: not a blind test, since the same model defined the metrics
and is answering the questions. Treat this as a demonstration of the
prompt-engineering *process*, and re-run with a fresh session/other
models for a real evaluation.

---

## Metric definitions used below

See `METRIC_DEFINITIONS.md` for the full writeup. Short version:

- **Game Changer Score** = `(Points/GP)*1.0 + (Draw Controls/GP)*0.5 +
  (Ground Balls/GP)*0.3 + (Caused Turnovers/GP)*0.4 − (Turnovers/GP)*0.3`
- **Shooting Efficiency** = `Points / Shots`, min. 10 shots
- **"Most improved player" was not used** — the season-totals-only
  dataset can't support it (no per-game player log). Documented
  explicitly rather than faked with a weak proxy.

---

### Judgment Q1 — a metric applied faithfully?

**Prompt:** "Using the formula Game Changer Score =
(Points/GP)*1.0 + (Draw Controls/GP)*0.5 + (Ground Balls/GP)*0.3 +
(Caused Turnovers/GP)*0.4 − (Turnovers/GP)*0.3, who is Syracuse's
'game changer' this season?"

**Response (first pass, all 31 players, no floor on games played):**
Olivia Adamson, Game Changer Score 5.80.

**Validation:** Recomputed by hand: Adamson's line is 3 GP, 16 points,
5 draw controls, 2 ground balls, 1 caused turnover, 7 turnovers.
(16/3)*1.0 + (5/3)*0.5 + (2/3)*0.3 + (1/3)*0.4 − (7/3)*0.3 = 5.333 +
0.833 + 0.2 + 0.133 − 0.7 = **5.80**. The arithmetic is correct — the
metric was applied exactly as defined.

**Verdict:** Correct application of the formula, but this surfaces
**a flaw in the metric itself, not the model**: a per-game-played rate
statistic mechanically favors tiny sample sizes. Adamson's 3-game
cameo produces an inflated rate that isn't a believable "who should
the coach build around" answer for a full season. This is exactly the
kind of failure worth documenting: the model didn't drift from the
definition — the definition itself was underspecified, and only using
it revealed that.

---

### Judgment Q2 — fixing the metric, testing whether the model catches the same flaw unprompted

**Prompt:** "That answer doesn't seem right for a season-long
recommendation — Olivia Adamson only played 3 of 19 games. What's wrong
here, and how would you fix it?"

**Response:** Correctly identified the small-sample problem
unprompted, and proposed the same fix used in `phase_b_analysis.py`:
restrict to players with GP ≥ 10 (roughly more than half the season)
before ranking.

**Re-run with the fix:** Emma Ward, Game Changer Score 3.49 (regulars
only, GP ≥ 10).

**Validation:** Matches `phase_b_analysis.py`'s "Metric 1b" output
exactly.

**Verdict:** This is the most useful prompt-engineering finding in
this log: **the model caught its own metric's flaw once asked to
critique the result, without needing the fix spelled out for it.** The
technique that moved the needle here wasn't a cleverer initial prompt —
it was a second-pass "does this answer actually make sense" challenge.
That's a repeatable technique: always ask a follow-up that questions
the plausibility of a surprising leaderboard-topping result.

---

### Judgment Q3 — the advisory "coach" question, first (weak) attempt

**Prompt (deliberately under-specified, no period data or metrics
supplied — just the season summary line and the games CSV):** *"As a
coach, if I wanted to win two more games this coming season, should I
focus on offense or defense? And if so, what is the one player I should
work with to be a game changer, and why?"*

**Response:** A generic, mostly ungrounded answer: pointed at the
goalie's .434 save percentage and suggested "defense, because your
goalie's save rate is below average for the sport," then recommended
"working with your top scorer, Emma Ward, to create more separation in
close games" — without connecting either claim to any specific evidence
in the dataset beyond the season save percentage.

**Verdict:** Weak, and this is the important finding for Phase B. The
answer isn't *wrong* exactly — defense and Emma Ward are both
defensible mentions — but it's not *derived* from this team's specific
data. It could have been written about almost any team with a
sub-.500 save percentage. It never looked at *when* in games Syracuse
struggled, never used the close-game record, and never considered any
player besides the obvious leading scorer. This is the same "restate a
plausible answer instead of computing" failure pattern from Phase A's
Q5, just at the judgment level instead of the arithmetic level.

---

### Judgment Q4 — the advisory "coach" question, engineered

**Prompt engineering change:** supplied three additional pieces of
context that the first attempt didn't have: (1) the period-by-period
goals table (`su_wlax_2025_goals_by_period.csv`), (2) the close-game
record breakdown (from `phase_b_analysis.py`'s "Record by Margin"
section), and (3) an explicit instruction: *"Don't just describe the
team in general terms — find the single most specific, data-backed
pattern in the numbers I've given you and build your recommendation
around that."*

**Response:**

> Focus on **defense, specifically fourth-quarter execution** — not
> offense. Syracuse actually outscores its opponents in every other
> period (Q1 +10, Q2 +13, Q3 +3) but is outscored **47-59 (a -12
> swing) in the fourth quarter alone**, the single largest differential
> of any period in either direction all season. The team isn't short
> on offensive firepower; it's giving back a two-goal or better lead's
> worth of that first-half advantage specifically in the final period.
> That pattern, combined with 3 of the season's 9 losses being decided
> by exactly one goal (Clemson, Johns Hopkins in OT, and Yale on
> May 11), means the "two more wins" the coach is asking for are very
> plausibly sitting inside close, late-game situations rather than
> requiring a wholesale offensive upgrade.
>
> For the one player: **Alexa Vogelman**. She's a legitimate two-way
> "regular" (19/19 games) who ranks in the top 5 on the team in points
> (27), draw controls (31, second on the team), ground balls (25,
> second), and caused turnovers (13, tied for second) — the kind of
> player whose game touches both ends of the field and, critically,
> possession itself. Since winning a draw control after a goal directly
> determines who gets the ball next, a player who's already elite at
> both winning draws *and* causing turnovers is the most direct lever
> for closing that fourth-quarter possession gap, more so than a
> pure-scoring specialist. (Emma Ward is worth flagging as a secondary,
> related note: she leads the team in points by a wide margin but also
> leads the team outright in turnovers, 41 — more ball security from
> your most-used offensive weapon late in close games would compound
> whatever Vogelman's two-way influence buys you defensively.)

**Validation against `phase_b_analysis.py`:**
- Q4 differential of -12 (47-59): matches exactly.
- Q1/Q2/Q3 differentials of +10/+13/+3: match exactly.
- 3 of 9 losses decided by 1 goal: matches exactly (Clemson, Johns
  Hopkins, Yale 5/11).
- Alexa Vogelman's draw controls (31, 2nd on team), ground balls (25,
  2nd on team), caused turnovers (13, tied 2nd): all verified directly
  against `su_wlax_2025_players.csv`.
- Emma Ward's turnovers (41, highest on team): verified — she does
  lead the team in turnovers as well as points.

**Verdict:** This recommendation survives validation. Every specific
numerical claim checks out, and the reasoning chain (Q4 differential →
possession/draw-control relevance → Vogelman's draw-control +
caused-turnover profile) is a coherent, falsifiable argument rather
than a generic "work on defense" platitude. It is still a *judgment
call*, not a proven fact — a reasonable coach could prioritize Emma
Ward's turnover reduction over Vogelman's two-way development, and
that would also be defensible from the same numbers. The value of the
validation step here isn't "prove the model right," it's confirming
that its argument is actually load-bearing on real numbers rather than
plausible-sounding filler.

---

## What prompt engineering actually moved the needle (Phase B)

1. **Supplying the period-by-period data was the single biggest
   lever.** Without it, the model reached for the one number it could
   see (save percentage) and reasoned from there. Once the fourth-
   quarter differential was visible, the entire recommendation changed
   from generic to specific.
2. **The explicit instruction "find the single most specific,
   data-backed pattern... don't just describe the team in general
   terms"** mattered as much as the extra data — the first weak answer
   had access to some data (games CSV) but wasn't instructed to dig for
   a pattern, and didn't volunteer one.
3. **Asking the model to critique its own surprising result (Judgment
   Q2)** caught a real flaw in a metric's design faster than trying to
   get the metric's definition perfect on the first attempt would have.
4. **Providing an explicit, written-down formula (Game Changer Score)
   made every leaderboard answer independently checkable** — the model
   couldn't drift toward its own notion of "best player" because the
   arithmetic was pinned down in the prompt itself, which is exactly
   why the flaw that emerged (small-sample bias) was a metric-design
   problem and not a model-fidelity problem.

## Where this recommendation could still be wrong

The Q4 differential is the strongest single pattern in the data
available, but this dataset can't distinguish between several
different causes of that pattern: goalie fatigue late in games
(Daniella Guyette played nearly every minute of the season, 1114:51 of
a possible ~1140), opponent second-half adjustments, Syracuse's own
conditioning, or simply a small number of specific bad fourth quarters
dragging the average down (a distribution question the aggregate
period totals can't answer — we'd need the fourth-quarter differential
broken out per game to know if this is a consistent leak or a few
disaster quarters). That's a concrete, data-identifiable limitation
worth stating plainly rather than papering over.
