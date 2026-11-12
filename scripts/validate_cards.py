"""Gate for the daily cards refresh: fail loudly instead of publishing bad cards."""
import json
import sys

from src.db import ROOT, query

C = ROOT / "reports" / "cards"
sk = json.loads((C / "skaters_league.json").read_text())
gl = json.loads((C / "goalies_league.json").read_text())
m, cards, gcards = sk["meta"], sk["cards"], gl["cards"]
fail = []
season = 20262027
as_of = m["as_of"]

ros = query(f"""SELECT DISTINCT r.player_id, r.pos FROM raw_nhl_rosters r JOIN raw_nhl_games g ON g.game_id = r.game_id
                WHERE g.season = {season} AND g.game_date <= '{as_of}'""")
n_sk = ros[ros.pos != "G"].player_id.nunique()
if m["goal_check"]["mismatches"]:
    fail.append(f"goal totals disagree with the feed for {m['goal_check']['mismatches']} players")
if len(cards) != n_sk:
    fail.append(f"{len(cards)} skater cards but {n_sk} skaters dressed")
if len({c['id'] for c in cards}) != len(cards) or len({c['id'] for c in gcards}) != len(gcards):
    fail.append("duplicate player cards")
if len({c['team'] for c in cards}) != 32 or len(m["teams"]) != 32:
    fail.append("not all 32 teams have cards")
ng = query(f"SELECT COUNT(*) n FROM raw_nhl_games WHERE season = {season} AND game_date <= '{as_of}'").n[0]
if sum(m["teams"].values()) != 2 * ng:
    fail.append(f"team games sum {sum(m['teams'].values())} != 2 x {ng} games")
if not 0.85 <= m["cal"] <= 1.15:
    fail.append(f"xG rescale factor {m['cal']} out of range")
if len(gcards) < 50:
    fail.append(f"only {len(gcards)} goalie cards")
if any(c.get("rate_p82") is None for c in cards if c["gp"] >= 5):
    fail.append("skaters with 5+ games missing a rating")

print(f"cards through {as_of}: {len(cards)} skaters, {len(gcards)} goalies, {ng} games")
if fail:
    sys.exit("VALIDATION FAILED:\n- " + "\n- ".join(fail))
print("validation passed")
