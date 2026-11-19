"""How often do big NFL mismatches go wrong? 25 years of lopsided games, and where Bills-Dolphins (Week 11, 2026) fits.

History: every regular-season game 1999-2025 where both teams had played 4+ games. "Mismatch" = the gap between the two teams'
scoring margins (points scored minus allowed, per game) going into the game. No betting lines anywhere (brand rule): the
schedule table's market columns are never read.
Our model: points model v0.1 (src/ledger/points_model.py), pregame projections 2018-2026 (through Week 10 of 2026).
Pinned: history through 2025; 2026 through WEEK_DONE. Writes reports/2026-11-19-nfl-mismatches.md, two PNGs and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import points_model as pm
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.sabres_postgame import finish

OUT = ROOT / "reports"
SEASON, WEEK_DONE, GAME = 2026, 10, "2026_11_MIA_BUF"
MIN_GP = 4
BINS = [0, 3, 7, 10, 14, 17, 20, 99]
LABELS = ["0-3", "3-7", "7-10", "10-14", "14-17", "17-20", "20+"]
NAMES = {"BUF": "Bills", "TEN": "Titans", "MIA": "Dolphins", "JAX": "Jaguars", "NE": "Patriots", "STL": "Rams", "NO": "Saints", "DEN": "Broncos",
         "PIT": "Steelers", "WAS": "Washington", "OAK": "Raiders", "CHI": "Bears", "CIN": "Bengals", "CLE": "Browns", "NYG": "Giants",
         "SF": "49ers", "TB": "Buccaneers", "PHI": "Eagles", "DAL": "Cowboys"}


def pregame_margins(s):
    """Each team's scoring margin per game before each game, within the season (team codes are fixed within a season)."""
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        t = s[["game_id", "season", "week", f"{side}_team", f"{side}_score", f"{opp}_score"]].copy()
        t.columns = ["game_id", "season", "week", "team", "pf", "pa"]
        rows.append(t)
    tg = pd.concat(rows).sort_values(["season", "team", "week"])
    tg["m"] = tg.pf - tg.pa
    tg["n_pre"] = tg.groupby(["season", "team"]).cumcount()
    tg["m_pre"] = tg.groupby(["season", "team"]).m.transform(lambda x: x.shift().expanding().mean())
    return tg.set_index(["game_id", "team"])[["m_pre", "n_pre"]]


def main():
    cols = "game_id, season, week, gameday, home_team, away_team, home_score, away_score"   # never the market columns
    s = query(f"SELECT {cols} FROM raw_schedules WHERE game_type = 'REG' AND (season < {SEASON} OR week <= {WEEK_DONE}) ORDER BY season, week")
    assert s.home_score.notna().all(), "unfinished game inside the pinned window"
    pre = pregame_margins(s)
    s = s.join(pre.rename(columns={"m_pre": "hm", "n_pre": "hn"}), on=["game_id", "home_team"]) \
         .join(pre.rename(columns={"m_pre": "am", "n_pre": "an"}), on=["game_id", "away_team"])
    d = s[(s.hn >= MIN_GP) & (s.an >= MIN_GP) & (s.season < SEASON)].copy()
    d["gap"] = (d.hm - d.am).abs()
    d["better_home"] = d.hm > d.am
    d["won"] = np.where(d.better_home, d.home_score > d.away_score, d.away_score > d.home_score)
    d["tie"] = d.home_score == d.away_score
    d["res"] = d.won.astype(float) + 0.5 * d.tie          # ties count half
    d["b"] = pd.cut(d.gap, BINS, right=False, labels=LABELS)
    tab = d.groupby("b", observed=True).agg(n=("res", "size"), won=("res", "mean"))
    n_hist, yr0, yr1 = len(d), int(d.season.min()), int(d.season.max())
    big = d[d.gap >= 17]
    big_rate, big_n, big_lost = big.res.mean(), len(big), int((~big.won & ~big.tie).sum())
    huge = d[d.gap >= 20]
    early, late = big[big.week <= 8], big[big.week > 8]
    assert 0.75 < big_rate < 0.82 and abs(huge.res.mean() - big_rate) < 0.03     # "about 4 in 5", "bigger gaps don't help"
    ups = big[~big.won & ~big.tie].sort_values("gap", ascending=False)
    buf_ups = ups[(ups.home_team == "BUF") | (ups.away_team == "BUF")]
    qbs = query("SELECT player, offense_snaps FROM raw_snap_counts WHERE game_id = '2024_18_BUF_NE' AND team = 'BUF' AND position = 'QB'").set_index("player").offense_snaps
    assert dict(qbs) == {"Josh Allen": 1, "Mitchell Trubisky": 48, "Mike White": 20}
    def where(r):
        opp = r.away_team if r.home_team == "BUF" else r.home_team
        txt = f"{'vs.' if r.home_team == 'BUF' else 'at'} {NAMES.get(opp, opp)} in {r.season}"
        if r.game_id == "2023_05_JAX_BUF": txt += " (in London)"
        if r.game_id == "2024_18_BUF_NE": txt += f" (Week 18: Josh Allen played {int(qbs['Josh Allen'])} snap, then Mitchell Trubisky and Mike White played the rest)"
        return txt
    bills_list = ", ".join(where(r) for r in buf_ups.sort_values(["season", "week"]).itertuples())
    assert len(buf_ups) == 5 and list(buf_ups.head(2).season) == [2021, 2023]   # two biggest: JAX 2021, NE 2023
    # the two teams' season-long margins, to show how early numbers overstate
    tg_all = []
    for side, opp in (("home", "away"), ("away", "home")):
        t = s[["season", f"{side}_team", f"{side}_score", f"{opp}_score"]].copy(); t.columns = ["season", "team", "pf", "pa"]; tg_all.append(t)
    tg_all = pd.concat(tg_all); tg_all["m"] = tg_all.pf - tg_all.pa
    season_m = tg_all.groupby(["season", "team"]).m.mean()
    big = big.assign(h_end=[season_m[(r.season, r.home_team)] for r in big.itertuples()],
                     a_end=[season_m[(r.season, r.away_team)] for r in big.itertuples()])
    big["gap_end"] = (big.h_end - big.a_end).abs()
    shrink = float(big.gap_end.mean() / big.gap.mean())
    ex = big[(big.season == 2021) & (big.week == 9) & (big.home_team == "JAX")].iloc[0]
    ex_b_end, ex_j_end = float(season_m[(2021, "BUF")]), float(season_m[(2021, "JAX")])
    buf_big = d[(d.gap >= 17) & (((d.home_team == "BUF") & d.better_home) | ((d.away_team == "BUF") & ~d.better_home))]
    buf_w, buf_l = int(buf_big.won.sum()), int((~buf_big.won & ~buf_big.tie).sum())
    assert (buf_w, buf_l, int(buf_big.tie.sum())) == (11, 5, 0)
    big_ties = int(big.tie.sum())
    assert shrink < 0.8

    # Bills-Dolphins: the same measure, 2026 through Week 10
    t26 = []
    for side, opp in (("home", "away"), ("away", "home")):
        t = s[s.season == SEASON][[f"{side}_team", f"{side}_score", f"{opp}_score"]].copy(); t.columns = ["team", "pf", "pa"]; t26.append(t)
    t26 = pd.concat(t26); t26["m"] = t26.pf - t26.pa
    m26 = t26.groupby("team").m.agg(["mean", "size"])
    bm, mm = float(m26.loc["BUF", "mean"]), float(m26.loc["MIA", "mean"])
    gap_now = bm - mm
    b_now = LABELS[np.searchsorted(BINS, abs(gap_now), side="right") - 1]
    hist_now = float(tab.loc[b_now, "won"]); n_now = int(tab.loc[b_now, "n"])
    gap_rank = int((m26["mean"] > bm).sum()) + 1
    mia_rank = int((m26["mean"] < mm).sum()) + 1
    sched = query(f"SELECT {cols} FROM raw_schedules WHERE game_id = '{GAME}'").iloc[0]
    assert (sched.home_team, sched.away_team, int(sched.week)) == ("BUF", "MIA", WEEK_DONE + 1)

    # our model: projections 2018-2026 (through Week 10) and Sunday's number
    coef, pairs = pm.paired_misses()
    fr = pm.build_frame(list(range(2018, SEASON + 1)), max_week={SEASON: WEEK_DONE})
    fr["pred"] = pm.predict(coef, fr.raw, fr.home)
    h, a = fr[fr.home == 1].set_index("game_id"), fr[fr.home == 0].set_index("game_id")
    g = h.join(a[["team", "pred", "score"]], rsuffix="_a").dropna(subset=["pred_a"])
    g["pm"] = (g.pred - g.pred_a).abs()
    g["won"] = np.where(g.pred > g.pred_a, g.score > g.score_a, g.score_a > g.score).astype(float) + 0.5 * (g.score == g.score_a)
    g["p"] = [max(pm.win_chance(x, y, pairs), 1 - pm.win_chance(x, y, pairs)) for x, y in zip(g.pred, g.pred_a)]
    g["blind"] = g.season >= 2024
    mb = [0, 3, 7, 10, 99]; ml = ["0-3", "3-7", "7-10", "10+"]
    g["b"] = pd.cut(g.pm, mb, right=False, labels=ml)
    mt = g.groupby("b", observed=True).agg(n=("won", "size"), won=("won", "mean"), said=("p", "mean"))
    m10, m10b = g[g.pm >= 10], g[(g.pm >= 10) & g.blind]
    m10t = g[(g.pm >= 10) & g.season.between(2019, 2023)]
    assert m10t.won.mod(1).eq(0).all()
    n14, max_pm = int((g.pm >= 14).sum()), float(g.pm.max())
    o, de, lg, pace, lgp = pm.ratings(pm._drives(), SEASON, WEEK_DONE + 1)
    rb, *_ = pm.raw_prediction(o, de, lg, pace, lgp, "BUF", "MIA")
    rm, *_ = pm.raw_prediction(o, de, lg, pace, lgp, "MIA", "BUF")
    pb, pmi = float(pm.predict(coef, rb, 1)), float(pm.predict(coef, rm, 0))
    p_buf = pm.win_chance(pb, pmi, pairs)
    assert 10 <= pb - pmi < 14 and 0.75 < p_buf < 0.85

    # ---- chart 1: history
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    xs = np.arange(len(tab))
    cols_ = [BLUE if lab != b_now else RED for lab in tab.index]
    ax.bar(xs, tab.won, color=cols_, width=0.62, zorder=2)
    for x_, (lab, r) in zip(xs, tab.iterrows()):
        ax.text(x_, r.won + 0.012, f"{r.won:.0%}", ha="center", fontsize=10.5, color=INK, fontweight="bold")
        ax.text(x_, 0.03, f"{int(r.n):,}\ngames", ha="center", fontsize=8.5, color="white")
    ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--")
    ax.text(0.5, 0.507, "coin\nflip", ha="center", va="bottom", fontsize=8, color=MUTED, linespacing=0.9)
    ax.set_xticks(xs, [f"{l}\npoints" for l in tab.index], fontsize=9.5)
    ax.set_xlabel("Gap between the two teams' scoring margins going in (points per game)")
    ax.set_ylim(0, 1); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("How often the team with the\nbetter scoring margin won")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    ax.annotate(f"Bills vs. Dolphins Sunday:\n{abs(gap_now):.1f}-point gap", (list(tab.index).index(b_now), hist_now), xytext=(0, 34), textcoords="offset points",
                ha="center", fontsize=9, color=RED, fontweight="bold")
    finish(fig, "Even the most lopsided NFL games go the other way about 1 in 5 times",
           f"Every regular-season game {yr0}-{yr1} where both teams had played {MIN_GP}+ games ({n_hist:,} games). Ties count as half a win.",
           "Scoring margin = points scored minus points allowed per game, that season, before the game.")
    fig.texts[-1].set_text(f"Source: nflverse schedules, {yr0}-{yr1} regular seasons.\nScoring margin = points scored minus points allowed per game, that season, before the game.")
    fig.savefig(OUT / "nfl-mismatch-history.png"); plt.close(fig)

    # ---- chart 2: our model
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(len(mt)); w = 0.36
    ax.bar(xs - w / 2, mt.said, w, color=GRAY, label="Our model's chance for the team it expected to win", zorder=2)
    ax.bar(xs + w / 2, mt.won, w, color=BLUE, label="How often that team actually won", zorder=2)
    for x_, (lab, r) in zip(xs, mt.iterrows()):
        ax.text(x_ - w / 2, r.said + 0.012, f"{r.said:.0%}", ha="center", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, r.won + 0.012, f"{r.won:.0%}", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_xticks(xs, [f"Model expected a\n{l.replace('+', ' or more')}-point win\n({int(r.n):,} games)" for l, r in mt.iterrows()], fontsize=9)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "When our model gives a team a chance, that team wins about that often",
           f"Pregame projections, {int(g.season.min())} to {SEASON} Week {WEEK_DONE} ({len(g):,} games). Built on 2019-23; it never saw the 2024-26 games.",
           f"Points model {pm.VERSION}. No betting lines used.")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play (drives) and schedules; Buffalo Quant Desk points model {pm.VERSION}.\nNo betting lines used.")
    fig.savefig(OUT / "nfl-mismatch-model.png"); plt.close(fig)

    up_rows = "\n".join(
        f"| {r.season}, Week {r.week} | {NAMES.get(r.home_team if not r.better_home else r.away_team, r.home_team if not r.better_home else r.away_team)} "
        f"{int(r.home_score if not r.better_home else r.away_score)}, {NAMES.get(r.away_team if not r.better_home else r.home_team, r.away_team if not r.better_home else r.home_team)} "
        f"{int(r.away_score if not r.better_home else r.home_score)} | {NAMES.get(r.away_team if not r.better_home else r.home_team, r.away_team if not r.better_home else r.home_team)} | {r.gap:.1f} |"
        for r in ups.head(8).itertuples())

    md = f"""# How often do big NFL mismatches go wrong? {yr1 - yr0 + 1} seasons of lopsided games, and where Bills-Dolphins fits

**Over {yr1 - yr0 + 1} seasons, when one NFL team's scoring margin was 17 or more points a game better than its opponent's, the better team won
{big_rate:.0%} of the time. About 1 in 5 still lost ({big_lost} of {big_n} games, plus {big_ties} tie), and past 17 points a bigger gap barely helped. Our own model
projects Bills {pb:.0f}, Dolphins {pmi:.0f} on Sunday, and gives Buffalo an {p_buf:.0%} chance to win. History and our model point the same
way: about 4 times in 5.**

*Regular season only. History covers {yr0}-{yr1}; this season counts through Week {WEEK_DONE}. We don't use betting lines: every number here comes from game
results and our own model.*

![Win rate by size of mismatch](nfl-mismatch-history.png)

## How we measured a mismatch

For every regular-season game since {yr0}, we took each team's scoring margin going in: points scored minus points allowed, per game, that season, before
that game. The gap between the two teams' margins is the size of the mismatch. We only counted games where both teams had played at least {MIN_GP} games, which
leaves {n_hist:,} games. Then we checked how often the team with the better margin won. Ties count as half a win.

| Gap going in (points per game) | Games | Better team won |
|---|---|---|
""" + "\n".join(f"| {lab} | {int(r.n):,} | {r.won:.0%} |" for lab, r in tab.iterrows()) + f"""

## Why the biggest gaps stop helping

The better team's win rate climbs with the gap, then flattens out around {big_rate:.0%}. One big reason is that a few weeks of scores exaggerate how far apart
two teams really are. In the games with a gap of 17 or more, by the end of those seasons the gap between the same two teams had shrunk by about
{1 - shrink:.0%}. Take the 2021 Bills at Jacksonville: going in, Buffalo had outscored opponents by {ex.am:.1f} points a game and the Jaguars had been
outscored by {abs(ex.hm):.1f}, a gap of about {ex.gap:.1f} points. By season's end it was Buffalo {ex_b_end:+.1f} and Jacksonville {ex_j_end:+.1f}, a gap of {ex_b_end - ex_j_end:.1f}. A team that has been crushing people is usually good, but not as good as its early scores say, and the same goes in reverse.
Early in the season the effect is stronger: with a 17-point gap or more, the better team won {early.res.mean():.0%} through Week 8 ({len(early)} games) and {late.res.mean():.0%} after ({len(late)} games).

## The biggest upsets since {yr0}

| Season | Final | Better team going in | Gap (points per game) |
|---|---|---|---|
{up_rows}

Miami pulled one of them off, in Chicago in 2006. The Bills have been the much better team (a gap of 17 or more) {buf_w + buf_l} times since {yr0}: they went {buf_w}-{buf_l}. The losses: {bills_list}.

## Sunday: Dolphins at Bills

By the same measure, the Bills have outscored opponents by {bm:.1f} points a game this season ({gap_rank}{'st' if gap_rank == 1 else 'th' if gap_rank > 3 else {2: 'nd', 3: 'rd'}[gap_rank]}
of 32 teams) and Miami has been outscored by {abs(mm):.1f} ({33 - mia_rank}th). That's a gap of {abs(gap_now):.1f} points a game.
In the last {yr1 - yr0 + 1} seasons, the better team won {hist_now:.0%} of games with a gap that size ({n_now:,} games).

**Our model's number: Bills {p_buf:.0%}, right next to the {hist_now:.0%} history gives.** It projects about {pb:.0f} points for Buffalo and {pmi:.0f} for Miami. It's built from each offense's points per drive
and each defense's points allowed per drive this season, blended with last season's numbers and pulled toward the league average while the season is young,
plus how many drives each team usually gets and home field. The model's pull toward the middle is why it rarely expects a blowout: in {len(g):,} games since {int(g.season.min())} it has expected a
team to win by 14 or more only {n14} times, and never by more than about {max_pm:.0f}.

![Our model's projections vs. results](nfl-mismatch-model.png)

**How we checked it.** When our model expected a team to win by 10 or more, that team won {m10.won.mean():.0%} of {len(m10)} games ({int(m10t.won.sum())} of {len(m10t)} in the seasons it was built on). In games from 2024 on, which it never
saw while being built, teams it expected to win by 10 or more went {int(m10b.won.sum())}-{len(m10b) - int(m10b.won.sum())}. That's a small group; the bigger point is that at every level, the teams it
expected to win won about as often as it said.

This is our model's number. It counts once it's logged on the [Ledger](../ledger.html) before kickoff, and every logged call is graded after the game, hit or miss.

## For the stat-heads

- History: nflverse schedules, regular season {yr0}-{yr1}, games where both teams had {MIN_GP}+ prior games that season ({n_hist:,}). Pregame margin = mean
  (PF - PA) over prior games that season. Ties = 0.5. Gap 17+: {big_n} games, {big_rate:.3f}; gap 20+: {len(huge)} games, {huge.res.mean():.3f}.
  Same games' full-season margin gap / pregame gap = {shrink:.2f}.
- Model: points model {pm.VERSION} (drive-based, trained 2019-23; K={pm.K}, prior keep {pm.PRIOR_KEEP}); win chance from paired training misses.
  Projections {int(g.season.min())}-{SEASON} Wk{WEEK_DONE}, Weeks 2+ only (the model needs a prior week): {len(g):,} games. By projected margin: """ + "; ".join(
        f"{lab}: n={int(r.n)}, said {r.said:.3f}, won {r.won:.3f}" for lab, r in mt.iterrows()) + f""".
  2018 projections have no prior-season blend for 2017 (data starts 2018). BUF-MIA: {pb:.2f} vs {pmi:.2f}, P(BUF) {p_buf:.3f}.
- No market data read: the schedule query selects only game, team and score columns.
"""
    (OUT / "2026-11-19-nfl-mismatches.md").write_text(md)
    (OUT / "2026-11-19-nfl-mismatches.hero.json").write_text(json.dumps({
        "label": f"Lopsided NFL games, {yr0}-{yr1}",
        "big": [[f"{big_rate:.0%}", "How often the much better team won (17+ point gap in scoring margin)"],
                [f"{p_buf:.0%}", "Bills' chance vs. Miami Sunday, our model"]],
        "note": f"About 1 in 5 lopsided games still go the other way. The Bills have been the much better team and lost {buf_l} times since {yr0}, including at Jacksonville in 2021.",
        "explainer": {"kicker": "Past 17 points, a bigger gap barely helps", "title": "Better team's win rate", "text": "By gap in scoring margin going in:", "fmt": "pct",
                      "bars": [[f"{lab} pts", round(float(r.won), 3)] for lab, r in tab.iterrows()][2:]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
