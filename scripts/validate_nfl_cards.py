"""Gate for the weekly NFL cards refresh: fail loudly instead of publishing bad cards."""
import collections
import json
import sys

from src.db import ROOT, query
import datetime

from src.reports.nfl_cards import SEASON, latest_week, schedule_week, week_status

d = json.loads((ROOT / "reports" / "cards" / "nfl_players.json").read_text())
m, cards = d["meta"], d["cards"]
fail = []

want = latest_week()
if m["week"] != want:
    fail.append(f"cards are through Week {m['week']} but the newest complete week is {want}")
# the schedule says a week is over, but its stats still haven't posted a day after the week ended: the cards would quietly stall
today = datetime.date.today()
st = week_status()
sw = schedule_week(st)
if sw > m["week"] and (today - st[sw]["ends"]).days >= 1:
    fail.append(f"Week {sw} ended {st[sw]['ends']} and its games are final, but the cards are still through Week {m['week']}: "
                "nflverse hasn't posted every game's box score, snap counts and play-by-play yet. Re-run once it has")
# a week whose window closed 3+ days ago but still has unfinished games would freeze the cards without anyone noticing
for w, s in sorted(st.items()):
    if w > m["week"] and s["open"] and (today - s["ends"]).days >= 3:
        fail.append(f"Week {w} ended {s['ends']} but {s['open']} still have no final score: cancelled, rescheduled without a new "
                    "date, or not loaded yet. Check the schedule; the cards can't move past it until it's settled")
        break
if len(m["dropped"]) > 3:   # a few brand-new signings can be missing a name or position for a day; more means something broke
    fail.append(f"{len(m['dropped'])} players dropped: {m['dropped'][:5]}")
elif m["dropped"]:
    print(f"note: {len(m['dropped'])} players dropped (allowed up to 3): {m['dropped']}")
if len(m["unlinked"]) > 10:
    fail.append(f"{len(m['unlinked'])} snap-count players couldn't be linked")
if m["pfr_week"] < m["week"] - 2:
    fail.append(f"game charting is through Week {m['pfr_week']}, more than two weeks behind Week {m['week']}")
ids = [c["id"] for c in cards]
if len(ids) != len(set(ids)):
    fail.append("duplicate cards")
per_team = collections.Counter(c["team"] for c in cards)
if len(per_team) != 32 or min(per_team.values()) < 45:
    fail.append(f"team coverage looks wrong: {len(per_team)} teams, smallest has {min(per_team.values())} cards")
if not 2000 <= len(cards) <= 3200:
    fail.append(f"{len(cards)} cards is outside the expected range")
# every player with a box-score line through the week has a card
box = set(query(f"SELECT DISTINCT player_id FROM raw_player_week WHERE season={SEASON} AND season_type='REG' AND week<={m['week']} "
                "AND player_id IS NOT NULL").player_id)
missing = box - set(ids)
if missing:
    fail.append(f"{len(missing)} players with stats this season have no card: {sorted(missing)[:5]}")
# the kicking splits add up
bad = [c["name"] for c in cards if c["fg_u40"][1] + c["fg_40"][1] + c["fg_50"][1] != c["fg_att"]]
if bad:
    fail.append(f"field-goal distance splits don't add up for {bad[:5]}")

print(f"NFL cards through Week {m['week']} (charting {m['pfr_week']}, rosters Week {m['roster_week']}): {len(cards)} cards"
      + (f"; postponed: {m['postponed']}" if m["postponed"] else ""))
if fail:
    sys.exit("VALIDATION FAILED:\n- " + "\n- ".join(fail))
print("validation passed")
