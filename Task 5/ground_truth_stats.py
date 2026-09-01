"""
ground_truth_stats.py  (Task 4/5, Phase A)

Computes trustworthy, hand-verifiable descriptive statistics for the
2025 Syracuse Women's Lacrosse season, from data transcribed directly
off the official team stats PDF (2025SUStats.pdf, "as of May 12, 2025").

This is the answer key every LLM answer in prompt_log.md is checked
against. Standard library only.

Usage:
    python ground_truth_stats.py
(expects su_wlax_2025_games.csv, su_wlax_2025_players.csv,
su_wlax_2025_goalies.csv in the current directory)
"""

import csv


def load_games(path="su_wlax_2025_games.csv"):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["su_score"] = int(r["su_score"])
        r["opp_score"] = int(r["opp_score"])
    return rows


def load_players(path="su_wlax_2025_players.csv"):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    int_cols = ["gp", "goals", "assists", "points", "shots",
                "game_winning_goals", "ground_balls", "draw_controls",
                "turnovers", "caused_turnovers"]
    for r in rows:
        for c in int_cols:
            r[c] = int(r[c])
    return rows


def report():
    games = load_games()
    players = load_players()

    print("=" * 70)
    print("GROUND TRUTH: 2025 Syracuse Women's Lacrosse")
    print("=" * 70)

    # --- Season record -----------------------------------------------
    n_games = len(games)
    wins = [g for g in games if g["result"] == "W"]
    losses = [g for g in games if g["result"] == "L"]
    print(f"\nTotal games played: {n_games}")
    print(f"Record: {len(wins)}-{len(losses)}")

    for loc in ("Home", "Away", "Neutral"):
        subset = [g for g in games if g["location"] == loc]
        w = sum(1 for g in subset if g["result"] == "W")
        l = sum(1 for g in subset if g["result"] == "L")
        print(f"  {loc}: {w}-{l} ({len(subset)} games)")

    conf = [g for g in games if g["is_conference"] == "Yes"]
    conf_w = sum(1 for g in conf if g["result"] == "W")
    conf_l = sum(1 for g in conf if g["result"] == "L")
    print(f"  Conference: {conf_w}-{conf_l} ({len(conf)} games)")

    # --- Scoring / margin ----------------------------------------------
    margins_in_wins = [g["su_score"] - g["opp_score"] for g in wins]
    avg_margin_wins = sum(margins_in_wins) / len(margins_in_wins)
    print(f"\nAverage margin of victory in wins: {avg_margin_wins:.2f}"
          f"  (over {len(wins)} wins)")

    margins_in_losses = [g["opp_score"] - g["su_score"] for g in losses]
    avg_margin_losses = sum(margins_in_losses) / len(margins_in_losses)
    print(f"Average margin of defeat in losses: {avg_margin_losses:.2f}"
          f"  (over {len(losses)} losses)")

    combined = [(g["su_score"] + g["opp_score"], g) for g in games]
    combined.sort(key=lambda t: t[0], reverse=True)
    top_combined, top_game = combined[0]
    print(f"\nHighest combined score: {top_combined} "
          f"({top_game['date']} vs {top_game['opponent']}, "
          f"{top_game['su_score']}-{top_game['opp_score']})")

    lowest_combined, low_game = combined[-1]
    print(f"Lowest combined score:  {lowest_combined} "
          f"({low_game['date']} vs {low_game['opponent']}, "
          f"{low_game['su_score']}-{low_game['opp_score']})")

    biggest_win = max(wins, key=lambda g: g["su_score"] - g["opp_score"])
    print(f"\nBiggest margin of victory: {biggest_win['su_score'] - biggest_win['opp_score']} "
          f"({biggest_win['date']} vs {biggest_win['opponent']}, "
          f"{biggest_win['su_score']}-{biggest_win['opp_score']})")

    worst_loss = max(losses, key=lambda g: g["opp_score"] - g["su_score"])
    print(f"Worst loss (largest margin): {worst_loss['opp_score'] - worst_loss['su_score']} "
          f"({worst_loss['date']} vs {worst_loss['opponent']}, "
          f"{worst_loss['su_score']}-{worst_loss['opp_score']})")

    ot_games = [g for g in games if g["overtime"] == "Yes"]
    print(f"\nOvertime games: {len(ot_games)}")
    for g in ot_games:
        print(f"  {g['date']} vs {g['opponent']}: {g['result']} "
              f"{g['su_score']}-{g['opp_score']}")

    # --- Player stats ----------------------------------------------
    print("\n" + "-" * 70)
    print("PLAYER LEADERS")
    print("-" * 70)

    def top(field, n=5):
        ranked = sorted(players, key=lambda p: p[field], reverse=True)
        return ranked[:n]

    for field, label in [("goals", "Goals"), ("assists", "Assists"),
                          ("points", "Points"), ("shots", "Shots"),
                          ("ground_balls", "Ground Balls"),
                          ("draw_controls", "Draw Controls"),
                          ("caused_turnovers", "Caused Turnovers")]:
        print(f"\nTop 5 by {label}:")
        for p in top(field):
            print(f"  {p['player']:<22} {p[field]:>4}  (GP={p['gp']})")

    total_goals = sum(p["goals"] for p in players)
    total_assists = sum(p["assists"] for p in players)
    total_points = sum(p["points"] for p in players)
    print(f"\nSum of individual player goals:   {total_goals}")
    print(f"Sum of individual player assists: {total_assists}")
    print(f"Sum of individual player points:  {total_points}")
    print("NOTE: The PDF's own 'Total' row reports 235 goals / 112 assists "
          "/ 347 points for the team. Summing the individual player rows "
          "as transcribed gives a slightly different total (see "
          "DATA_QUALITY_NOTES.md) -- this is a real discrepancy in the "
          "source PDF/OCR, not a bug in this script, and is documented "
          "rather than silently corrected.")

    # Shooting percentage per player with at least 1 shot
    print("\nTop 5 by shooting percentage (min. 10 shots):")
    shooters = [p for p in players if p["shots"] >= 10]
    for p in sorted(shooters, key=lambda p: p["goals"] / p["shots"],
                     reverse=True)[:5]:
        pct = p["goals"] / p["shots"] * 100
        print(f"  {p['player']:<22} {pct:5.1f}%  ({p['goals']}/{p['shots']})")

    # Points per game (for players with reasonable playing time)
    print("\nTop 5 by points-per-game (min. 10 games played):")
    regulars = [p for p in players if p["gp"] >= 10]
    for p in sorted(regulars, key=lambda p: p["points"] / p["gp"],
                     reverse=True)[:5]:
        ppg = p["points"] / p["gp"]
        print(f"  {p['player']:<22} {ppg:5.2f} ppg  ({p['points']} pts / {p['gp']} gp)")


if __name__ == "__main__":
    report()
