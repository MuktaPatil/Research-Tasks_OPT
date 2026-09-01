# Task_05_Descriptive_Stats

From Ground Truth to LLM Judgment: 2025 Syracuse Women's Lacrosse.
**Both Phase A and Phase B are covered in this repo.**

## Dataset

**Source:** `2025SUStats.pdf` — "2025 Syracuse Women's Lacrosse,
Syracuse Combined Team Statistics, All games (as of May 12, 2025)",
Syracuse Athletics' official team stats sheet.

**Where to get it:** This PDF is not included in this repo. It's the
kind of public team-stats PDF Syracuse Athletics posts each season —
search "2025 Syracuse women's lacrosse combined team statistics" on
cuse.com, or use the assignment's suggested source
(https://cuse.com/sports/2013/1/16/WLAX_0116134638, which links to the
current season's stats page). Place the downloaded PDF in the repo root
as `2025SUStats.pdf` if you want to re-verify the transcription
yourself.

**What's in this repo instead of the PDF:** three small CSVs,
hand-transcribed from the PDF:

- `su_wlax_2025_games.csv` — 19 games: date, opponent, opponent rank
  (if ranked), home/away/neutral, conference flag, result, score,
  overtime flag, attendance.
- `su_wlax_2025_players.csv` — 31 players: games played, goals,
  assists, points, shots, game-winning goals, ground balls, draw
  controls, turnovers, caused turnovers.
- `su_wlax_2025_goalies.csv` — 2 goalies: minutes, goals against, GAA,
  saves, save %, record.
- `su_wlax_2025_goals_by_period.csv` — team goals scored/allowed per
  quarter (Q1-Q4, OT, OT2), used for the Phase B "coach" analysis.

See `DATA_QUALITY_NOTES.md` for exactly how ambiguous fields (home vs.
away, conference vs. non-conference) were inferred and cross-checked,
and for a real, documented discrepancy: summing the player table's
individual goals/assists/points does **not** exactly match the PDF's
own printed team totals.

## Reproducing the ground truth

```bash
python ground_truth_stats.py     # Phase A: season/player descriptive stats
python phase_b_analysis.py       # Phase B: derived metrics + quarter-by-quarter analysis
```

No dependencies beyond the Python standard library. `ground_truth_stats.py`
prints season record (overall/home/away/neutral/conference), scoring
margins, the highest/lowest combined-score games, overtime games, and
player leaderboards across goals/assists/points/shots/ground
balls/draw controls/caused turnovers, plus shooting percentage and
points-per-game for regulars — saved in `ground_truth_output.txt`.
`phase_b_analysis.py` computes the Game Changer Score and Shooting
Efficiency metrics (see `METRIC_DEFINITIONS.md`), the close-game
record breakdown, and the quarter-by-quarter scoring differential that
Phase B's coach recommendation is built on — saved in
`phase_b_output.txt`. Together these are the answer key `prompt_log.md`
and `judgment_log.md` are checked against.

## Experiment narrative — Phase A: Ground Truth and Baseline Q&A

1. **Chose the dataset.** Picked the assignment's suggested category —
   a single SU sports season — and specifically women's lacrosse's 2025
   season, since the official stats PDF is compact (19 games, 31
   players) and unambiguous.
2. **Transcribed it by hand** rather than trying to OCR/scrape the PDF
   programmatically, specifically so every value could be manually
   cross-checked against the PDF's own summary rows (overall record,
   conference record, home/away/neutral splits, team goal/assist/point
   totals) before treating it as ground truth. Every cross-check passed
   except one: the player-level goal/assist/point sums don't match the
   PDF's own team totals row (see `DATA_QUALITY_NOTES.md`).
3. **Built `ground_truth_stats.py`**, reusing the same pure-Python,
   standard-library-only approach from earlier tasks in this series, to
   compute an answer key I trust because I can read every line of the
   code that produced it.
4. **Ran a baseline Q&A pass** (`prompt_log.md`) — 8 factual questions,
   moving from trivial row-counts up to a genuine cross-column derived
   question (record in one-goal games) and a deliberate stress question
   about whether individual player stats sum to the team total.

## Experiment narrative — Phase B: Derived Metrics and Judgment Questions

1. **Considered the assignment's example metric ("most improved
   player," first-half vs. second-half PPG) and rejected it explicitly**
   — the source data only has season totals per player, no per-game
   player log, so that metric can't be honestly computed here. This is
   documented in `METRIC_DEFINITIONS.md` rather than faked with a weak
   proxy.
2. **Defined two metrics that the available data actually supports**:
   a "Game Changer Score" (a weighted combination of points, draw
   controls, ground balls, caused turnovers, and turnovers, all rated
   per game played) and "Shooting Efficiency" (points per shot, with a
   minimum-shots floor). Both formulas are written out explicitly in
   `METRIC_DEFINITIONS.md` so any answer using them is independently
   checkable.
3. **Ran the Game Changer Score and immediately hit a real flaw**: a
   3-game player (Olivia Adamson) topped the leaderboard purely because
   a per-game-played rate statistic rewards tiny samples. Rather than
   quietly patching the formula before showing it, `judgment_log.md`
   documents the flawed first result, the follow-up question that
   surfaced the problem, and the fix (a GP ≥ 10 floor).
4. **Built the "coach" advisory question in two passes.** The first
   pass, given only the season summary and games list, produced a
   generic, barely-data-grounded answer. The second pass, given the
   quarter-by-quarter scoring breakdown plus an explicit instruction to
   find a specific pattern, produced a materially different and fully
   validated recommendation: Syracuse outscores opponents in every
   quarter except the fourth (-12 differential, the largest of any
   period), and the two-way regular best positioned to help close that
   gap is Alexa Vogelman, based on her draw-control and caused-turnover
   profile. Every specific claim in that answer was independently
   re-checked against `phase_b_analysis.py`'s output.

## What succeeded, what failed — Phase A

**Succeeded:** every single-column lookup (game count, top scorer,
highest combined score, attendance extremes) and even a two-column
derived question (record in one-goal games) were answered correctly
when reasoned through carefully.

**Failed, instructively:** asked casually whether player-level goals
summed to the team's reported total, the first-pass answer asserted
"yes" without actually doing the addition — a confidently wrong answer
that only got corrected when explicitly asked to show the row-by-row
sum. This is the single most useful finding from this pass: **the
model's failure mode here wasn't a missing capability, it was skipping
the computation it was fully capable of doing**, and it took an
explicit instruction to force the real calculation.

**A real limitation of this specific pass:** the log's Q&A was
conducted by the same model instance that built the ground truth,
which is not a genuinely blind test. The next step (noted in
`prompt_log.md`) is re-running the same 8 prompts in a fresh session
and, ideally, in ChatGPT and Copilot as well, to get an honest
multi-model comparison.

## What succeeded, what failed — Phase B

**Succeeded:** once given the quarter-by-quarter data and an explicit
instruction to find a specific pattern rather than describe the team
generically, the model produced a coach recommendation that held up
completely under validation — every specific number cited (the -12
Q4 differential, the 3 one-goal losses, Alexa Vogelman's draw-control
and caused-turnover totals, Emma Ward's turnover total) checked out
exactly against `phase_b_analysis.py`.

**Failed, instructively (twice):** (1) the first, unprompted "coach"
answer was generic and barely used the actual dataset — it reached for
the one obviously-visible number (save percentage) instead of digging
for a pattern, until explicitly told to. (2) The Game Changer Score's
first-pass leaderboard was topped by a 3-game player due to a genuine
flaw in the metric's own design (a per-game rate statistic rewarding
tiny samples) — caught not by a smarter initial prompt, but by asking
the model to critique its own surprising result on a follow-up turn.

**Biggest Phase B takeaway:** the gap between a weak, generic
"coaching" answer and a specific, validated one was almost entirely
about what data was supplied and whether the model was explicitly told
to look for a pattern — not about the model's underlying reasoning
capability. The same model produced a defensible, data-grounded
recommendation once given the right inputs and the right instruction.

**Same blind-test caveat as Phase A applies** — this was not tested
against a fresh/independent model instance. See the bonus multi-model
comparison suggestion in `prompt_log.md`.

## Files in this repo

| File | Purpose |
|---|---|
| `su_wlax_2025_games.csv` | Transcribed schedule/results |
| `su_wlax_2025_players.csv` | Transcribed player stats |
| `su_wlax_2025_goalies.csv` | Transcribed goalie stats |
| `su_wlax_2025_goals_by_period.csv` | Quarter-by-quarter scoring (Phase B) |
| `ground_truth_stats.py` | Phase A answer key |
| `ground_truth_output.txt` | Saved output of the script above |
| `phase_b_analysis.py` | Phase B derived-metrics answer key |
| `phase_b_output.txt` | Saved output of the script above |
| `METRIC_DEFINITIONS.md` | Explicit formulas for Game Changer Score and Shooting Efficiency; why "most improved" wasn't used |
| `DATA_QUALITY_NOTES.md` | How ambiguous fields were resolved; the goals-sum discrepancy |
| `prompt_log.md` | Phase A prompt-and-response log against the answer key |
| `judgment_log.md` | Phase B prompt-engineering log, metric flaws, and the validated coach recommendation |
