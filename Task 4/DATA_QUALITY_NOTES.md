# DATA_QUALITY_NOTES.md

## Source

All three CSVs in this repo were **hand-transcribed** from
`2025SUStats.pdf` ("2025 Syracuse Women's Lacrosse, Syracuse Combined
Team Statistics, All games (as of May 12, 2025)"). No dataset file is
committed to the repo per the assignment's instructions — see
`README.md` for where to get the original PDF.

## A real discrepancy: player-row sums don't match the PDF's own team total

The PDF's team totals row reports:

- Goals: **235**
- Assists: **112**
- Points: **347**

Summing the individual player rows exactly as printed in the PDF gives:

- Goals: **232** (3 short)
- Assists: **114** (2 over)
- Points: **346** (1 short)

This is not a transcription bug on our end — `ground_truth_stats.py`
sums the `su_wlax_2025_players.csv` rows exactly as entered, and those
rows were copied digit-for-digit from the PDF table. Two explanations
are plausible: (1) the PDF itself has a genuine typo somewhere in one
or more player rows (a single misread digit, e.g. a `34` that should
be `31` or similar, would explain a few-goal gap), or (2) the printed
player table silently omits or double-counts a player relative to the
team total (e.g. a player who left the team mid-season and isn't
listed, or a stat attributed to the team but not to any individual,
such as an own-goal-equivalent rule in lacrosse). We did not "fix" this
by forcing the player sum to match the team total, because doing so
would require guessing which specific number is wrong — that's exactly
the kind of silent correction this assignment's earlier tasks warned
against making without evidence.

**Implication for Phase A/B testing:** any question that asks an LLM to
independently sum player-level goals/assists/points and compare that
sum to the "team total" is a legitimate stress test of the model, not
a trick — the "right" answer depends on which number you're trusting,
and a good answer should surface the discrepancy rather than silently
picking one number.

## Other transcription notes

- `is_conference` was inferred from the PDF's `*` marker next to a
  game's date, and cross-checked against the "CONFERENCE" record row
  (5-4 = 9 games): the 9 games we marked `Yes` match exactly.
- `location` (Home/Away/Neutral) was inferred from the PDF's own
  formatting convention: opponents printed in ALL CAPS with no prefix
  are home games; `at <Opponent>` is away; `vs <Opponent>` is neutral
  site. This was cross-checked against the HOME (5-4=9), AWAY
  (4-4=8), and NEUTRAL (1-1=2) record rows and matches exactly.
- The `Wo2` and `L ot` notations in the PDF (Mar 07 Stanford win in
  double-overtime; Mar 10 Johns Hopkins loss in overtime) were
  transcribed into a boolean `overtime` column plus the result/score
  columns; the "OT2" columns in the period-by-period breakdown tables
  (not transcribed here, since Phase A intentionally keeps the dataset
  small) corroborate this.
- Rankings (e.g. `#7 Maryland`) were pulled into a separate
  `opponent_rank` column rather than left in the opponent name string,
  since a model asked "how many ranked opponents did SU play" needs
  that as a clean, separately-checkable fact.
- Goalie appearance stats (`su_wlax_2025_goalies.csv`) are a small
  separate file since the PDF prints them in a visually distinct table
  with different columns (minutes, GAA, save %) than the main player
  table.
