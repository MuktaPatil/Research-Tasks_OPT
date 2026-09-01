# METRIC_DEFINITIONS.md — Phase B

## Why "most improved player" isn't used here

The assignment's example — largest positive change in points-per-game
between the first and second half of the season — requires a **game
log per player** (points broken out by game, or at least by half of
season). The source PDF only publishes **season totals per player**;
it has no per-game player breakdown at all. Computing "most improved"
from season totals alone would mean inventing a proxy that isn't
actually measuring improvement (e.g. comparing GP to points, which
measures playing time, not trend). Rather than force a metric the data
can't actually support, this task uses two different qualitative
concepts that season-total data *can* legitimately measure, defined
explicitly below.

## Metric 1: Two-Way Impact Score ("Game Changer Score")

**Concept:** which player affects the game most broadly — not just
scoring, but puck (ball) possession and defensive disruption — per game
played, so it's fair to both a 19-game full-season player and someone
who only played a handful of games.

**Formula:**

```
Game Changer Score =
    (Points / GP) * 1.0
  + (Draw Controls / GP) * 0.5
  + (Ground Balls / GP) * 0.3
  + (Caused Turnovers / GP) * 0.4
  - (Turnovers / GP) * 0.3
```

**Why these weights:** Points get the highest weight (1.0) because
scoring output is the most direct way to affect a lacrosse game's
outcome. Draw controls (0.5) matter because in lacrosse, winning a draw
control after every goal directly determines who gets the next
possession — a high-draw-control player extends the team's number of
offensive chances independent of their own scoring. Ground balls (0.3)
and caused turnovers (0.4) both measure defensive/possession
disruption; caused turnovers get a higher weight than ground balls
because forcing a turnover is a more decisive, player-driven event than
recovering a loose ball. Turnovers are subtracted (-0.3, a smaller
penalty than any of the positive weights) to penalize live-ball
giveaways without letting a high-usage offensive player's score be
wiped out by a handful of turnovers that come with heavy usage.

**This is one explicit, defensible weighting — not the only one.** A
coach who cared more about raw scoring could weight points at 2.0; a
defense-focused coach could double the caused-turnover weight. The
point of writing the formula down is that any LLM answer using this
metric can be checked against the exact same arithmetic, not a vibe.

## Metric 2: Shooting Efficiency (points per shot)

**Concept:** who converts their scoring chances most efficiently,
independent of raw volume — a different, narrower concept than "best
player," useful for a specific kind of coaching decision (who should
take the last-second shot vs. who generates the most total offense).

**Formula:** `Points / Shots`, restricted to players with at least 10
shots on the season (to exclude small-sample outliers — e.g. a player
with 1 shot and 1 goal would otherwise "lead" at 100%).

## Metric 3: Fourth-Quarter Defensive Differential (team-level, not per-player)

**Concept:** rather than a player-level metric, this measures *when*
in games Syracuse's performance relative to opponents changes, which
turned out to be the single most important finding for the Phase B
coach question below.

**Formula:** `SU goals scored in period P` − `Opponent goals scored in
period P`, computed separately for Q1, Q2, Q3, Q4, OT, and OT2, from
`su_wlax_2025_goals_by_period.csv`.
