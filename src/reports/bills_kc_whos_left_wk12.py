"""Bills-Chiefs series, part 2 (Nov. 24, 2026): who's left from the January 2025 AFC Championship Game.

For each team, every player who played at least half the offensive or defensive snaps in that game (2024_21_BUF_KC), and
where he is in 2026: same team, another team, or no snaps this season.

Writes reports/2026-wk12-kc-whos-left.md, one PNG (bills-kc-wk12-whos-left.png) and a hero JSON.

Sources and pins: PFR snap counts via nflverse (raw_snap_counts), 2026 regular season through Week 11 (games loaded when this
ran, pinned below). Weekly rosters (raw_rosters_weekly) for players with no 2026 snaps. Targets from nflverse play-by-play.
Coaching staffs from team announcements and reporting (cited in the story).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk11_postgame import finish

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-whos-left"
PNG = "bills-kc-wk12-whos-left.png"
GAME = "2024_21_BUF_KC"
WK = 11
ROSTER_WK = 12                             # latest weekly roster when this ran
SNAP_GAMES_2026 = 162                      # 2026 regular-season games in the snap counts when this ran (weeks 1-11)
KC_RED = "#E31837"
TEAM = {"NO": "New Orleans", "NE": "New England", "PHI": "Philadelphia", "WAS": "Washington", "LV": "Las Vegas", "ATL": "Atlanta",
        "CHI": "Chicago", "CIN": "Cincinnati", "LA": "the Rams", "LAC": "the Chargers", "BUF": "Buffalo", "KC": "Kansas City"}
SRC_NOTE = "Source: Pro Football Reference snap counts via nflverse; nflverse weekly rosters and play-by-play."


def poss(name):
    return name + ("'" if name.endswith("s") else "'s")


def where(r):
    """Plain-English 'where is he now' for a player not still with his team."""
    t = TEAM.get(r.now, r.now)
    if r.status == "other":
        return f"{t}{', injured reserve' if r.r_status == 'RES' else ''}"
    if r.status == "released":
        return f"released by {TEAM.get(r.r_team, r.r_team)}"
    if r.status == "practice":
        return f"{poss(TEAM.get(r.r_team, r.r_team))} practice squad"
    return "hasn't played this season"


def status_table():
    c = query(f"SELECT * FROM raw_snap_counts WHERE game_id = '{GAME}'")
    c = c[(c.offense_pct >= 0.5) | (c.defense_pct >= 0.5)].copy()
    c["side"] = c.offense_pct.ge(0.5).map({True: "Offense", False: "Defense"})
    s = query(f"""SELECT pfr_player_id, team, SUM(offense_snaps + defense_snaps) AS snaps, COUNT(*) AS g, MAX(week) AS last_wk
                  FROM raw_snap_counts WHERE season = 2026 AND game_type = 'REG' AND week <= {WK} GROUP BY 1, 2""")
    s = s[s.snaps > 0]
    latest = s.sort_values("last_wk").groupby("pfr_player_id").tail(1).set_index("pfr_player_id")
    same = set(zip(s.pfr_player_id, s.team))
    now = [t if (p, t) in same else (str(latest.team[p]) if p in latest.index else "") for p, t in zip(c.pfr_player_id, c.team)]
    c["status"] = ["same" if n == t else ("other" if n else "none") for n, t in zip(now, c.team)]
    c["g26"] = [int(s[(s.pfr_player_id == p) & (s.team == n)].g.sum()) if n else 0 for p, n in zip(c.pfr_player_id, now)]
    c["now"] = now
    # latest weekly roster: released, practice squad, injured reserve
    ro = query(f"""SELECT pfr_id, team, status, week FROM raw_rosters_weekly WHERE season = 2026 AND week <= {ROSTER_WK}""")
    last = ro.sort_values("week").groupby("pfr_id").tail(1).set_index("pfr_id")
    c["r_status"] = [str(last.status[p]) if p in last.index else "" for p in c.pfr_player_id]
    c["r_team"] = [str(last.team[p]) if p in last.index else "" for p in c.pfr_player_id]
    c.loc[(c.r_status == "CUT") & (c.status != "same"), "status"] = "released"
    c.loc[(c.r_status == "DEV") & (c.status == "none"), "status"] = "practice"
    # display position: the game's PFR position, with every defensive back shown as DB (PFR listed safety Cole Bishop as CB)
    c["pos"] = ["DB" if q in ("CB", "S", "FS", "SS", "DB") else q for q in c.position]
    return c


def main():
    n_games = query(f"SELECT COUNT(DISTINCT game_id) n FROM raw_snap_counts WHERE season = 2026 AND game_type = 'REG' AND week <= {WK}").n.iloc[0]
    sched = query(f"SELECT game_id FROM raw_schedules WHERE season = 2026 AND game_type = 'REG' AND week <= {WK}")
    snapped = set(query(f"SELECT DISTINCT game_id FROM raw_snap_counts WHERE season = 2026 AND week <= {WK}").game_id)
    missing = sorted(set(sched.game_id) - snapped)
    assert n_games == SNAP_GAMES_2026 and missing == ["2026_11_CIN_WAS"]
    gm = query(f"SELECT home_team, away_team, home_score, away_score, gameday FROM raw_schedules WHERE game_id = '{GAME}'").iloc[0]
    assert (gm.home_team, gm.home_score, gm.away_score) == ("KC", 32, 29)
    c = status_table()
    cnt = c.groupby(["team", "side", "status"]).size().unstack(fill_value=0)
    tot = c.groupby(["team", "status"]).size().unstack(fill_value=0)
    nb, nk = int(tot.loc["BUF"].sum()), int(tot.loc["KC"].sum())
    sb, sk = int(tot.loc["BUF", "same"]), int(tot.loc["KC", "same"])
    assert (nb, sb, nk, sk) == (21, 13, 23, 12)
    assert list(c[c.status == "released"].player) == ["Justin Reid"] and list(c[c.status == "practice"].player) == ["Kaiir Elam"]
    assert c.loc[c.player == "Cole Bishop", "pos"].iloc[0] == "DB"
    bo, bd = cnt.loc[("BUF", "Offense")], cnt.loc[("BUF", "Defense")]
    ko, kd = cnt.loc[("KC", "Offense")], cnt.loc[("KC", "Defense")]

    db_pos = {"CB", "SS", "FS", "S", "DB"}
    sec = c[c.position.isin(db_pos)]
    sec_t = sec.groupby(["team", "status"]).size().unstack(fill_value=0)
    gone_sec = {t: sec[(sec.team == t) & (sec.status != "same")].player.tolist() for t in ("BUF", "KC")}
    assert len(gone_sec["KC"]) == 4 and len(gone_sec["BUF"]) == 3

    # players with no 2026 snaps: on any 2026 roster?
    none = c[c.status == "none"].copy()
    ro = query(f"SELECT pfr_id, team, status, week FROM raw_rosters_weekly WHERE season = 2026 AND week <= {WK}")
    on_roster = set(ro.pfr_id.dropna())
    none["rostered"] = none.pfr_player_id.isin(on_roster)

    # a Chief who's now a Bill
    switch = c[(c.team == "KC") & (c.now == "BUF")]
    assert len(switch) == 1
    sw = switch.iloc[0]

    # targets: then and now
    def targets(cond):
        return query(f"""SELECT pl.display_name AS name, p.receiver_player_id AS id, COUNT(*) AS tg FROM raw_pbp p
                         JOIN raw_players pl ON pl.gsis_id = p.receiver_player_id
                         WHERE {cond} AND p.pass_attempt = 1 AND p.sack = 0 AND COALESCE(p.two_point_attempt, 0) = 0
                           AND p.play_type <> 'no_play' AND p.receiver_player_id IS NOT NULL
                         GROUP BY 1, 2 ORDER BY tg DESC, name""")
    kt_then = targets(f"p.game_id = '{GAME}' AND p.posteam = 'KC'")
    kt_now = targets(f"p.season = 2026 AND p.season_type = 'REG' AND p.week <= {WK} AND p.posteam = 'KC'")
    bt_then = targets(f"p.game_id = '{GAME}' AND p.posteam = 'BUF'")
    bt_now = targets(f"p.season = 2026 AND p.season_type = 'REG' AND p.week <= {WK} AND p.posteam = 'BUF'")
    k_tot, b_tot = int(kt_now.tg.sum()), int(bt_now.tg.sum())
    k_top = kt_now.head(5).copy()
    k_top["share"] = k_top.tg / k_tot
    k_top["in_game"] = k_top.id.isin(set(kt_then.id))
    b_top = bt_now.head(5).copy()
    b_top["share"] = b_top.tg / b_tot
    b_top["in_game"] = b_top.id.isin(set(bt_then.id))
    k_new_share = float(k_top[~k_top.in_game].tg.sum() / k_tot)
    k_then_now = kt_then[kt_then.id.isin(set(kt_now.id))]
    k_then_share_now = float(kt_now[kt_now.id.isin(set(kt_then.id))].tg.sum() / k_tot)
    b_then_share_now = float(bt_now[bt_now.id.isin(set(bt_then.id))].tg.sum() / b_tot)

    # ---- chart: two rosters
    col = {"same": None, "other": GRAY, "none": "#D5D8DE"}
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 8.6), dpi=200)
    for ax, team, tcol, lab in ((axes[0], "BUF", BLUE, "Bills"), (axes[1], "KC", KC_RED, "Chiefs")):
        d = c[c.team == team].copy()
        d["o"] = d.status.map({"same": 0, "other": 1, "released": 2, "practice": 2, "none": 3})
        d = d.sort_values(["side", "o", "player"], ascending=[False, True, True])
        y = 0
        ax.set_xlim(0, 1); ax.axis("off")
        same_n = int((d.status == "same").sum())
        ax.text(0, 1.0, f"{lab}: {same_n} of {len(d)} still with the team", transform=ax.transAxes, fontsize=13, fontweight="bold", color=tcol, va="top")
        rows = []
        for side in ("Offense", "Defense"):
            rows.append(("hdr", side))
            rows += [("p", r) for r in d[d.side == side].itertuples()]
        n = len(rows)
        for i, (kind, r) in enumerate(rows):
            yy = 0.93 - i * (0.9 / n)
            if kind == "hdr":
                ax.text(0, yy, r.upper(), fontsize=9, color=MUTED, fontweight="bold", transform=ax.transAxes, va="center")
                continue
            c_ = tcol if r.status == "same" else col.get(r.status, col["none"])
            ax.add_patch(plt.Rectangle((0.0, yy - 0.013), 0.025, 0.026, color=c_, transform=ax.transAxes, clip_on=False))
            ax.text(0.04, yy, f"{r.player}", fontsize=9.5, color=INK, transform=ax.transAxes, va="center")
            ax.text(0.40, yy, r.pos, fontsize=8.5, color=MUTED, transform=ax.transAxes, va="center")
            ir = " (injured reserve)" if r.r_status == "RES" else ""
            now = {"same": f"Still a {lab[:-1]}{ir}", "other": f"Now with {TEAM.get(r.now, r.now)}{ir}", "none": "Hasn't played this season",
                   "released": f"Released by {TEAM.get(r.r_team, r.r_team)}", "practice": f"On {poss(TEAM.get(r.r_team, r.r_team))} practice squad"}[r.status]
            ax.text(0.52, yy, now, fontsize=9, color=INK if r.status == "same" else MUTED, transform=ax.transAxes, va="center")
    finish(fig, "Who's left from the January 2025 AFC title game",
           f"Every player on at least half his team's offensive or defensive snaps in Kansas City's 32-29 win, and where he is now.",
           f"{SRC_NOTE} 2026: regular season through Week {WK}'s Sunday games; rosters as of Week {ROSTER_WK}. \"Now with\" = his most recent 2026 team with snaps.")
    fig.texts[-1].set_text(fig.texts[-1].get_text().replace(
        "Source: nflverse play-by-play and schedules (completion chance: nflverse model). Regular season.\n", ""))
    fig.savefig(OUT / PNG)
    plt.close(fig)

    def names(t, st):
        return ", ".join(c[(c.team == t) & (c.status == st)].sort_values("player").player)

    def joinl(items):
        items = list(items)
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]

    def gone(t, side):
        d = c[(c.team == t) & (c.side == side) & (c.status != "same")].sort_values("player")
        return joinl(f"{r.player} ({where(r)})" for r in d.itertuples())

    def gone_db(t, db=True):
        d = c[(c.team == t) & (c.side == "Defense") & (c.status != "same") & (c.position.isin(db_pos) == db)].sort_values("player")
        return joinl(f"{r.player} ({where(r)})" for r in d.itertuples())

    months = (2026 - pd.Timestamp(gm.gameday).year) * 12 + (11 - pd.Timestamp(gm.gameday).month)
    assert months == 22

    def kept(t, side):
        return set(c[(c.team == t) & (c.side == side) & (c.status == "same")].player)

    # every name the text states as still with the team
    assert {"Josh Allen"} <= kept("BUF", "Offense")
    ol = c[(c.team == "BUF") & c.position.isin(["T", "G", "C"])]
    ol_back = int((ol.status == "same").sum())
    assert len(ol) == 5 and ol_back == 4
    assert {"Patrick Mahomes", "Travis Kelce", "Xavier Worthy", "Creed Humphrey"} <= kept("KC", "Offense")
    assert {"Chris Jones", "George Karlaftis III", "Nick Bolton"} <= kept("KC", "Defense")

    k_rows = "\n".join(f"| {r.name} | {r.tg} | {r.share:.0%} | {'Yes' if r.in_game else 'No'} |" for r in k_top.itertuples())
    b_rows = "\n".join(f"| {r.name} | {r.tg} | {r.share:.0%} | {'Yes' if r.in_game else 'No'} |" for r in b_top.itertuples())

    md = f"""# Who's left from the AFC title game: Buffalo kept its offense, and both teams rebuilt their secondary

**{"Twenty-two" if months == 22 else months} months ago, Kansas City beat Buffalo {int(gm.home_score)}-{int(gm.away_score)} in the AFC Championship Game. Of the {nb} Bills who played at least half the
offensive or defensive snaps that night, {sb} are still Bills. Kansas City kept {sk} of {nk}. Buffalo's offense is nearly intact: {int(bo.get('same', 0))} of
{int(bo.sum())} regulars are back, starting with Josh Allen and {ol_back} of the {len(ol)} offensive linemen. The big turnover on both sides is in the secondary: Kansas City has lost
{len(gone_sec['KC'])} of its {int(sec_t.loc['KC'].sum())} regular defensive backs from that game, and Buffalo {len(gone_sec['BUF'])} of {int(sec_t.loc['BUF'].sum())}.**

*Part 2 of our Bills-Chiefs series. [Part 1: the Leonhard file](bills-chiefs-leonhard-file.html).*

![Who's left from the January 2025 AFC title game]({PNG})

## Buffalo: same offense, new coaches, reworked defense

On offense, {int(bo.get('same', 0))} of Buffalo's {int(bo.sum())} regulars from that game are still Bills. Gone: {gone('BUF', 'Offense')}.

On defense it's {int(bd.get('same', 0))} of {int(bd.sum())}. Still here: {', '.join(c[(c.team=='BUF')&(c.side=='Defense')&(c.status=='same')].sort_values('player').player)}.
Gone: {gone('BUF', 'Defense')}.

The sideline changed too. Joe Brady called Buffalo's plays in that game as offensive coordinator. He's now the head coach and still calls them.
Pete Carmichael is the new offensive coordinator, and Jim Leonhard, [hired from Denver in January](https://www.nfl.com/news/bills-hiring-broncos-assistant-head-coach-jim-leonhard-as-defensive-coordinator), runs the defense.

## Kansas City: same quarterback and tight end, a new secondary

On offense, {int(ko.get('same', 0))} of Kansas City's {int(ko.sum())} regulars are still Chiefs, including Patrick Mahomes, Travis Kelce, Xavier Worthy and center Creed Humphrey.
Gone: {gone('KC', 'Offense')}.

On defense, {int(kd.get('same', 0))} of {int(kd.sum())}. Chris Jones, George Karlaftis III and Nick Bolton are still there. Most of the secondary isn't:
{gone_db('KC')}. Also gone from the front: {joinl(f"{r.player} ({where(r)})" for r in c[(c.team == 'KC') & (c.side == 'Defense') & (c.status != 'same') & ~c.position.isin(db_pos) & (c.player != sw.player)].sort_values('player').itertuples())}
and {sw.player}, who crossed over. {sw.player.split()[-1]} played {sw.defense_pct:.0%} of Kansas City's defensive snaps in that game and is now a Bill ({sw.g26} game{'s' if sw.g26 != 1 else ''} this season).

Andy Reid and defensive coordinator Steve Spagnuolo are back. The offensive coordinator is new:
[Eric Bieniemy replaced Matt Nagy](https://www.yardbarker.com/nfl/articles/chiefs_make_double_coaching_decision_on_thursday/s1_17615_43398657) after the 2025 season.

## Who Mahomes throws to now

| Chiefs receiver, 2026 | Targets | Share | Targeted in the Jan. 2025 game? |
|---|---|---|---|
{k_rows}

Players who were targeted in that title game have drawn {k_then_share_now:.0%} of Kansas City's targets this season. For Buffalo it's {b_then_share_now:.0%}:

| Bills receiver, 2026 | Targets | Share | Targeted in the Jan. 2025 game? |
|---|---|---|---|
{b_rows}

## What it means Thursday

Buffalo's offense is the most familiar group on the field: the same quarterback and play-caller, most of the same line and most of the same targets.
Kansas City has replaced most of its secondary from that game, and Buffalo has a new defensive coordinator. The history between these teams is real, but only
about half of the defenders from that game are still on the same side.

## How we counted

We started with Pro Football Reference's snap counts for the AFC Championship Game played {pd.Timestamp(gm.gameday).strftime('%b. %-d, %Y')} and kept every player who was on the field for at least
half his team's offensive or defensive plays. For example, {sw.player} played {int(sw.defense_snaps)} of Kansas City's defensive snaps. Then we looked up each player's
2026 snaps through Week {WK}'s Sunday games (Monday night's Cincinnati-Washington game hadn't been played), and his latest weekly roster status. "Still with the team" means he has played for the same team this season. A team in parentheses is the last team he played for this season.

## For the stat-heads

- Regular in the game: offense_pct >= 0.5 or defense_pct >= 0.5 in {GAME} (BUF {nb}, KC {nk}). Special-teams-only players excluded.
- 2026 status: any offensive or defensive snap in 2026 regular-season games through Week {WK} ({n_games} of {len(sched)} games; {missing[0]} not yet played). Released and practice-squad labels: Week {ROSTER_WK} weekly roster (CUT, DEV).
- No 2026 offensive or defensive snaps: {', '.join(f"{r.player} ({r.team}{', on a 2026 roster' if r.rostered else ', not on a 2026 weekly roster'})" for r in none.itertuples())}.
- Targets: nflverse `receiver_player_id` on pass attempts; sacks, two-point tries and no-plays excluded. KC 2026 {k_tot}, BUF 2026 {b_tot}.
- Defensive backs: positions CB, S, FS, SS.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "From the January 2025 AFC title game",
        "big": [[sb, f"of {nb} Bills regulars still Bills"], [sk, f"of {nk} Chiefs regulars still Chiefs"]],
        "note": f"Buffalo's offense is nearly intact. Both secondaries turned over: Kansas City lost {len(gone_sec['KC'])} of {int(sec_t.loc['KC'].sum())} regular defensive backs, Buffalo {len(gone_sec['BUF'])} of {int(sec_t.loc['BUF'].sum())}.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
