"""Bills trade for safety Amani Hooker (Nov 10, 2026 deadline). What the data says he brings, in plain English.

Writes reports/2026-11-10-hooker-trade.md, two PNGs and a hero JSON. Angle (Charlie): Bishop's partner problem. Every number is computed here, except the trade terms,
which are reported facts cited to the Bills' announcement. Pinned: games through 2026 week THRU.
Coverage numbers (targets, yards allowed, missed tackles) are Pro Football Reference charting via nflverse: human-charted, noisy.
Safeties are identified by matching PFR names to nflverse weekly player stats (see match_safeties).
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 9
PFR_THRU = 8                   # PFR charting complete through week 8 as of AS_OF; pinned so re-runs reproduce
AS_OF = "2026-11-10"
HOOKER = "00-0035632"          # gsis id
HOOKER_PFR = "HookAm00"        # PFR id (matched by name+team+season, verified unique)
SAFETY = ("SAF", "FS", "SS", "S")
MIN_TGT, MIN_TGT_SEASON, MIN_TGT_3YR = 25, 15, 60
SLUG = "2026-11-10-hooker-trade"
SRC = "Source: nflverse player stats; Pro Football Reference coverage charting via nflverse. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def finish(fig, title, sub, foot, src=SRC):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{src}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


SUFFIX = {"jr", "sr", "ii", "iii", "iv", "v"}
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA"}


def _tokens(n):
    return [w for w in re.sub(r"[.'’]", "", str(n)).lower().split() if w not in SUFFIX]


def full_key(n):
    return " ".join(_tokens(n))


def short_key(n):
    t = _tokens(n)
    return f"{t[0][0]}|{t[-1]}" if t else ""


def match_safeties(pw, pf):
    """PFR rows -> nflverse safeties. Tier 1: same season, team and name (suffixes and punctuation removed).
    Tier 2, only for PFR players still unmatched: first initial + last name, used only where that key is unique
    on the team-season in both sources (catches Kam/Kamren Curl, C.J./Chauncey Gardner-Johnson)."""
    pw = pw.assign(fk=pw.name.map(full_key), sk=pw.name.map(short_key))
    pf = pf.assign(team=pf.team.replace(TEAM_FIX), fk=pf.name.map(full_key), sk=pf.name.map(short_key))
    saf_ids = set(pw[pw.position.isin(SAFETY)].player_id)
    roster = pw[["season", "team", "player_id", "fk", "sk"]].drop_duplicates()
    ids = pf[["season", "team", "pfr_player_id", "fk", "sk"]].drop_duplicates()
    t1 = ids.merge(roster[["season", "team", "fk", "player_id"]].drop_duplicates(), on=["season", "team", "fk"])
    left = ids[~ids.set_index(["season", "pfr_player_id"]).index.isin(t1.set_index(["season", "pfr_player_id"]).index)]
    uniq_r = roster.groupby(["season", "team", "sk"]).player_id.nunique().rename("nr").reset_index()
    uniq_p = ids.groupby(["season", "team", "sk"]).pfr_player_id.nunique().rename("np").reset_index()
    t2 = (left.merge(uniq_r[uniq_r.nr == 1], on=["season", "team", "sk"]).merge(uniq_p[uniq_p.np == 1], on=["season", "team", "sk"])
          .merge(roster[["season", "team", "sk", "player_id"]].drop_duplicates(), on=["season", "team", "sk"]))
    link = pd.concat([t1, t2])[["season", "pfr_player_id", "player_id"]].drop_duplicates()
    link = link[~link.duplicated(["season", "pfr_player_id"], keep=False)]   # same name, two players (e.g. NYJ Michael Carter): drop
    link = link[link.player_id.isin(saf_ids)]
    # a player counts as a safety in a season if nflverse lists him at a safety position that season
    pos = pw[pw.position.isin(SAFETY)][["season", "player_id"]].drop_duplicates()
    link = link.merge(pos, on=["season", "player_id"])
    assert not link.duplicated(["season", "player_id"]).any()
    return pf.merge(link, on=["season", "pfr_player_id"]), int(len(t2.merge(link, on=["season", "pfr_player_id", "player_id"])))


def safety_seasons():
    pw = query("""SELECT season, week, team, player_id, player_display_name AS name, position, def_interceptions AS i
                  FROM raw_player_week WHERE season_type='REG'""")
    pw = pw[(pw.season < SEASON) | (pw.week <= THRU)]
    pf = query("""SELECT season, week, team, pfr_player_name AS name, pfr_player_id, def_ints, def_targets, def_completions_allowed,
                  def_yards_allowed, def_missed_tackles, def_tackles_combined FROM raw_pfr_def WHERE game_type='REG'""")
    pf = pf[(pf.season < SEASON) | (pf.week <= PFR_THRU)]
    x, n_tier2 = match_safeties(pw, pf)
    s = x.groupby(["season", "pfr_player_id"]).agg(
        name=("name", "last"), g=("week", "nunique"), ints=("def_ints", "sum"), tgt=("def_targets", "sum"),
        cmp=("def_completions_allowed", "sum"), yds=("def_yards_allowed", "sum"), mt=("def_missed_tackles", "sum"),
        tk=("def_tackles_combined", "sum")).reset_index()
    s["ypt"] = s.yds / s.tgt
    s["cmp_pct"] = s.cmp / s.tgt
    s["int_rate"] = s.ints / s.tgt
    s["mt_pct"] = s.mt / (s.mt + s.tk)
    return pw, x, s, n_tier2


def carryover(s, draws=2000, seed=0):
    q = s[(s.tgt >= MIN_TGT) & (s.season < SEASON)]
    a = q.merge(q, on="pfr_player_id", suffixes=("", "_n"))
    a = a[a.season_n == a.season + 1].reset_index(drop=True)
    mets = ("int_rate", "ypt", "cmp_pct", "mt_pct")
    out = {m: float(a[m].corr(a[m + "_n"])) for m in mets}
    # pairs share players (a middle season appears twice), so resample players, not pairs
    rng = np.random.default_rng(seed)
    players = a.pfr_player_id.unique()
    groups = {p: idx for p, idx in a.groupby("pfr_player_id").groups.items()}
    boot = {m: [] for m in mets}
    for _ in range(draws):
        idx = np.concatenate([groups[p] for p in rng.choice(players, len(players))])
        b = a.loc[idx]
        for m in mets:
            boot[m].append(b[m].corr(b[m + "_n"]))
    boot = {m: np.array(v) for m, v in boot.items()}
    ci = {m: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) for m, v in boot.items()}
    mt_ahead = float((boot["mt_pct"] > boot["int_rate"]).mean())
    big = a[a.ints >= 5]
    ex = dict(n=len(big), players=int(big.pfr_player_id.nunique()), repeat=int((big.ints_n >= 5).sum()),
              this=float(big.ints.mean()), nxt=float(big.ints_n.mean()), all_nxt=float(a.ints_n.mean()))
    return out, len(a), int(a.season.min()), int(a.season_n.max()), len(players), ci, mt_ahead, ex


def pass_d_by_pair(team, seasons):
    """Each game: the defense's pass plays, points allowed, and what that opponent's passing usually does
    (its points per pass play in its other games that season, games through week THRU in SEASON).
    Pair = the two safeties with the most defensive snaps, each on the field for 50%+ of them."""
    sl = ",".join(map(str, seasons))
    p = query(f"""SELECT season, week, posteam, defteam, epa FROM raw_pbp WHERE season_type='REG' AND qb_dropback=1
                  AND epa IS NOT NULL AND season IN ({sl}) AND COALESCE(two_point_attempt,0)=0""")
    p = p[(p.season < SEASON) | (p.week <= THRU)]
    g = p.groupby(["season", "week", "posteam", "defteam"]).agg(n=("epa", "size"), epa=("epa", "sum")).reset_index()
    tot = g.groupby(["season", "posteam"])[["n", "epa"]].sum()
    o = tot.loc[list(zip(g.season, g.posteam))].to_numpy()
    g["norm"] = (o[:, 1] - g.epa) / (o[:, 0] - g.n)          # opponent's points per pass play elsewhere
    g["vs"] = g.epa - g.norm * g.n                            # points allowed beyond that norm
    # the passer who led each team-game in dropbacks; "regular starter" = the one who did that in the most games
    sl_q = ",".join(map(str, [min(seasons) - 1] + list(seasons)))
    q = query(f"""SELECT season, week, posteam, COALESCE(passer_player_id, rusher_player_id) AS qb,
                  COALESCE(passer_player_name, rusher_player_name) AS qb_name FROM raw_pbp WHERE season_type='REG'
                  AND qb_dropback=1 AND epa IS NOT NULL AND season IN ({sl_q}) AND COALESCE(two_point_attempt,0)=0""")
    q = q[(q.season < SEASON) | (q.week <= THRU)]
    gq = (q.groupby(["season", "week", "posteam", "qb", "qb_name"]).size().rename("dbs").reset_index()
          .sort_values(["dbs", "qb"]).groupby(["season", "week", "posteam"]).tail(1))
    # regular starter as of each game: the passer who has led the team in the most games through that week (ties: dropbacks)
    def starter_asof(r):
        h = gq[(gq.season == r.season) & (gq.posteam == r.posteam) & (gq.week <= r.week)]
        t = h.groupby("qb").agg(gms=("week", "size"), dbs=("dbs", "sum")).reset_index().sort_values(["gms", "dbs", "qb"])
        return t.qb.iloc[-1]
    # ... or the team's main passer the season before (catches a starter returning from injury, e.g. Burrow 2025)
    prev = (gq.groupby(["season", "posteam", "qb"]).agg(gms=("week", "size"), dbs=("dbs", "sum")).reset_index()
            .sort_values(["gms", "dbs", "qb"]).groupby(["season", "posteam"]).tail(1).set_index(["season", "posteam"]).qb)
    gq = gq[gq.season.isin(seasons)].copy()
    gq["starter"] = [starter_asof(r) for r in gq.itertuples()]
    gq["prev"] = [prev.get((r.season - 1, r.posteam)) for r in gq.itertuples()]
    gq["backup"] = (gq.qb != gq.starter) & (gq.qb != gq.prev)
    g = g.merge(gq[["season", "week", "posteam", "qb_name", "backup"]], on=["season", "week", "posteam"])
    pass_d_by_pair.all_teams = g
    sn = query(f"""SELECT season, week, team, player, pfr_player_id, defense_snaps, defense_pct FROM raw_snap_counts
                   WHERE game_type='REG' AND season IN ({sl}) AND team='{team}' AND position IN ('S','FS','SS','SAF')""")
    sn = sn[(sn.season < SEASON) | (sn.week <= THRU)]
    rows = []
    for (se, wk), x in sn.groupby(["season", "week"]):
        x = x[x.defense_pct >= 0.5].sort_values("defense_snaps", ascending=False)
        rows.append((se, wk, list(x.player)))
    pr = pd.DataFrame(rows, columns=["season", "week", "safeties"])
    return g[g.defteam == team].merge(pr, on=["season", "week"]), sn


def main():
    pw, x, s, n_tier2 = safety_seasons()
    co, n_pairs, y0, y1, n_players, ci, mt_ahead, ex = carryover(s)
    lead = pw[pw.season == SEASON].groupby(["player_id", "name"]).i.sum()
    co_leaders = [n for (pid, n), v in lead.items() if v == lead.max() and pid != HOOKER]
    h_ints = int(lead.xs(HOOKER, level="player_id").iloc[0])
    h_games = int(pw[(pw.player_id == HOOKER) & (pw.season == SEASON)].week.nunique())
    career = int(pw[pw.player_id == HOOKER].i.sum())
    n_seasons = int(pw[pw.player_id == HOOKER].season.nunique())

    # ---- Bishop and his partner: Bills pass defense vs. each opponent's norm
    bg, bsn = pass_d_by_pair("BUF", [SEASON - 1, SEASON])
    bg = bg[bg.safeties.map(lambda v: "Cole Bishop" in v and len(v) >= 2)].copy()
    bg["partner"] = bg.safeties.map(lambda v: next(p for p in v if p != "Cole Bishop"))
    # Hamlin's week-9 game had Geno Stone as a third safety; the partner is the top-snap other safety (Hamlin)
    pr = bg.groupby(["season", "partner"]).agg(games=("week", "size"), plays=("n", "sum"), epa=("epa", "sum"),
                                               vs=("vs", "sum"), wks=("week", lambda w: f"{min(w)}-{max(w)}")).reset_index()
    pr["per"] = pr.vs / pr.plays
    pr["allowed"] = pr.epa / pr.plays
    pr = pr.sort_values(["season", "games"], ascending=[True, False])
    get = lambda se, nm: pr[(pr.season == se) & pr.partner.str.contains(nm)].iloc[0]
    poy, rap, cj, ham = get(SEASON - 1, "Poyer"), get(SEASON - 1, "Rapp"), get(SEASON, "Gardner"), get(SEASON, "Hamlin")
    ham_g = bg[(bg.season == SEASON) & (bg.partner.str.contains("Hamlin"))].sort_values("week")
    ham_opp = list(ham_g.posteam)
    ham_wo_min = ham_g[ham_g.posteam != "MIN"]
    ham_wo_min_per = ham_wo_min.vs.sum() / ham_wo_min.n.sum()
    reg = bg[~bg.backup]
    pr_reg = reg.groupby(["season", "partner"]).agg(games=("week", "size"), plays=("n", "sum"), vs=("vs", "sum"))
    pr_reg["per"] = pr_reg.vs / pr_reg.plays
    reg_of = lambda r: pr_reg.loc[(r.season, r.partner)] if (r.season, r.partner) in pr_reg.index else None
    nb = lambda r: int(bg[(bg.season == r.season) & (bg.partner == r.partner)].backup.sum())
    ham_lv = ham_g[~ham_g.backup].iloc[0]
    # how often a gap as big as Poyer vs. Gardner-Johnson shows up by chance: shuffle which games go to which partner
    gp = bg[((bg.season == poy.season) & (bg.partner == poy.partner)) | ((bg.season == cj.season) & (bg.partner == cj.partner))]
    lab = (gp.partner == poy.partner).to_numpy()
    vs_, n_ = gp.vs.to_numpy(), gp.n.to_numpy()
    gap = vs_[~lab].sum() / n_[~lab].sum() - vs_[lab].sum() / n_[lab].sum()
    rng = np.random.default_rng(0)
    perm = []
    for _ in range(20000):
        l2 = rng.permutation(lab)
        perm.append(vs_[~l2].sum() / n_[~l2].sum() - vs_[l2].sum() / n_[l2].sum())
    p_gap = float((np.abs(np.array(perm)) >= abs(gap)).mean())   # two-sided: a gap this big either way
    # league context: the same number for every defense, full 2025 and 2026 through week THRU
    lgx = pass_d_by_pair.all_teams
    tv = lgx.groupby(["season", "defteam"]).agg(vs=("vs", "sum"), n=("n", "sum"))
    tv["per"] = -(tv.vs / tv.n)                                   # + = better than norm
    rank_in = lambda se, v: int((tv.loc[se].per > v).sum()) + 1
    poy_rank, cj_rank = rank_in(SEASON - 1, -poy.per), rank_in(SEASON, -cj.per)
    buf25, buf26 = tv.loc[(SEASON - 1, "BUF")].per, tv.loc[(SEASON, "BUF")].per
    buf25_rk, buf26_rk = rank_in(SEASON - 1, buf25), rank_in(SEASON, buf26)
    # worked example: the Bills' worst Gardner-Johnson game
    wx = bg[(bg.season == SEASON) & (bg.partner == cj.partner)].assign(pp=lambda d: d.vs / d.n).sort_values("pp").iloc[-1]
    team_name = {"LA": "Rams", "DET": "Lions", "NE": "Patriots", "LAC": "Chargers", "HOU": "Texans"}
    # Bishop's own coverage with each partner (PFR charting, by game)
    bp = query(f"""SELECT season, week, def_targets t, def_yards_allowed y FROM raw_pfr_def WHERE game_type='REG' AND pfr_player_id='BishCo00'
                   AND (season < {SEASON} OR week <= {PFR_THRU})""")
    bp = bp.merge(bg[["season", "week", "partner"]], on=["season", "week"]).groupby(["season", "partner"])[["t", "y"]].sum()
    bp["ypt"] = bp.y / bp.t
    bish_cj = bp.loc[(SEASON, cj.partner)]
    bish_poy = bp.loc[(SEASON - 1, poy.partner)]
    saf_ypt = s.groupby("season").apply(lambda d: d.yds.sum() / d.tgt.sum())
    pfr_thru = PFR_THRU

    # ---- Hooker on a bad Tennessee defense
    td = query(f"""SELECT team, pfr_player_id id, pfr_player_name name, def_targets t, def_yards_allowed y, def_ints i,
                   def_missed_tackles mt, def_tackles_combined tk FROM raw_pfr_def WHERE game_type='REG' AND season={SEASON} AND week<={PFR_THRU}""")
    tmy = td.groupby("team")[["y", "t"]].sum()
    tmy["ypt"] = tmy.y / tmy.t
    ten_rank, n_teams = int(tmy.ypt.rank(method="min")["TEN"]), len(tmy)
    lg_ypt = td.y.sum() / td.t.sum()
    ten = td[td.team == "TEN"].groupby("id")[["t", "y", "i", "mt", "tk"]].sum()
    hk, rest = ten.loc[HOOKER_PFR], ten.drop(HOOKER_PFR)
    ten_ints, rest_ints = int(ten.i.sum()), int(rest.i.sum())
    rest_ypt, hk_ypt = rest.y.sum() / rest.t.sum(), hk.y / hk.t
    # tackling among safeties (same safety universe as before)
    z = s[(s.season == SEASON) & (s.tgt >= MIN_TGT_SEASON)].copy()
    z["rk_mt"] = z.mt_pct.rank(method="min")
    hz = z[z.pfr_player_id == HOOKER_PFR].iloc[0]
    mt_tied = int((z.mt_pct == hz.mt_pct).sum()) > 1
    lg26_mt = z.mt.sum() / (z.mt.sum() + z.tk.sum())
    left = int(query(f"""SELECT COUNT(*) AS n FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week>{THRU}
                         AND (home_team='BUF' OR away_team='BUF')""").n.iloc[0])
    nm = lambda full: full.split()[-1] if "Gardner" not in full else "Gardner-Johnson"

    # ---- chart 1: Bishop's partner, all games and against regular starters only
    fig, ax = plt.subplots(figsize=(9.5, 5.0), dpi=200)
    order = [poy, rap, cj, ham]
    labels = [f"{r.partner}\n{int(r.season)}, {r.games} games" + (f" ({nb(r)} vs. " + ("a backup QB)" if nb(r) == 1 else "backup QBs)") if nb(r) else "") for r in order]
    ys = np.arange(len(order))[::-1] * 1.0
    for y_, r in zip(ys, order):
        v_all = -r.per
        rr = reg_of(r)
        v_reg = -rr.per if rr is not None else None
        ax.barh(y_ + 0.17, v_all, 0.32, color=GRAY if r is ham else (BLUE if v_all > 0 else RED), zorder=2)
        ax.text(v_all + (0.01 if v_all >= 0 else -0.01), y_ + 0.17, f"{v_all:+.2f}", va="center", ha="left" if v_all >= 0 else "right",
                fontsize=9.5, fontweight="bold", color=INK)
        if v_reg is not None:
            ax.barh(y_ - 0.17, v_reg, 0.32, color="#C9CDD4", zorder=2)
            if r is poy:
                ax.text(-0.01, y_ + 0.17, "All games", ha="right", va="center", fontsize=8.5, color=MUTED)
                ax.text(-0.01, y_ - 0.17, "Starting QBs only", ha="right", va="center", fontsize=8.5, color=MUTED)
            ax.text(v_reg + (0.01 if v_reg >= 0 else -0.01), y_ - 0.17, f"{v_reg:+.2f}", va="center", ha="left" if v_reg >= 0 else "right",
                    fontsize=9, color=MUTED)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_yticks(ys, labels, fontsize=9.5)
    lim = 0.55
    ax.set_xlim(-lim, lim)
    ax.set_xlabel("Points per pass play, better (+) or worse (-) than what that opponent usually does", fontsize=9.5)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "The Bills' pass defense has tracked with Cole Bishop's partner",
           "Games where Bishop and the partner both played most snaps. Gray Hamlin bar: 2 of 3 games vs. backup QBs.",
           f"What that opponent usually does = its points per pass play in its other games that season. {int(pr.plays.sum())} pass plays, "
           f"{SEASON - 1} and {SEASON} through week {THRU}.", src="Source: nflverse play-by-play and snap counts. Regular season.")
    fig.savefig(OUT / "hooker-bishop-partner.png"); plt.close(fig)

    # ---- chart 2: Tennessee's interceptions
    fig, ax = plt.subplots(figsize=(9.5, 4.0), dpi=200)
    ax.barh([1, 0], [h_ints, rest_ints], color=[BLUE, GRAY], height=0.55, zorder=2)
    ax.set_yticks([1, 0], ["Amani Hooker", "Every other Titan"], fontsize=11)
    for y_, v in ((1, h_ints), (0, rest_ints)):
        ax.text(v + 0.08, y_, str(v), va="center", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlim(0, max(h_ints, rest_ints) + 1); ax.set_xticks(range(0, max(h_ints, rest_ints) + 1))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"On a bad defense, Hooker made the plays: {h_ints} of Tennessee's {ten_ints} interceptions",
           f"Interceptions, {SEASON} weeks 1-{THRU} (Tennessee's bye was week 9). Tennessee ranks {ordn(ten_rank)} of {n_teams} in yards allowed per throw.",
           f"Hooker played {h_games} games.", src="Source: Pro Football Reference charting via nflverse. Regular season.")
    fig.savefig(OUT / "hooker-ten-ints.png"); plt.close(fig)

    lead_txt = f"tied with {co_leaders[0]} for the NFL lead" if len(co_leaders) == 1 else "the NFL lead"
    poy_reg, rap_reg, cj_reg = reg_of(poy), reg_of(rap), reg_of(cj)
    chance = round(1 / p_gap) if p_gap > 0 else None
    md = f"""# What the Bills get in Amani Hooker: a ball hawk, and a new partner for Cole Bishop

**Amani Hooker has {h_ints} of Tennessee's {ten_ints} interceptions this season, {lead_txt}, on a defense that ranks {ordn(ten_rank)} of {n_teams} in yards
allowed per throw. He's also tackling well. And he steps into the open question on the Bills' defense: the spot next to Cole Bishop, where the
pass defense has tracked with whoever's played there. With Jordan Poyer there last season,
opponents' passing did {-poy.per:.2f} points a play worse than usual against Buffalo, about {ordn(poy_rank)}-best in the league. With C.J. Gardner-Johnson
this season, it's done {cj.per:.2f} better than usual, about {ordn(cj_rank)} of 32. Bishop's own coverage barely changed between the two.**

Small samples, and other things changed along with Bishop's partner. Details below.

*The Bills traded a 2027 second-round pick to Tennessee for Hooker and a 2027 fifth-round pick on Tuesday, Nov. 10, deadline day. He's
signed through 2028. (Trade terms as announced by the Bills.) Game results are through week {THRU} of the {SEASON} season. Yards-per-throw and
tackling numbers come from Pro Football Reference's charting, which is through week {pfr_thru}.*

*Updated Nov. 11: headline, lead and story order revised to lead with Hooker. No numbers changed.*

## What Hooker brings: the one making plays in Tennessee

Tennessee's defense has been bad: passes against it have gained {tmy.loc['TEN', 'ypt']:.1f} yards per throw, {ordn(ten_rank)} of {n_teams} (league average
{lg_ypt:.1f}). Hooker has been the exception. His {h_ints} interceptions came in {h_games} games;
everyone else on that defense has {rest_ints} combined. He tackles well, too: {int(hz.mt)} misses on {int(hz.mt + hz.tk)} tries ({hz.mt_pct:.1%}),
against {lg26_mt:.1%} for the average safety. That {'ties him for' if mt_tied else 'puts him'} {ordn(int(hz.rk_mt))}-best of {len(z)} regular safeties.

![Tennessee's interceptions](hooker-ten-ints.png)

One honest caveat: in yards allowed per throw, he's been about the same as his teammates ({hk_ypt:.1f} on {int(hk.t)} throws vs. {rest_ypt:.1f} for the rest
of the defense). The case for Hooker is the ball-hawking and the tackling, not that throws at him go nowhere. All of this is seven games, a small
sample.

## What it means for Bishop: the partner problem

![Bishop's partner](hooker-bishop-partner.png)

Hooker likely takes the spot beside Bishop that Gardner-Johnson and Hamlin have split. Here's how the Bills' pass defense did in games
where Bishop and each partner both played most of the snaps:

| Bishop's partner | Games | Points per pass play vs. opponent's usual (+ = better) | Starting QBs only |
|---|---|---|---|
| Jordan Poyer, {SEASON - 1} | {poy.games} | {-poy.per:+.2f} | {-poy_reg.per:+.2f} ({int(poy_reg.games)} games) |
| Taylor Rapp, {SEASON - 1} | {rap.games} | {-rap.per:+.2f} | {-rap_reg.per:+.2f} ({int(rap_reg.games)} games) |
| C.J. Gardner-Johnson, {SEASON} | {cj.games} | {-cj.per:+.2f} | {-cj_reg.per:+.2f} ({int(cj_reg.games)} games) |
| Damar Hamlin, {SEASON} | {ham.games} | {-ham.per:+.2f} | {-ham_lv.vs / ham_lv.n:+.2f} (1 game) |

For scale: across all 32 defenses, the Bills were {buf25:+.2f} over all of {SEASON - 1} ({ordn(buf25_rk)}) and are {buf26:+.2f} so far this season ({ordn(buf26_rk)}).
Every row is a small sample, {min(r.games for r in (poy, rap, cj, ham))} to {max(r.games for r in (poy, rap, cj, ham))} games.

**Hamlin's {-ham.per:+.2f} needs an asterisk.** Two of his three games, Baltimore and Minnesota, came against backup quarterbacks. The one against a
regular starter, Las Vegas, came out {-ham_lv.vs / ham_lv.n:+.2f}, as bad as the Gardner-Johnson games.

What this means for Bishop himself: his own coverage barely moved. Throws his way gained {bish_poy.ypt:.1f} yards each with Poyer beside him ({int(bish_poy.t)} throws) and {bish_cj.ypt:.1f} with
Gardner-Johnson ({int(bish_cj.t)}). Both are a bit worse than the average safety ({saf_ypt.loc[SEASON - 1]:.1f} and {saf_ypt.loc[SEASON]:.1f}), on small samples.
The difference was around him. That's the spot Hooker steps into. Whether it helps is what we'll track.

**Where these numbers come from.** Every pass play starts from a spot on the field where an average offense can expect a certain number of points,
and the play raises or lowers that number. We add those changes up for each opponent's passes against Buffalo, then compare them with what the same
offense does in its other games that season. Example: the {team_name.get(wx.posteam, wx.posteam)} normally gain about {wx.norm:.2f} points per pass play. In week {int(wx.week)}
their {int(wx.n)} pass plays against Buffalo were worth {wx.epa:.1f} points combined, about {wx.vs / wx.n:.2f} a play more than usual. That game counts as
{-wx.vs / wx.n:+.2f} for Buffalo, one of the {cj.games} games behind Gardner-Johnson's {-cj.per:+.2f}. The partner is the other safety on the field for the most
snaps, from the league's snap counts.

**How we checked it.**
- **Luck.** We shuffled the {poy.games + cj.games} Poyer and Gardner-Johnson games between the two groups 20,000 times. A gap this big (either way) showed
  up about 1 time in {chance}. Suggestive, not proof.
- **Quarterbacks.** Two of Poyer's games came against backups. Without them his number drops to {-poy_reg.per:+.2f}. All {cj.games} Gardner-Johnson games
  came against regular starters.
- **Everything else that changed.** This season also brought a new defensive coordinator, Jim Leonhard, and other roster changes. These numbers
  can't separate those from the safety next to Bishop.


## What it means

- **It's about the pair, not just the player.** Against starting quarterbacks, Buffalo's best stretch with Bishop came with a steady veteran beside him. Hooker is in his
  {n_seasons}th season and making plays.
- **What we'll track.** Bills pass defense against what each opponent usually does, with Bishop and Hooker together, over the {left} games left, with backup-QB
  games marked. If it climbs back toward the Poyer-era level against starting quarterbacks ({-poy_reg.per:+.2f}), that fits the trade working. It still
  won't separate Hooker from the new coordinator.
- **It's a real price.** Per the Bills, it's the most draft capital the team has used to acquire a player at the trade deadline under general
  manager Brandon Beane: a second-round pick for a title push this season, with two more years of Hooker after it.

## For the stat-heads

- Pass defense: nflverse play-by-play, dropbacks (pass attempts, sacks, scrambles; no two-point tries), EPA allowed, regular season. Opponent's
  norm = that offense's EPA per dropback in its other games that season ({SEASON} through week {THRU}). Value = (EPA allowed - norm x dropbacks)
  / dropbacks, sign flipped so + = better than norm. Counts every Bills dropback in the game, not only snaps with both safeties on the field.
- League context: same value for all 32 defenses. {-poy.per:+.3f} would rank {ordn(poy_rank)} among {SEASON - 1} defenses; {-cj.per:+.3f} {ordn(cj_rank)} among {SEASON}.
- Pairings: nflverse snap counts (`raw_snap_counts`), safeties (S/FS/SS/SAF) with 50%+ of defensive snaps; partner = the other one with the
  most snaps. Bishop + {poy.partner}: weeks {poy.wks}, {int(poy.plays)} dropbacks; + {rap.partner}: weeks {rap.wks}, {int(rap.plays)}; + {cj.partner}:
  weeks {cj.wks}, {int(cj.plays)}; + {ham.partner}: weeks {ham.wks}, {int(ham.plays)}. Week 6 {SEASON} was shared (Hamlin over 50%, Gardner-Johnson under);
  week 9 also had Geno Stone at 50%+. Games where Bishop played under 50%, or where the other safety is listed as "DB" (week 17 {SEASON - 1},
  Cameron Lewis), are excluded. Not adjusted for cornerbacks, pass rush, coordinator or injuries.
- Backup QB: the passer who led a team-game in dropbacks, when he is neither the one who has led that team in the most games through that
  week (ties: dropbacks) nor the team's main passer the season before. Flagged games in these pairings: {'; '.join(f"{int(r.season)} wk {int(r.week)} {r.posteam} ({r.qb_name})" for r in bg[bg.backup].sort_values(['season', 'week']).itertuples())}.
- Chance check: permutation of the {poy.games + cj.games} games between Poyer and Gardner-Johnson labels, 20,000 draws (seed 0), dropback-weighted;
  two-sided p = {p_gap:.3f} for a gap of {gap:.3f}.
- Bishop coverage by partner (PFR charting): {SEASON - 1} with Poyer {int(bish_poy.t)} targets, {bish_poy.ypt:.2f} yards/target; {SEASON} with
  Gardner-Johnson {int(bish_cj.t)} targets, {bish_cj.ypt:.2f}. Matched safeties: {saf_ypt.loc[SEASON - 1]:.2f} ({SEASON - 1}), {saf_ypt.loc[SEASON]:.2f} ({SEASON}).
- Tennessee {SEASON}: PFR charting through week {pfr_thru} (Tennessee's week-9 bye means it's complete for them): all charted defenders
  {tmy.loc['TEN', 'ypt']:.2f} yards/target ({ordn(ten_rank)} of {n_teams}, 1st = fewest); Hooker {hk_ypt:.2f} on {int(hk.t)}; rest {rest_ypt:.2f} on {int(rest.t.sum())}.
  Interceptions: {ten_ints} team, {h_ints} Hooker (PFR and nflverse agree). The tie for the NFL lead ({', '.join(co_leaders) or 'none'}) is from nflverse
  player stats through week {THRU}; PFR hadn't charted Green Bay's week 9 as of {AS_OF}. Career: {career} regular-season interceptions.
- Missed-tackle rate = missed / (missed + combined tackles), safeties with {MIN_TGT_SEASON}+ targets ({len(z)}). PFR safeties matched to nflverse
  by season, team and name (suffixes removed; {n_tier2} by initial + last name where unique); DB-labeled players excluded.
- Trade terms and "most draft capital ... at the trade deadline under Beane": buffalobills.com, "Bills land impact safety Amani Hooker in trade
  with Titans" and "'A difference maker'...", Nov. 10, 2026.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "The Hooker trade",
        "big": [[h_ints, f"of Tennessee's {ten_ints} interceptions"], [round(float(-cj.per), 2), "Bills vs. opponents' usual passing, per play, with Gardner-Johnson"]],
        "note": f"With Poyer beside Bishop, opponents' passing did {-poy.per:.2f} points a play worse than usual against Buffalo. With Gardner-Johnson, it's done {cj.per:.2f} better than usual.",
        "explainer": {"kicker": "Bishop's partner", "title": "Bills vs. what opponents' passing usually does, per play.",
                      "text": "Better (+) or worse (-) than each opponent usually does:", "fmt": "score",
                      "bars": [[f"{nm(r.partner)} ({int(r.season)}" + (f", {nb(r)} vs. " + ("a backup)" if nb(r) == 1 else "backups)") if nb(r) else ")"), round(float(-r.per), 2)] for r in order]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
