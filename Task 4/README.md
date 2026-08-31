# Task_05_Descriptive_Stats — Phase A

From Ground Truth to LLM Judgment: 2025 Syracuse Women's Lacrosse.

**This repo currently covers Phase A only.** Phase B (derived metrics,
judgment questions, the advisory "coach" question) will be added as a
follow-up once Phase A's ground truth and baseline log are locked in —
per the assignment, that's the intended pacing across reporting
periods.

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

See `DATA_QUALITY_NOTES.md` for exactly how ambiguous fields (home vs.
away, conference vs. non-conference) were inferred and cross-checked,
and for a real, documented discrepancy: summing the player table's
individual goals/assists/points does **not** exactly match the PDF's
own printed team totals.

## Reproducing the ground truth

```bash
python ground_truth_stats.py
```

No dependencies beyond the Python standard library. This prints season
record (overall/home/away/neutral/conference), scoring margins, the
highest/lowest combined-score games, overtime games, and player
leaderboards across goals/assists/points/shots/ground balls/draw
controls/caused turnovers, plus shooting percentage and points-per-game
for regulars. Its output is saved in `ground_truth_output.txt` for
reference — this is the answer key `prompt_log.md` is checked against.

## Experiment narrative (Phase A)

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

## What succeeded, what failed

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

## Files in this repo

| File | Purpose |
|---|---|
| `su_wlax_2025_games.csv` | Transcribed schedule/results |
| `su_wlax_2025_players.csv` | Transcribed player stats |
| `su_wlax_2025_goalies.csv` | Transcribed goalie stats |
| `ground_truth_stats.py` | Computes the answer key |
| `ground_truth_output.txt` | Saved output of the script above |
| `DATA_QUALITY_NOTES.md` | How ambiguous fields were resolved; the goals-sum discrepancy |
| `prompt_log.md` | Phase A prompt-and-response log against the answer key |
