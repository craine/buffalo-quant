"""Gate for the daily cards refresh: fail loudly instead of publishing bad cards."""
import argparse
import datetime as dt
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
DONE = "game_state IN ('OFF', 'FINAL')"
ng = query(f"SELECT COUNT(*) n FROM raw_nhl_games WHERE season = {season} AND game_date <= '{as_of}' AND {DONE}").n[0]
n_open = query(f"SELECT COUNT(*) n FROM raw_nhl_games WHERE season = {season} AND game_date <= '{as_of}' AND NOT {DONE}").n[0]
if n_open:
    fail.append(f"{n_open} unfinished games on or before {as_of} in the data")
latest = query(f"SELECT MAX(game_date) d FROM raw_nhl_games WHERE {DONE}").d.iloc[0]
if as_of != latest:
    fail.append(f"cards are through {as_of} but the data has games through {latest}")
today = dt.date.today()
# season is under way (this season has games) and it's not summer; 7 days covers the holiday and All-Star breaks
in_season = today.month in (10, 11, 12, 1, 2, 3, 4) and ng > 0
if in_season and (today - dt.date.fromisoformat(latest)).days > 7:
    fail.append(f"newest completed game is {latest}, more than 7 days old: the NHL ingest may be stale")
if sum(m["teams"].values()) != 2 * ng:
    fail.append(f"team games sum {sum(m['teams'].values())} != 2 x {ng} games")
if not 0.85 <= m["cal"] <= 1.15:
    fail.append(f"xG rescale factor {m['cal']} out of range")
if len(gcards) < 50:
    fail.append(f"only {len(gcards)} goalie cards")
if any(c.get("rate_p82") is None for c in cards if c["gp"] >= 5):
    fail.append("skaters with 5+ games missing a rating")

FP = ROOT / "config" / "xg_fingerprint.json"
now = query("SELECT season, SUM(xg) xg, COUNT(xg) n FROM clean_nhl_shots_xg WHERE season < 20262027 GROUP BY season")
ap = argparse.ArgumentParser()
ap.add_argument("--update-fingerprint", action="store_true",
                help="after a deliberate change (NHL edited old play-by-play, model or library change): record the current totals")
if ap.parse_args().update_fingerprint:
    doc = json.loads(FP.read_text())
    doc["seasons"] = {str(int(x.season)): {"xg_sum": round(float(x.xg), 6), "n": int(x.n)} for x in now.itertuples()}
    FP.write_text(json.dumps(doc, indent=1))
    print("fingerprint updated:", doc["seasons"])
fpr = json.loads(FP.read_text())["seasons"]
for x in now.itertuples():
    ref = fpr.get(str(int(x.season)))
    if ref is None or ref["n"] != x.n or abs(ref["xg_sum"] - x.xg) > 1e-3:
        fail.append(f"shot model changed for {x.season}: xG {x.xg:.3f} on {x.n} shots vs. fingerprint {ref}")

print(f"cards through {as_of}: {len(cards)} skaters, {len(gcards)} goalies, {ng} games")
if fail:
    sys.exit("VALIDATION FAILED:\n- " + "\n- ".join(fail))
print("validation passed")
