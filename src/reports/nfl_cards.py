"""NFL player cards: one card per player with offensive or defensive snaps this season. -> reports/cards/nfl_players.json

Sources (all regular season):
  raw_snap_counts  games, snaps and the player's position (Pro Football Reference ids)
  raw_player_week  box-score stats (gsis ids)
  raw_pfr_def      Pro Football Reference game charting: pressures, missed tackles, coverage (only fully charted weeks)
  raw_pbp          QB points added per dropback
  raw_players      links PFR ids to gsis ids; jersey numbers
Players are identified by gsis id. A PFR id is linked through raw_players only when that player is active in this era; otherwise
(e.g. a rookie who shares a retired player's PFR id) it is matched to the box-score player with the same team, name and weeks.
Stats are season totals across teams; the card sits with the team he played for most recently. Pinned to WEEK; --latest refreshes.
"""
import json
import re
import sys

import numpy as np
import pandas as pd

from src.db import ROOT, query

OUT = ROOT / "reports" / "cards"
SEASON = 2026
WEEK = 9              # cards pinned through this week; --latest uses the newest complete week
MIN_GP = 4            # games played, to be ranked
MIN_DB = 100          # QB dropbacks, to be ranked
EDGE_PRESS, EDGE_TACKLES = 1.0, 6.0   # per game: a linebacker who rushes the passer like an edge rusher
HIST_FROM = 2018

# PFR snap-count position -> card group
POS_GROUP = {"QB": "QB", "RB": "RB", "HB": "RB", "FB": "FB", "WR": "WR", "TE": "TE", "C": "OL", "G": "OL", "T": "OL", "OL": "OL",
             "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
             "CB": "CB", "S": "S", "FS": "S", "SS": "S", "SAF": "S"}
GROUPS = ["QB", "RB", "FB", "WR", "TE", "OL", "DL", "LB", "CB", "S"]
POS_NAME = {"QB": "Quarterback", "RB": "Running back", "HB": "Running back", "FB": "Fullback", "WR": "Wide receiver",
            "TE": "Tight end", "C": "Center", "G": "Guard", "T": "Offensive tackle", "OT": "Offensive tackle", "OL": "Offensive lineman",
            "DE": "Defensive end", "DT": "Defensive tackle", "NT": "Nose tackle", "DL": "Defensive lineman", "LB": "Linebacker",
            "ILB": "Inside linebacker", "MLB": "Middle linebacker", "OLB": "Outside linebacker", "CB": "Cornerback", "S": "Safety",
            "FS": "Safety", "SS": "Safety", "SAF": "Safety", "DB": "Defensive back"}
# group -> (headline column, headline label); group -> (rank column, rank wording); FB and OL are not ranked
BIG = {"QB": ("pass_yds", "passing yards"), "RB": ("scrim", "yards from scrimmage"), "FB": ("scrim", "yards from scrimmage"),
       "WR": ("rec_yds", "receiving yards"), "TE": ("rec_yds", "receiving yards"), "OL": ("snaps", "snaps"),
       "DL": ("pressures", "pressures"), "LB": ("tackles", "tackles"), "CB": ("pd", "passes defended"), "S": ("tackles", "tackles")}
RANK_ON = {"QB": ("epa_db", "points added per dropback"), "RB": ("scrim", "yards from scrimmage per game"),
           "WR": ("rec_yds", "receiving yards per game"), "TE": ("rec_yds", "receiving yards per game"),
           "DL": ("pressures", "pressures per game"), "LB": ("tackles", "tackles per game"),
           "CB": ("pd", "passes defended per game"), "S": ("tackles", "tackles per game")}


def norm(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()   # Estimé -> Estime
    name = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(name).lower())
    return re.sub(r"[^a-z]", "", name)


def latest_week(season=SEASON):
    """Newest week whose games are all final and whose player stats are loaded."""
    sch = query(f"SELECT week, SUM(home_score IS NULL) open FROM raw_schedules WHERE season={season} AND game_type='REG' GROUP BY week ORDER BY week")
    first_open = sch[sch.open > 0].week.min()
    done = (first_open - 1) if pd.notna(first_open) else sch.week.max()
    have = query(f"SELECT MAX(week) w FROM raw_player_week WHERE season={season} AND season_type='REG'").w.iloc[0]
    return int(min(done, have))


def tackles(df):
    # solo + the tackler credited on a shared tackle + assists: matches ESPN's and PFR's combined tackles
    return df.def_tackles_solo + df.def_tackles_with_assist + df.def_tackle_assists


def main(week=WEEK):
    week = week or latest_week()
    pl = query("SELECT gsis_id, pfr_id, display_name, position, jersey_number, rookie_season, last_season FROM raw_players ORDER BY gsis_id")
    pl = pl.drop_duplicates("gsis_id")
    info = pl.set_index("gsis_id")

    # ---- snaps: every game he played (special teams included); a card needs offensive or defensive snaps this season
    sn = query(f"""SELECT week, team, player, pfr_player_id, position, offense_snaps, offense_pct, defense_snaps, defense_pct, st_snaps
                   FROM raw_snap_counts WHERE season={SEASON} AND game_type='REG' AND week<={week} ORDER BY week, team, pfr_player_id""")
    for c in ("offense_snaps", "defense_snaps", "st_snaps"):
        sn[c] = sn[c].fillna(0)
    sn = sn[sn.offense_snaps + sn.defense_snaps + sn.st_snaps > 0].copy()
    sn["od"] = sn.offense_snaps + sn.defense_snaps
    keep = sn.groupby("pfr_player_id").od.sum()
    sn = sn[sn.pfr_player_id.isin(keep[keep > 0].index)]

    # ---- link PFR id -> gsis id
    pw = query(f"SELECT * FROM raw_player_week WHERE season_type='REG' AND season BETWEEN {HIST_FROM} AND {SEASON} ORDER BY season, week, player_id")
    cur = pw[(pw.season == SEASON) & (pw.week <= week)]
    direct = pl.dropna(subset=["pfr_id"]).drop_duplicates("pfr_id", keep=False)
    direct = direct[direct.last_season.fillna(SEASON) >= SEASON - 1].set_index("pfr_id").gsis_id     # active in this era only
    link = {p: direct[p] for p in sn.pfr_player_id.unique() if p in direct.index}
    # fallback: same team, same normalized name, overlapping weeks in the box scores
    curn = cur.assign(n=cur.player_display_name.map(norm))[["player_id", "team", "week", "n"]]
    fallback = 0
    for pid, g in sn[~sn.pfr_player_id.isin(link)].groupby("pfr_player_id"):
        m = curn[(curn.n == norm(g.player.iloc[0])) & curn.team.isin(g.team) & curn.week.isin(g.week)].player_id.unique()
        if len(m) == 1 and m[0] not in link.values():
            link[pid] = m[0]
            fallback += 1
    unlinked = sorted(set(sn.pfr_player_id) - set(link))
    sn["gsis"] = sn.pfr_player_id.map(link)
    sn = sn.dropna(subset=["gsis"])
    inv = {}
    for p, g in link.items():
        inv.setdefault(g, []).append(p)
    assert all(len(v) == 1 for v in inv.values()), "two PFR ids linked to one player"

    # ---- per-player season basics
    sn["pct"] = np.where(sn.offense_snaps >= sn.defense_snaps, sn.offense_pct, sn.defense_pct)
    sn.loc[sn.od == 0, "pct"] = np.nan                     # special-teams-only games don't count toward snap share
    pos = sn[sn.od > 0].groupby("gsis").position.agg(lambda x: x.mode().iloc[0])
    games = sn.groupby("gsis").agg(snaps=("od", "sum"), pct=("pct", "mean"))
    gweeks = (pd.concat([sn[["gsis", "week"]], cur[cur.player_id.isin(games.index)][["player_id", "week"]].rename(columns={"player_id": "gsis"})])
              .drop_duplicates().groupby("gsis").week.apply(sorted))   # a snap row or a stat line: the snap file misses some games
    games["gp"] = gweeks.map(len)
    last = sn.sort_values(["week", "team"]).groupby("gsis").tail(1).set_index("gsis")
    teams_played = sn.sort_values("week").groupby("gsis").team.agg(lambda x: list(dict.fromkeys(x)))
    tw = query(f"""SELECT home_team AS team, week FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week}
                   UNION SELECT away_team, week FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week}""")
    team_last = tw.groupby("team").week.max()
    week_date = query(f"SELECT MAX(gameday) d FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week={week}").d.iloc[0]

    num = cur.select_dtypes("number").columns.drop(["season", "week"])
    tot = cur.groupby("player_id")[list(num)].sum()

    # ---- QB points added per dropback (scrambles credit the QB as rusher; no two-point tries)
    db = query(f"""SELECT COALESCE(passer_player_id, rusher_player_id) AS qb, week, epa FROM raw_pbp
                   WHERE season={SEASON} AND season_type='REG' AND week<={week} AND qb_dropback=1 AND epa IS NOT NULL
                   AND two_point_attempt=0 ORDER BY game_id, play_id""")
    qb = db.groupby("qb").agg(n_db=("epa", "size"), epa=("epa", "sum"))

    # ---- PFR charting, through the last week with every game charted (and no gaps before it)
    sch_n = query(f"SELECT week, COUNT(*) n FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week ORDER BY week")
    pf_n = query(f"SELECT week, COUNT(DISTINCT game_id) n FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week")
    full = sch_n.merge(pf_n, on="week", how="left", suffixes=("", "_pf")).fillna(0)
    gap = full[full.n_pf < full.n].week.min()
    pfr_week = int(gap - 1) if pd.notna(gap) else week
    games["gp_pfr"] = gweeks.map(lambda w: sum(x <= pfr_week for x in w))
    pf = query(f"""SELECT week, pfr_player_id, def_pressures, def_missed_tackles, def_targets, def_completions_allowed, def_yards_allowed
                   FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={pfr_week} ORDER BY week, pfr_player_id""")
    pf["gsis"] = pf.pfr_player_id.map(link)
    pf = pf.dropna(subset=["gsis"])
    pft = pf.groupby("gsis")[["def_pressures", "def_missed_tackles", "def_targets", "def_completions_allowed", "def_yards_allowed"]].sum()

    rows = []
    for gid, g in games.iterrows():
        p = pos.get(gid)
        if p == "DB" and gid in info.index:
            p = "S" if info.loc[gid, "position"] in ("S", "FS", "SS", "SAF") else "CB"
        grp = POS_GROUP.get(p)
        if grp is None:
            continue                    # specialists: not in the first cut
        t = tot.loc[gid] if gid in tot.index else pd.Series(0, index=tot.columns)
        f = pft.loc[gid] if gid in pft.index else pd.Series(0, index=pft.columns)
        q = qb.loc[gid] if gid in qb.index else None
        jn = info.loc[gid, "jersey_number"] if gid in info.index else None
        name = info.loc[gid, "display_name"] if gid in info.index else last.loc[gid, "player"]
        rows.append(dict(
            id=gid, name=name, team=last.loc[gid, "team"], last_week=int(last.loc[gid, "week"]),
            team_last_week=int(team_last.get(last.loc[gid, "team"], week)), grp=grp, pos=p,
            number=int(jn) if jn is not None and jn == jn else None,
            gp=int(g.gp), gp_pfr=int(g.gp_pfr), snaps=int(g.snaps), snap_pct=float(g.pct) if g.pct == g.pct else None,
            other_teams=[x for x in teams_played.loc[gid] if x != last.loc[gid, "team"]],
            cmp=int(t.completions), att=int(t.attempts), pass_yds=int(t.passing_yards), pass_td=int(t.passing_tds),
            ints=int(t.passing_interceptions), sacked=int(t.sacks_suffered),
            car=int(t.carries), rush_yds=int(t.rushing_yards), rush_td=int(t.rushing_tds),
            tgt=int(t.targets), rec=int(t.receptions), rec_yds=int(t.receiving_yards), rec_td=int(t.receiving_tds),
            fum_lost=int(t.rushing_fumbles_lost + t.receiving_fumbles_lost + t.sack_fumbles_lost),
            tackles=int(tackles(t)), tfl=int(t.def_tackles_for_loss), sacks=float(t.def_sacks),
            def_int=int(t.def_interceptions), pd=int(t.def_pass_defended), ff=int(t.def_fumbles_forced), def_td=int(t.def_tds),
            pressures=int(f.def_pressures), missed_tk=int(f.def_missed_tackles), cov_tgt=int(f.def_targets),
            cov_cmp=int(f.def_completions_allowed), cov_yds=int(f.def_yards_allowed), penalties=int(t.penalties),
            n_db=int(q.n_db) if q is not None else 0, epa_db=float(q.epa / q.n_db) if q is not None and q.n_db else None))
    c = pd.DataFrame(rows)
    c["scrim"] = c.rush_yds + c.rec_yds
    # edge rushers are listed as linebackers: card them with the pass rushers when they play like one
    per_press = c.pressures / c.gp_pfr.clip(lower=1)
    c["edge"] = (c.grp == "LB") & (per_press >= EDGE_PRESS) & (c.tackles / c.gp < EDGE_TACKLES)
    c.loc[c.edge, "grp"] = "DL"

    def per_game(df, col):
        return df[col] / (df.gp_pfr.clip(lower=1) if col == "pressures" else df.gp)

    c["rk"], c["of"] = None, None
    lg = {"QB_all": float(db.epa.sum() / len(db))}
    for grp, (col, _) in RANK_ON.items():
        m = (c.grp == grp) & ((c.n_db >= MIN_DB) if grp == "QB" else (c.gp >= MIN_GP))
        val = c.loc[m, col] if grp == "QB" else per_game(c[m], col)
        c.loc[m, "rk"] = val.rank(ascending=False, method="min").astype(int)
        c.loc[m, "of"] = int(m.sum())
        lg[grp] = float(val.mean()) if grp != "QB" else lg["QB_all"]

    # ---- week-by-week running totals for the sparkline
    wk = cur.assign(scrim=cur.rushing_yards + cur.receiving_yards, tackles=tackles(cur)).rename(
        columns={"passing_yards": "pass_yds", "receiving_yards": "rec_yds", "def_pass_defended": "pd"})
    by_week = {col: wk.groupby(["player_id", "week"])[col].sum() for col in ("pass_yds", "scrim", "rec_yds", "tackles", "pd")}
    by_week["pressures"] = pf.groupby(["gsis", "week"]).def_pressures.sum()
    by_week["snaps"] = sn.groupby(["gsis", "week"]).od.sum()

    # ---- history: every season (from 2018) with a snap or a stat line; this season included
    hs = query(f"""SELECT season, week, team, pfr_player_id FROM raw_snap_counts WHERE game_type='REG' AND season BETWEEN {HIST_FROM} AND {SEASON - 1}
                   AND COALESCE(offense_snaps, 0) + COALESCE(defense_snaps, 0) + COALESCE(st_snaps, 0) > 0""")
    hs["player_id"] = hs.pfr_player_id.map(lambda p: link.get(p, direct.get(p)))
    hw = pd.concat([hs.dropna(subset=["player_id"])[["player_id", "season", "week", "team"]],
                    pw[pw.season < SEASON][["player_id", "season", "week", "team"]],
                    cur[["player_id", "season", "week", "team"]],
                    sn[["gsis", "week", "team"]].rename(columns={"gsis": "player_id"}).assign(season=SEASON)])
    hw = hw[hw.player_id.isin(c.id)].drop_duplicates(["player_id", "season", "week"]).sort_values(["player_id", "season", "week"])
    hg = hw.groupby(["player_id", "season"]).agg(gp=("week", "nunique"), team=("team", lambda x: "/".join(dict.fromkeys(x))))
    hp = pd.concat([pw[pw.season < SEASON], cur])
    hp = hp[hp.player_id.isin(c.id)].assign(tk=tackles(hp[hp.player_id.isin(c.id)])).groupby(["player_id", "season"]).agg(
        pass_yds=("passing_yards", "sum"), pass_td=("passing_tds", "sum"), ints=("passing_interceptions", "sum"),
        rush_yds=("rushing_yards", "sum"), rush_td=("rushing_tds", "sum"), rec=("receptions", "sum"), rec_yds=("receiving_yards", "sum"),
        rec_td=("receiving_tds", "sum"), tackles=("tk", "sum"), sacks=("def_sacks", "sum"), def_int=("def_interceptions", "sum"),
        pd=("def_pass_defended", "sum"))
    hist = hg.join(hp).fillna(0).reset_index()
    hist_by = {pid: g for pid, g in hist.groupby("player_id")}

    cards = []
    for r in c.to_dict("records"):
        col, label = BIG[r["grp"]]
        weeks = gweeks.loc[r["id"]]
        s = by_week[col]
        r["spark"] = np.cumsum([int(s.get((r["id"], w), 0)) for w in weeks]).tolist()
        r["big"], r["big_label"] = r[col], label
        r["rank_what"] = RANK_ON[r["grp"]][1] if r["grp"] in RANK_ON else None
        h = hist_by.get(r["id"], pd.DataFrame())
        r["seasons"] = [dict(season=int(x.season), team=x.team, gp=int(x.gp), pass_yds=int(x.pass_yds), pass_td=int(x.pass_td),
                             ints=int(x.ints), rush_yds=int(x.rush_yds), rush_td=int(x.rush_td), rec=int(x.rec),
                             rec_yds=int(x.rec_yds), rec_td=int(x.rec_td), tackles=int(x.tackles), sacks=float(x.sacks),
                             def_int=int(x.def_int), pd=int(x.pd)) for x in h.itertuples()]
        r["small"] = bool(r["n_db"] < MIN_DB if r["grp"] == "QB" else r["gp"] < MIN_GP)
        r["number"] = None if r["number"] is None or r["number"] != r["number"] else int(r["number"])
        for k, v in list(r.items()):
            if isinstance(v, (bool, np.bool_)):
                r[k] = bool(v)
            elif isinstance(v, (int, np.integer)):
                r[k] = int(v)
            elif isinstance(v, (float, np.floating)):
                r[k] = None if np.isnan(v) else float(v)
        cards.append(r)

    meta = dict(season=SEASON, week=week, week_date=str(week_date), pfr_week=pfr_week, min_gp=MIN_GP, min_db=MIN_DB,
                edge_press=EDGE_PRESS, edge_tackles=EDGE_TACKLES, hist_from=HIST_FROM, lg=lg, n=len(cards),
                linked_by_name=fallback, unlinked=unlinked)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "nfl_players.json").write_text(json.dumps(dict(meta=meta, cards=cards), indent=1, allow_nan=False))
    print(f"NFL cards through week {week} (charting through {pfr_week}): {len(cards)} players; "
          f"{fallback} linked by team/name/weeks; unlinked {unlinked}")
    print(c.groupby("grp").size().to_dict())
    return meta, cards


if __name__ == "__main__":
    main(None if "--latest" in sys.argv else WEEK)
