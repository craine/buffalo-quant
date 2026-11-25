"""Is Josh Allen too reckless to win it all? (Nov. 25, 2026)

Every Super Bowl-winning quarterback, 1966-2025 (60), ranked against that season's starters on three things: how often he threw
interceptions, how far his completions went (a rough sign of throwing downfield), and passing value (yards per throw with touchdowns
counted as +20 and interceptions as -45, Pro Football Reference's adjusted yards per attempt). Then Brett Favre, Josh Allen, and
Allen's Week 11 game against Miami.

Writes reports/2026-11-25-allen-yolo.md, one PNG (allen-yolo-nov25-champions.png) and a hero JSON.

Sources and pins:
- 1966-1998 season passing: Pro Football Reference season tables, saved in reports/sources/pfr_passing_1966_2002.csv
  (fetched 2026-11-25 through Chrome; row counts and attempt, yard and interception totals per decade checked against the page).
  1968-69 AFL tables included for the Jets and Chiefs. Also 1999-2002, because nflverse's weekly stats are missing 19 team-games in those
  seasons (the 1999 Rams opener, two 2000 games, and one side of 16 Jaguars home games in 2001-02); those rows also cross-check nflverse.
- Super Bowl quarterbacks: the winning team's passer with the most attempts in each Super Bowl box score (reports/sources/pfr_super_bowl_qbs.csv).
- 2003-2026 season passing: nflverse weekly player stats (regular season), summed; every scheduled game is covered. 2026 through Week 11.
- Deep-throw check and the Miami game: nflverse play-by-play in data/buffalo.db (2018-2025; 2026 weeks 1-11, fingerprint asserted).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk11_postgame import finish, ordn

OUT = ROOT / "reports"
SRC = OUT / "sources"
CACHE = ROOT / "data" / "cache"
SLUG = "2026-11-25-allen-yolo"
PNG = "allen-yolo-nov25-champions.png"
WK26 = 11
ALLEN_PFR, FAVRE_PFR = "AlleJo02", "FavrBr00"
MIA_GAME = "2026_11_MIA_BUF"
NFLV = "https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{y}.parquet"
# nflverse regular-season pass attempts and passing yards, 1999-2025, and 2026 weeks 1-11 (pinned on Nov. 25, 2026)
NFLV_FINGERPRINT = (479872, 3367804)
PBP26_FINGERPRINT = (28141, -186.8888)


def nflverse_seasons():
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for y in range(1999, 2027):
        f = CACHE / f"stats_player_week_{y}.parquet"
        if not f.exists():
            pd.read_parquet(NFLV.format(y=y)).to_parquet(f)
        w = pd.read_parquet(f)
        w = w[(w.season_type == "REG") & (w.attempts.fillna(0) > 0)]
        if y == 2026:
            w = w[w.week <= WK26]
        out.append(w)
    w = pd.concat(out, ignore_index=True)
    w["team"] = w.team.astype(object).fillna("UNK")
    s = w.groupby(["season", "player_id"]).agg(name=("player_display_name", "last"), games=("week", "nunique"), att=("attempts", "sum"),
                                                cmp=("completions", "sum"), yds=("passing_yards", "sum"), td=("passing_tds", "sum"),
                                                int=("passing_interceptions", "sum")).reset_index()
    tm = w.groupby(["season", "player_id", "team"]).attempts.sum().reset_index().sort_values("attempts").groupby(["season", "player_id"]).team.last()
    s = s.merge(tm.reset_index(), on=["season", "player_id"])
    tg = w.groupby(["season", "team"]).game_id.nunique().groupby("season").max().rename("G")   # most games any team has played
    s = s.merge(tg.reset_index(), on="season")
    fp = (int(w.attempts.sum()), int(w.passing_yards.sum()))
    return s, fp


def main():
    # ---- sources
    p = pd.read_csv(SRC / "pfr_passing_1966_2002.csv", dtype={"season": str})
    p["league"] = np.where(p.season.str.endswith("AFL"), "AFL", "NFL")
    p["yr"] = p.season.str[:4].astype(int)
    dec = p.assign(d=p.yr // 10 * 10)[p.league == "NFL"].groupby("d").agg(n=("att", "size"), att=("att", "sum"), yds=("yds", "sum"), i=("int", "sum"))
    assert dec.loc[1960].tolist() == [86, 21927, 153746, 1124] and dec.loc[1970].tolist() == [359, 91249, 614825, 4563]
    assert dec.loc[1980].tolist() == [397, 122917, 873774, 4946] and dec.loc[1990].tolist() == [446, 142341, 972027, 4635]
    assert p[p.yr.between(2000, 2002)].agg({"att": ["size", "sum"], "yds": "sum", "int": "sum"}).stack().dropna().astype(int).tolist() == [126, 46783, 317816, 1472]
    tm = p[p.team.str.match(r"\dTM")][["yr", "league", "pfr_id"]].assign(multi=1)            # traded players: keep the combined row
    p = p.merge(tm, on=["yr", "league", "pfr_id"], how="left")
    p = p[p.multi.isna() | p.team.str.match(r"\dTM")]
    p["G"] = p.groupby(["yr", "league"]).games.transform("max")

    n, fp = nflverse_seasons()
    if NFLV_FINGERPRINT is not None:
        assert fp == NFLV_FINGERPRINT, f"nflverse player stats changed: {fp}"
    links = query("SELECT gsis_id, pfr_id FROM raw_players WHERE gsis_id IS NOT NULL")
    n = n.merge(links, left_on="player_id", right_on="gsis_id", how="left")
    n["pfr_id"] = n.pfr_id.fillna(n.player_id)
    n["league"], n["yr"] = "NFL", n.season

    # nflverse coverage: every scheduled regular-season game should have passing rows for both teams
    sc = query(f"SELECT season, game_id FROM raw_schedules WHERE game_type = 'REG' AND home_score IS NOT NULL AND season BETWEEN 1999 AND 2026")
    sc = sc[(sc.season < 2026) | (sc.game_id.str.split("_").str[1].astype(int) <= WK26)]
    cov = pd.concat([pd.read_parquet(CACHE / f"stats_player_week_{y}.parquet", columns=["game_id", "team", "attempts", "season_type"]) for y in range(1999, 2027)])
    cov = cov[(cov.season_type == "REG") & (cov.attempts.fillna(0) > 0)].groupby("game_id").team.nunique()
    gaps = sc[sc.game_id.map(cov).fillna(0) < 2]
    assert len(gaps) == 19 and gaps.season.max() == 2002, gaps
    # second source: 1999-2002 in both; rows where nflverse has every game must match exactly
    x = p[p.yr.between(1999, 2002) & ~p.team.str.match(r"\dTM")].merge(n[n.yr.between(1999, 2002)], on=["yr", "pfr_id"], suffixes=("_p", "_n"))
    full = x[x.games_p == x.games_n]
    same = int(((full.yds_p == full.yds_n) & (full.td_p == full.td_n) & (full.int_p == full.int_n)).sum())
    x_n, x_full = len(x), len(full)
    off = full[~((full.yds_p == full.yds_n) & (full.td_p == full.td_n) & (full.int_p == full.int_n))]
    assert (x_n, x_full, same) == (172, 136, 135) and off.pfr_id.tolist() == ["FiedJa00"] and int((off.yds_p - off.yds_n).iloc[0]) == 42

    cols = ["yr", "league", "pfr_id", "team", "att", "cmp", "yds", "td", "int", "G"]
    d = pd.concat([p[p.yr <= 2002][cols], n[n.yr >= 2003][cols]], ignore_index=True)
    d["qual"] = d.att >= 14 * d.G
    d["int_rt"], d["ypc"] = d["int"] / d.att, d.yds / d.cmp
    d["aya"] = (d.yds + 20 * d.td - 45 * d["int"]) / d.att
    Q = d[d.qual].copy()
    for c in ("int_rt", "ypc", "aya"):
        Q[c + "_p"] = Q.groupby(["yr", "league"])[c].rank(pct=True)

    # ---- champions: percentile against that season's qualified starters (non-qualifiers ranked against the same pool)
    sb = pd.read_csv(SRC / "pfr_super_bowl_qbs.csv")
    sb["yr"] = pd.to_datetime(sb.game_date, format="%b %d, %Y").dt.year - 1
    sb["league"] = np.where(sb.yr.isin([1968, 1969]), "AFL", "NFL")
    assert len(sb) == 60 and sb.yr.min() == 1966 and sb.yr.max() == 2025

    def pct(me, col, pool):
        v = pool[col].values
        if me["qual"]:
            return ((v < me[col]).sum() + 0.5 * ((v == me[col]).sum() - 1)) / (len(v) - 1)
        return ((v < me[col]).sum() + 0.5 * (v == me[col]).sum()) / len(v)

    rows = []
    for s in sb.itertuples():
        pool = d[(d.yr == s.yr) & (d.league == s.league) & d.qual]
        me = d[(d.yr == s.yr) & (d.league == s.league) & (d.pfr_id == s.qb_id)]
        assert len(me) == 1, (s.yr, s.qb)
        me = me.iloc[0]
        rows.append(dict(yr=s.yr, qb=s.qb, qual=bool(me.qual), att=int(me.att), ints=int(me["int"]), int_rt=me.int_rt, n_pool=len(pool),
                         int_p=pct(me, "int_rt", pool), ypc_p=pct(me, "ypc", pool), aya_p=pct(me, "aya", pool)))
    C = pd.DataFrame(rows)
    bins = [0, 0.25, 0.5, 0.75, 1.0]
    qc = {c: pd.cut(C[c], bins, include_lowest=True).value_counts().sort_index().tolist() for c in ("int_p", "ypc_p", "aya_p")}
    assert qc == {"int_p": [25, 16, 9, 10], "ypc_p": [7, 13, 11, 29], "aya_p": [3, 6, 12, 39]}, qc
    n_qual = int(C.qual.sum())
    Cq = C[C.qual]
    qc_q = {c: pd.cut(Cq[c], bins, include_lowest=True).value_counts().sort_index().tolist() for c in ("int_p", "ypc_p", "aya_p")}
    early, late = C[C.yr <= 1995], C[C.yr >= 1996]
    halves = {k: (int((g.int_p <= 0.25).sum()), int((g.int_p > 0.75).sum()), int((g.ypc_p > 0.75).sum()), len(g)) for k, g in (("early", early), ("late", late))}
    gun = C[C.int_p > 0.75].sort_values("yr")
    both = C[(C.int_p <= 0.5) & (C.ypc_p > 0.5)]
    timid = C[(C.int_p <= 0.5) & (C.ypc_p <= 0.5)]

    # ---- Favre and Allen
    F = Q[Q.pfr_id == FAVRE_PFR].sort_values("yr")
    f96 = F[F.yr == 1996].iloc[0]
    f_high = F[F.int_rt_p >= 0.9].yr.tolist()
    A = Q[(Q.pfr_id == ALLEN_PFR)].sort_values("yr")
    a26 = A[A.yr == 2026].iloc[0]
    a24 = A[A.yr == 2024].iloc[0]
    assert f96.int_rt_p < 0.1 and f_high == [1993, 2003, 2005, 2008, 2010], f_high
    assert a24.int_rt_p < 0.15 and a24.ypc_p > 0.85 and a24.aya_p > 0.9
    a_ypc_above = int((A[A.yr <= 2025].ypc_p > 0.5).sum())

    # ---- deep-throw check: yards per completion vs. share of throws 20+ yards downfield, 2018-2025
    pb = query("""SELECT p.season, COALESCE(p.passer_player_id, p.rusher_player_id) qb, COUNT(*) n,
                  SUM(CASE WHEN p.air_yards >= 20 THEN 1 ELSE 0 END) deep
                  FROM raw_pbp p WHERE p.season BETWEEN 2018 AND 2025 AND p.season_type = 'REG' AND p.pass_attempt = 1 AND p.sack = 0
                  AND p.air_yards IS NOT NULL AND COALESCE(p.two_point_attempt, 0) = 0 GROUP BY 1, 2""")
    pb["deep_rt"] = pb.deep / pb.n
    nq = n[(n.yr.between(2018, 2025))].merge(pb, left_on=["yr", "player_id"], right_on=["season", "qb"])
    nq = nq[nq.att >= 14 * nq.G].copy()
    nq["ypc"] = nq.yds / nq.cmp
    nq["ypc_p"], nq["deep_p"] = nq.groupby("yr").ypc.rank(pct=True), nq.groupby("yr").deep_rt.rank(pct=True)
    r_proxy = float(nq.ypc_p.corr(nq.deep_p))
    a_deep = nq[nq.pfr_id == ALLEN_PFR].set_index("yr").deep_p

    # ---- the Miami game
    fp26 = query(f"SELECT COUNT(*) n, ROUND(SUM(epa), 4) s FROM raw_pbp WHERE season = 2026 AND season_type = 'REG' AND week <= {WK26} AND epa IS NOT NULL").iloc[0]
    if PBP26_FINGERPRINT is not None:
        assert (int(fp26.n), float(fp26.s)) == PBP26_FINGERPRINT, f"2026 play-by-play changed: {tuple(fp26)}"
    allen = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{ALLEN_PFR}'").gsis_id.iloc[0]
    g = query(f"""SELECT p.game_id, p.season, COUNT(*) db, AVG(p.epa) e, SUM(p.interception) ints, SUM(p.sack) sk
                  FROM raw_pbp p WHERE p.season_type = 'REG' AND p.pass = 1 AND p.epa IS NOT NULL AND p.play_type <> 'no_play'
                  AND COALESCE(p.two_point_attempt, 0) = 0 AND COALESCE(p.qb_spike, 0) = 0 AND (p.season < 2026 OR p.week <= {WK26})
                  AND COALESCE(p.passer_player_id, p.rusher_player_id) = '{allen}' GROUP BY 1, 2 HAVING COUNT(*) >= 15""")
    mia = g[g.game_id == MIA_GAME].iloc[0]
    mia_pct = float((g.e < mia.e).mean())
    s26 = g[g.season == 2026].sort_values("e")
    mia_rank26 = int((s26.e < mia.e).sum()) + 1
    lg = query(f"""SELECT COALESCE(passer_player_id, rusher_player_id) qb, game_id, COUNT(*) n, AVG(epa) e FROM raw_pbp
                   WHERE season = 2026 AND week <= {WK26} AND season_type = 'REG' AND pass = 1 AND epa IS NOT NULL AND play_type <> 'no_play'
                   AND COALESCE(two_point_attempt, 0) = 0 AND COALESCE(qb_spike, 0) = 0 GROUP BY 1, 2 HAVING COUNT(*) >= 15""")
    worse = float((lg.e < mia.e).mean())
    runs = int(query(f"SELECT COUNT(*) n FROM raw_pbp WHERE game_id = '{MIA_GAME}' AND rush = 1 AND rusher_player_id = '{allen}'").n.iloc[0])
    assert (int(mia.ints), int(mia.sk), runs, len(g)) == (2, 3, 0, 135) and 0.2 < mia_pct < 0.25 and mia_rank26 == 2

    # ranks for Allen's 2024 and 2026 interception rates (1 = most interceptions per throw)
    def int_rank(yr):
        pool = Q[(Q.yr == yr)].sort_values("int_rt", ascending=False).reset_index(drop=True)
        return int(pool.index[pool.pfr_id == ALLEN_PFR][0]) + 1, len(pool)
    r24, n24 = int_rank(2024)
    r26, n26 = int_rank(2026)
    f_val = (f96.yds + 20 * f96.td - 45 * f96["int"]) / f96.att
    f_ypc = f96.yds / f96.cmp
    assert (round(f_val, 1), round(f_ypc, 1), int(f96.att), int(f96["int"]), int(f96.td)) == (7.5, 12.0, 543, 13, 39)
    hi_int = int((C.int_p > 0.75).sum())
    lo_int = int((C.int_p <= 0.25).sum())
    hi_ypc, lo_ypc = int((C.ypc_p > 0.75).sum()), int((C.ypc_p <= 0.25).sum())
    hi_val = int((C.aya_p > 0.75).sum())
    assert (lo_int, hi_int, hi_ypc, lo_ypc, hi_val, len(both), len(timid)) == (25, 10, 29, 7, 39, 27, 14)

    # ---- chart: left, every champion by interceptions (x) and completion distance (y), Allen's seasons on top; right, the three counts
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 6.2), dpi=200, gridspec_kw={"width_ratios": [1.35, 1]})
    ax.axvspan(0, 50, ymin=0.5, ymax=1, color="#EEF2F9", zorder=0)
    ax.axvline(50, color="#D5D8DE", lw=1); ax.axhline(50, color="#D5D8DE", lw=1)
    ax.scatter(C.int_p * 100, C.ypc_p * 100, s=34, color=GRAY, edgecolor="white", linewidth=0.8, zorder=2, label="Super Bowl-winning QB, that season")
    ax.text(2, 53, f"Few picks, long completions:\n{len(both)} of {len(C)} champions", fontsize=9.5, color=BLUE, va="bottom", fontweight="bold")
    AA = A[A.yr >= 2018]
    ax.scatter(AA.int_rt_p * 100, AA.ypc_p * 100, s=60, color=BLUE, edgecolor="white", linewidth=1, zorder=4, label="Josh Allen, 2018-2026")
    for r in AA.itertuples():
        lab = f"'{str(r.yr)[2:]}" + ("*" if r.yr == 2026 else "")
        ax.annotate(lab, (r.int_rt_p * 100, r.ypc_p * 100), xytext=(5, 4), textcoords="offset points", fontsize=8.5, color=BLUE, fontweight="bold")
    ax.scatter([f96.int_rt_p * 100], [f96.ypc_p * 100], s=60, color=RED, edgecolor="white", linewidth=1, zorder=4, label="Brett Favre, 1996 (won it all)")
    ax.set_xlim(-3, 103); ax.set_ylim(-3, 103)
    ax.set_xlabel("Interceptions per throw, rank among that season's starters\n(left = fewest, right = most)")
    ax.set_ylabel("Yards per completion, rank among starters\n(top = longest)")
    ax.set_xticks([0, 50, 100], ["fewest", "middle", "most"]); ax.set_yticks([0, 50, 100], ["shortest", "middle", "longest"])
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    ax.set_title("Where every champion ranked the year he won", fontsize=11, color=INK, loc="left")
    labels = ["Fewest\npicks", "", "", "Most\npicks"]
    groups = [("Interceptions per throw", qc["int_p"], ["Fewest", "2nd", "3rd", "Most"]),
              ("Yards per completion", qc["ypc_p"], ["Shortest", "2nd", "3rd", "Longest"]),
              ("Passing value", qc["aya_p"], ["Lowest", "2nd", "3rd", "Highest"])]
    y0 = 0
    for ttl, cnt, qn in groups:
        ys = [y0 - i for i in range(4)]
        bx.barh(ys, cnt, 0.72, color=[BLUE if (ttl.startswith("Inter") and i == 0) or (not ttl.startswith("Inter") and i == 3) else GRAY for i in range(4)], zorder=2)
        for yy, c, q in zip(ys, cnt, qn):
            bx.text(-0.6, yy, q + " quarter", ha="right", va="center", fontsize=8.5, color=MUTED)
            bx.text(c + 0.5, yy, str(c), va="center", fontsize=9.5, color=INK, fontweight="bold")
        bx.text(-0.6, y0 + 0.75, ttl, ha="right", va="center", fontsize=10, color=INK, fontweight="bold")
        y0 -= 5.6
    bx.set_xlim(0, 44); bx.set_yticks([]); bx.spines["left"].set_visible(False)
    bx.set_xlabel(f"Number of the {len(C)} champions")
    bx.set_title("Champions by quarter of that season's starters", fontsize=11, color=INK, loc="left")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.82, wspace=0.42)
    finish(fig, "Champions throw the ball downfield. They don't throw it to the other team",
           f"All {len(C)} Super Bowl-winning quarterbacks, 1966-2025, ranked against that season's starters. *2026 through Week {WK26}.", "x")
    fig.texts[-1].set_text("Source: Pro Football Reference season stats (1966-2002) and nflverse (2003-2026). Starters: 14+ throws per team game. "
                           "Passing value: yards per throw, touchdowns +20, interceptions -45.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    # ---- story
    gl = ", ".join(f"{r.qb} ({r.yr})" for r in gun.itertuples())
    arow = "\n".join(f"| {r['yr']}{' (through Week ' + str(WK26) + ')' if r['yr'] == 2026 else ''} | {r['att']} | {r['int']} | {ordn(round(r['int_rt_p'] * 100))} | "
                      f"{ordn(round(r['ypc_p'] * 100))} | {ordn(round(r['aya_p'] * 100))} |" for r in A[A.yr >= 2018].to_dict("records"))
    md = f"""# Is Josh Allen too reckless to win it all? 60 Super Bowl champions say: throw it deep, but don't throw it away

**Allen had a rough day against Miami, and the question came back: is he too much of a gunslinger to win a Super Bowl? We ranked all {len(C)}
Super Bowl-winning quarterbacks against the other starters the year they won. Champions weren't timid: {hi_ypc} of {len(C)} ranked in the top quarter
for how far their completions went. But they rarely threw it to the other team: {lo_int} were in the quarter with the fewest interceptions,
and only {hi_int} were in the quarter with the most. Allen throws downfield like a champion. In 2024 he also protected the ball like one.
This season, his interception rate ranks {ordn(r26)} highest of {n26} starters.**

![Champions throw the ball downfield. They don't throw it to the other team]({PNG})

## The Miami game

Measured by how much each of his pass plays helped or hurt Buffalo's chances to score, it was one of Allen's weaker days: only {mia_pct:.0%} of his
{len(g)} career starts were worse, and it was his {ordn(mia_rank26)}-worst game this season. He threw {int(mia.ints)} interceptions, took {int(mia.sk)} sacks
and didn't run once. But by the same measure, {worse:.0%} of all NFL starts this season have been worse. For most quarterbacks it would have been a normal day.
For Allen it was a dud. That's part of the "reckless" story: the bar is high.

## How we measured it

For every season since 1966, we took every starter (at least 14 throws per team game) and ranked them on three things:

- **Interceptions per throw.** Brett Favre in 1996: {int(f96["int"])} interceptions on {int(f96.att)} throws.
- **Yards per completion,** how far his completed passes went. Favre in 1996: {f_ypc:.1f} yards. It's a rough sign of throwing downfield. We checked it against
  the actual distance of every throw since 2018: quarterbacks who rank high on one tend to rank high on the other, but it's a loose match.
- **Passing value:** yards per throw, with each touchdown worth 20 extra yards and each interception costing 45. Favre in 1996: {f_val:.1f}.

Then we found where each Super Bowl winner ranked the year he won: top quarter, bottom quarter, or in between.

## What the champions had in common

- **They were efficient.** {hi_val} of {len(C)} ranked in the top quarter for passing value.
- **They threw it downfield.** {hi_ypc} ranked in the top quarter for yards per completion. Only {lo_ypc} were in the bottom quarter.
- **They didn't throw many interceptions.** {lo_int} were in the quarter with the fewest. Only {hi_int} were in the quarter with the most.

The most common champion was both: {len(both)} of {len(C)} were better than the middle on interceptions and on completion distance. Only {len(timid)} were
careful but short.

**How we checked it.** {len(C) - n_qual} champions didn't throw enough that season to count as starters, such as Jeff Hostetler, a backup for most of 1990.
We ranked them against the starters anyway. Without them, the pattern is the same: {qc_q['int_p'][0]} of {n_qual} in the fewest-interceptions quarter, {qc_q['int_p'][3]} in the most.
It holds in both halves of Super Bowl history too: {halves['early'][0]} of the first {halves['early'][3]} champions (1966-1995) were in the
fewest-interceptions quarter and {halves['early'][1]} in the most; for the last {halves['late'][3]} (1996-2025), {halves['late'][0]} and {halves['late'][1]}.

## The gunslingers who won anyway

It does happen. {hi_int} champions won in a year when their interception rate was in the league's top quarter: {gl}.
Last season's champion, Sam Darnold, is one of them.

## Brett Favre

Favre is the classic gunslinger, but his title season wasn't. In 1996 his interception rate was lower than {round((1 - f96.int_rt_p) * 100)}% of starters', and his
passing value ranked near the top of the league. In five other seasons ({", ".join(str(y) for y in f_high)}) his interception rate was among the highest 10% of
starters. None of those seasons ended in a title.

## Josh Allen

| Season | Throws | Interceptions | Interception rate, rank* | Yards per completion, rank* | Passing value, rank* |
|---|---|---|---|---|---|
{arow}

*Percentile among that season's starters: 99th is highest. For interceptions, higher means more.

Allen's completions have gone farther than the typical starter's in {a_ypc_above} of his {len(A[A.yr <= 2025])} full seasons. That's the champion half.
His interceptions are the part that moves. In 2024 he threw {int(a24['int'])} on {int(a24.att)} throws, the {ordn(n24 - r24 + 1)} lowest rate of {n24} starters, and his passing value
ranked near the top. That season looked like a champion's. This season he has {int(a26['int'])} interceptions in {int(a26.att)} throws, {ordn(r26)} highest of {n26}.

## What it means

The data doesn't say Allen is too reckless to win. Champions throw downfield; Allen does that every year. What separates most champions is the
second half: they kept the ball away from the defense. Allen has done it before, in 2024. This season he hasn't so far.

## Caveats

- Quarterbacks don't win alone. Defenses, running games and luck matter, and this only looks at the passer.
- Interceptions are a rough stand-in for risky throws. They include tipped balls and miss risky throws that weren't caught.
- In the 1960s there were only 9 to 15 starters per league, so a single rank moves a lot.

## For the stat-heads

- Champion QB: the winning team's passer with the most attempts in the Super Bowl box score (Earl Morrall in Super Bowl V, not Johnny Unitas).
  1968-69 champions ranked within the AFL. Ranks are percentiles within season and league among qualifiers (att >= 14 x the most games any team played);
  non-qualifiers ({len(C) - n_qual}) are placed within the qualified pool.
- Passing value = PFR adjusted yards per attempt, (yds + 20 TD - 45 INT) / att. It includes interceptions, so it's not independent of the interception rank.
- Sources: PFR season passing tables 1966-2002 (saved, decade totals asserted); nflverse weekly player stats 2003-2026, summed, regular season.
  nflverse is missing 19 team-games in 1999-2002, so PFR is used through 2002. In 1999-2002 the two sources agree exactly on yards, TDs and INTs for
  {x_full - 1} of {x_full} QB-seasons with the same games played (Jay Fiedler 2001 differs by 42 yards).
- Yards per completion vs. share of throws 20+ air yards, 2018-2025 qualifiers, within-season percentile correlation: {r_proxy:.2f}.
- Allen's deep-throw percentile (20+ air yards), 2018-2025: {", ".join(f"{k}: {v:.0%}" for k, v in a_deep.items())}.
- Miami game: Allen EPA per dropback {mia.e:+.3f} on {int(mia.db)} dropbacks (scrambles included); his career starts with 15+ dropbacks: {len(g)}.
- Data pins: nflverse weekly stats 1999-2026 (week <= {WK26}) attempts and yards {fp}; 2026 play-by-play fingerprint {PBP26_FINGERPRINT}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "60 Super Bowl QBs",
        "big": [[lo_int, f"of {len(C)} champions were in the quarter of starters with the fewest interceptions"],
                [hi_int, f"of {len(C)} were in the quarter with the most"]],
        "note": f"Champions also threw downfield: {hi_ypc} of {len(C)} ranked in the top quarter for yards per completion. Allen's 2026 interception rate ranks {ordn(r26)} highest of {n26} starters.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
