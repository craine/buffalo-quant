"""Sabres pregame: Vegas at Buffalo, Sun Nov 8, 2026, 3:30 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-08-sabres-vgk-pregame.md, two PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
Win chance from nhl_game_model v0.1, tested on 2025-26 and 2026-27 games it never saw.
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.ledger import nhl_game_model as gmod
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SEASON, US, THEM = 20262027, "BUF", "VGK"
AS_OF = "2026-11-07"  # games through Saturday night; pinned so the published story doesn't change
GOLD = "#B4975A"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def main(as_of=AS_OF):
    s = shots()
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    g26 = gm[gm.season == SEASON]
    last_date = g26.game_date.max()

    # games played and records
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        rows.append(g26.rename(columns={side: "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "game_date", "team", "gf", "ga", "last_period_type"]])
    rec = pd.concat(rows)
    rec["w"] = rec.gf > rec.ga
    rec["otl"] = (rec.gf < rec.ga) & rec.last_period_type.isin(["OT", "SO"])
    rec["l"] = (rec.gf < rec.ga) & ~rec.last_period_type.isin(["OT", "SO"])
    gp = rec.groupby("team").game_id.nunique()

    # team chances (all situations, unblocked, empty net excluded), per game
    t = pd.DataFrame({"xgf": cur.groupby("team").xg.sum(), "xga": cur.groupby("opp").xg.sum(),
                      "gf_sh": cur.groupby("team").goal.sum(), "ga_sh": cur.groupby("opp").goal.sum(),
                      "close_f": cur[cur.dist < 20].groupby("team").size(), "close_a": cur[cur.dist < 20].groupby("opp").size(),
                      "reb_f": cur[cur.rebound == 1].groupby("team").size(), "reb_a": cur[cur.rebound == 1].groupby("opp").size(),
                      "reb_xgf": cur[cur.rebound == 1].groupby("team").xg.sum(), "reb_xga": cur[cur.rebound == 1].groupby("opp").xg.sum()}).fillna(0)
    t["gp"] = gp.reindex(t.index)
    for c in ["xgf", "xga", "close_f", "close_a", "reb_f", "reb_a", "reb_xgf", "reb_xga", "gf_sh", "ga_sh"]:
        t[c + "_pg"] = t[c] / t.gp
    t["share"] = t.xgf / (t.xgf + t.xga)
    rk = lambda col, team, high_good=True: int(t[col].rank(ascending=not high_good, method="min").loc[team])
    lg = t[["xgf_pg", "close_f_pg", "reb_f_pg"]].mean()
    b, v = t.loc[US], t.loc[THEM]
    recd = lambda tm: f"{int(rec[rec.team == tm].w.sum())}-{int(rec[rec.team == tm].l.sum())}-{int(rec[rec.team == tm].otl.sum())}"
    gfa = rec.groupby("team").agg(GF=("gf", "sum"), GA=("ga", "sum"))

    # last 5 games: share of chances
    def last5(tm):
        ids = rec[rec.team == tm].sort_values("game_date").game_id.tail(5)
        x = cur[cur.game_id.isin(ids)]
        f_, a_ = x[x.team == tm].xg.sum(), x[x.opp == tm].xg.sum()
        return f_ / (f_ + a_), len(ids)
    b5, nb5 = last5(US)
    l5 = rec[rec.team == US].sort_values("game_date").tail(5)
    l5_rec = f"{int(l5.w.sum())}-{int(l5.l.sum())}-{int(l5.otl.sum())}"
    v5, nv5 = last5(THEM)

    # explainer examples (prior seasons, so not circular)
    pri = u[u.season < SEASON]
    close10 = pri[pri.dist < 10].goal.mean()
    far60 = pri[pri.dist >= 60].goal.mean()
    reb_rate, non_rate = pri[pri.rebound == 1].goal.mean(), pri[pri.rebound == 0].goal.mean()
    n_pri = len(pri)

    # goalies: goals saved vs an average goalie this season
    gk = cur[cur.goalie_id.notna()].groupby(["opp", "goalie_id"]).agg(gp=("game_id", "nunique"), sog=("on_goal", "sum"),
                                                                         xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["gsax"] = gk.xga - gk.ga
    gk["name"] = gk.goalie_id.map(names)
    gk["sv"] = 1 - gk.ga / gk.sog
    tot = gk.groupby("goalie_id").gsax.sum()          # rank each goalie once, even if he played for two teams
    gk["rk"] = gk.goalie_id.map(tot.rank(ascending=False, method="min").astype(int))
    n_gk = len(tot)
    bg = gk[gk.opp == US].sort_values("gp", ascending=False)
    vg = gk[gk.opp == THEM].sort_values("gp", ascending=False)

    # ---- game prediction (NHL game model v0.1), pinned to games before Nov 8
    tg, coef, p_ot, home_rate = gmod.train()
    off_r, def_r, lg_r, ratio = gmod.ratings(tg, SEASON, "2026-11-08")
    mu_b = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, US, THEM), 1)
    mu_v = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, THEM, US), 0)
    p_b, p_tie = gmod.win_prob(mu_b, mu_v, p_ot)
    bt = {}
    for ss, mxd in ((20252026, None), (SEASON, as_of)):
        fr = gmod.build_frame(tg, [ss], max_date=mxd)
        gr = gmod.baselines(tg, gmod.game_rows(fr, coef, p_ot), home_rate)
        bt[ss] = dict(n=len(gr), brier=gmod.brier(gr.p_home, gr.home_won), b_home=gmod.brier(gr.b_home, gr.home_won),
                      b_rec=gmod.brier(gr.b_record, gr.home_won), right=((gr.p_home > .5) == gr.home_won).mean(),
                      home_obs=gr.home_won.mean(), g=gr)
    g25 = bt[20252026]["g"]
    fav = g25.p_home.where(g25.p_home >= .5, 1 - g25.p_home)
    fav_won = ((g25.p_home >= .5) == g25.home_won)
    cal_bins = [(0.5, 0.55), (0.55, 0.6), (0.6, 0.65), (0.65, 1.0)]
    calb = [(f"{int(lo*100)}-{int(min(hi,0.99)*100)}%" if hi < 1 else f"{int(lo*100)}%+", fav[(fav >= lo) & (fav < hi)].mean(),
            fav_won[(fav >= lo) & (fav < hi)].mean(), int(((fav >= lo) & (fav < hi)).sum())) for lo, hi in cal_bins]
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.model_version == gmod.VERSION] if not lp.empty else lp
    lp = lp[lp.claim_text.str.contains("Sabres", na=False)] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace("T", " ").rstrip("Z")} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- why goalies aren't in the model: half-season repeatability, goalies vs team chances allowed (complete seasons only)
    gg = gmod.goalie_games()
    rep_g, rep_t = [], []
    for ss in (20232024, 20242025, 20252026):
        x = gg[gg.season == ss]; mid = x.game_date.sort_values().iloc[len(x) // 2]
        h1 = x[x.game_date < mid].groupby("goalie_id").agg(sh=("shots", "sum"), xga=("xga", "sum"), ga=("ga", "sum"))
        h2 = x[x.game_date >= mid].groupby("goalie_id").agg(sh=("shots", "sum"), xga=("xga", "sum"), ga=("ga", "sum"))
        jj = h1.join(h2, lsuffix="1", rsuffix="2"); jj = jj[(jj.sh1 >= 400) & (jj.sh2 >= 400)]
        rep_g.append(np.corrcoef((jj.xga1 - jj.ga1) / jj.sh1, (jj.xga2 - jj.ga2) / jj.sh2)[0, 1])
        y = tg[tg.season == ss]; mid = y.game_date.sort_values().iloc[len(y) // 2]
        a1 = y[y.game_date < mid].groupby("team").xga.mean(); a2 = y[y.game_date >= mid].groupby("team").xga.mean()
        rep_t.append(np.corrcoef(a1, a2.reindex(a1.index))[0, 1])
    g_lo, g_hi, t_lo, t_hi = min(rep_g), max(rep_g), min(rep_t), max(rep_t)

    # ---- chart 3: how the model's chances held up on 2025-26
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(len(calb)); w = 0.36
    ax.bar(xs - w / 2, [c[1] for c in calb], w, color=GRAY, label="What the model said (favorite's chance)", zorder=2)
    ax.bar(xs + w / 2, [c[2] for c in calb], w, color=BLUE, label="How often the favorite actually won", zorder=2)
    for x_, c in zip(xs, calb):
        ax.text(x_ - w / 2, c[1] + 0.01, f"{c[1]:.0%}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, c[2] + 0.01, f"{c[2]:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_xticks(xs, [f"Favorite given {c[0]}\n({c[3]} games)" for c in calb], fontsize=9.5)
    ax.set_ylim(0, 0.9); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tested on 2025-26 games, the model's chances mostly held up",
           f"Every 2025-26 game ({bt[20252026]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-vgk-model-test.png"); plt.close(fig)

    # ---- chart 1: every team's chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, GOLD, "Golden Knights")):
        r = t.loc[tm]
        ax.scatter(r.xgf_pg, r.xga_pg, s=140, color=col, zorder=3, edgecolor="white", lw=1.5)
        ax.annotate(lab, (r.xgf_pg, r.xga_pg), xytext=(8, 6), textcoords="offset points", fontsize=11, fontweight="bold", color=INK)
    mx, my = t.xgf_pg.mean(), t.xga_pg.mean()
    ax.axvline(mx, color="#D5D8DE", lw=1, ls="--"); ax.axhline(my, color="#D5D8DE", lw=1, ls="--")
    ax.invert_yaxis()
    ax.text(t.xgf_pg.max(), t.xga_pg.min(), "Create a lot,\nallow little", ha="right", va="top", fontsize=9, color=MUTED)
    ax.text(t.xgf_pg.min(), t.xga_pg.max(), "Create little,\nallow a lot", ha="left", va="bottom", fontsize=9, color=MUTED)
    ax.set_xlabel("Chances created per game (goals they were worth)")
    ax.set_ylabel("Chances allowed per game (lower is better, so it's flipped)")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Vegas allows the {ordn(rk('xga_pg', THEM, False))}-fewest chances. Buffalo allows the {ordn(33 - rk('xga_pg', US, False))}-most",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Golden Knights {int(v.gp)}.")
    fig.savefig(OUT / "sabres-vgk-chances.png"); plt.close(fig)

    # ---- chart 2: rebounds — Sabres creating vs Vegas allowing, among 32 teams
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9), dpi=200)
    for ax, col, tm, title, lab in ((axes[0], "reb_f_pg", US, "Rebound shots created per game", "Sabres"),
                                    (axes[1], "reb_a_pg", THEM, "Rebound shots allowed per game", "Golden Knights")):
        srt = t[col].sort_values(ascending=False)
        cols = [(BLUE if tm == US else GOLD) if i == tm else "#C9CDD4" for i in srt.index]
        ax.bar(range(32), srt.values, color=cols, width=0.8, zorder=2)
        i = list(srt.index).index(tm)
        r_ = rk(col, tm, high_good=(tm == US))
        ax.text(i, srt.loc[tm] + (0.08 if tm == US else 0.75), f"{lab}\n{srt.loc[tm]:.1f} ({ordn(r_)}{'' if tm == US else ' fewest'})", ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.axhline(srt.mean(), color=INK, lw=1, ls="--")
        ax.set_xticks([]); ax.set_xlabel("32 teams, most to fewest")
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.set_ylim(0, srt.max() * 1.3); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo is {ordn(rk('reb_f_pg', US))} at creating rebound shots; Vegas is {ordn(rk('reb_a_pg', THEM, False))} at preventing them",
           "A rebound shot comes within 3 seconds of another shot by the same team. Dashed line: league average.",
           f"2026-27 through {pd.to_datetime(last_date):%b. %-d}. Unblocked shots, empty net excluded.")
    fig.savefig(OUT / "sabres-vgk-rebounds.png"); plt.close(fig)

    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Golden Knights'} | [{r['name']}](../cards/{re.sub(r'[^a-z0-9]+', '-', r['name'].lower()).strip('-')}.html) | {int(r.gp)} | {r.sv:.3f} | {r.gsax:+.1f} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    rb_rk_f, rb_rk_a = rk("reb_f_pg", US), rk("reb_a_pg", THEM, high_good=False)
    tie5 = "tied for " if (t.close_a_pg.round(4) == round(v.close_a_pg, 4)).sum() > 1 else ""
    md = f"""# Sabres vs. Golden Knights: Buffalo's attack meets one of the NHL's toughest defenses

**Finding: Vegas allows chances worth {v.xga_pg:.2f} goals a game, the {ordn(rk('xga_pg', THEM, False))}-fewest in the NHL, and few shots from close to its net
({tie5}{ordn(rk('close_a_pg', THEM, False))}-fewest). Buffalo's attack is middle of the pack ({ordn(rk('xgf_pg', US))} in chances created) but {ordn(rb_rk_f)} at creating rebound
shots. The bigger worry is at the other end: the Sabres allow chances worth {b.xga_pg:.2f} goals a game, {ordn(rk('xga_pg', US, False))} of 32.
Our model gives Vegas a {1 - p_b:.0%} chance to win and Buffalo {p_b:.0%}.**

*Vegas at Buffalo, Sunday, Nov. 8, 3:30 p.m. ET, KeyBank Center. Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}: Sabres
{recd(US)} in {int(b.gp)} games, Golden Knights {recd(THEM)} in {int(v.gp)}. Sixteen to 18 games is early; ranks can move a lot.*

![Chances created vs allowed](sabres-vgk-chances.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Over the last three seasons
({n_pri:,} unblocked shots), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add
up those chances on every shot and you get what a team's chances were worth in goals.

**The source:** the NHL's own play-by-play feed, which records where every shot came from. **The math:** each shot's chance
comes from our model, built on past seasons and tested on a season it hadn't seen before we added that season in; we nudge each season's totals so the
league's chances add up to the league's real goals. **How we checked it:** the full explanation, with the chart, is in our
story on [last year's 50-win season](sabres-50-win-mirage.html).

## The two teams, side by side

| Per game, 2026-27 | Sabres | Golden Knights | League average |
|---|---|---|---|
| Chances created (goals they were worth) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(rk('xga_pg', US, False))}) | {v.xga_pg:.2f} ({ordn(rk('xga_pg', THEM, False))}) | {lg.xgf_pg:.2f} |
| Share of the chances in their games | {b.share:.1%} ({ordn(rk('share', US))}) | {v.share:.1%} ({ordn(rk('share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Shots from within 20 feet | {b.close_f_pg:.1f} ({ordn(rk('close_f_pg', US))}) | {v.close_f_pg:.1f} ({ordn(rk('close_f_pg', THEM))}) | {lg.close_f_pg:.1f} |
| Shots allowed from within 20 feet | {b.close_a_pg:.1f} ({ordn(rk('close_a_pg', US, False))}) | {v.close_a_pg:.1f} ({ordn(rk('close_a_pg', THEM, False))}) | {lg.close_f_pg:.1f} |
| Share of chances, last {nb5} games | {b5:.1%} | {v5:.1%} | |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave
out empty-net shots.

## The matchup to watch: rebounds

A rebound shot catches the goalie moving. Over the last three seasons, rebounds went in {reb_rate:.1%} of the time, about
{reb_rate / non_rate:.1f} times the {non_rate:.1%} rate for every other shot.

![Rebounds](sabres-vgk-rebounds.png)

Buffalo gets {b.reb_f_pg:.1f} rebound shots a game ({ordn(rb_rk_f)} of 32; league average {lg.reb_f_pg:.1f}), worth {b.reb_xgf_pg:.2f} goals a game. Friday's
10 against Columbus was its season high. Vegas allows {v.reb_a_pg:.1f} a game, {ordn(rb_rk_a)} of 32 at keeping them down. Vegas's strength
is keeping shots away from the net in the first place. How many second looks Buffalo gets anyway is the part of this
matchup to watch.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good. Tap a name for
that goalie's card, with his season-by-season record.

| Team | Goalie | Games | Save rate | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. Buffalo has switched goalies every game for its last four, which points
to Colten Ellis on Sunday (WGR and Buffalo Hockey Beat both expect him). Vegas hadn't named a starter when we
published; NHL.com projects Adin Hill. These are small samples: a goalie's numbers over a dozen games can swing a lot.

## Our prediction: Vegas {1 - p_b:.0%}, Sabres {p_b:.0%}

{ledger_status}

Our model expects about **{mu_v:.1f} goals for Vegas and {mu_b:.1f} for Buffalo**, and gives about a {p_tie:.0%} chance the game is tied
after 60 minutes. Close to a coin flip, leaning Vegas.

**Where the number comes from.** The same chances numbers above. Buffalo creates chances worth {b.xgf_pg:.2f} goals a game; Vegas
allows {v.xga_pg:.2f}. Sixteen or 18 games is a small sample, so we blend each team's numbers with last season's, pulled halfway
toward the league average; Buffalo's attack counts as {off_r[US]:.2f} and Vegas's defense as {def_r[THEM]:.2f}. Start from the league's
{lg_r:.2f} per game, adjust for Buffalo's attack and Vegas's defense, and you get Buffalo's expected chances; do the same the
other way for Vegas. A final step, fit on past seasons, turns chances into goals and adds about {coef[2]:.2f} of a goal for playing at
home. Then we play the game out on paper: with those scoring rates, how often does each team end up ahead? Ties after 60 minutes
are split the way they went for home teams in past overtimes and shootouts ({p_ot:.0%} home wins).

![Model test](sabres-vgk-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only
what was known before each game. It called the winner {bt[20252026]['right']:.0%} of the time; choosing the home team every time would have been right
{bt[20252026]['home_obs']:.0%}. (The shot model behind the chances was later refit with 2025-26 included; re-running this test with a
version that never saw 2025-26 gave the same results.) Its percentages were also closer to what actually happened than two simple guesses, giving every home team
its usual edge or going by the teams' records, though not by much: a hockey game is close to a coin flip, and no model changes that.
This season so far ({bt[SEASON]['n']} games) it has called {bt[SEASON]['right']:.0%} right; home teams have won {bt[SEASON]['home_obs']:.0%}. When it made a team a 60-65% favorite in 2025-26, that team won
{calb[2][2]:.0%} of the time. But the teams it favored slightly, at 50-55%, won {calb[0][2]:.0%}, no better than a coin flip, and at 55-60% they won {calb[1][2]:.0%}. Sunday's call is in that range,
so read it as "slight lean Vegas," not "Vegas should win."

**What it doesn't count: goalies, and why.** The model rates teams by the chances they create and allow, not by who's in net.
We tested adding each game's starting goalie, rated on his record before that game, and it made the predictions no better. The
reason shows up in the data: a goalie's goals saved in the first half of a season tells you little about his second half. On a
scale where 1 means one half perfectly predicts the next and 0 means it tells you nothing, goalies came in between {g_lo:.2f} and {g_hi:.2f} over the last three seasons; a
team's chances allowed came in between {t_lo:.2f} and {t_hi:.2f}. Over a few dozen games, goalie numbers are mostly noise. So
while Buffalo's expected starter, Colten Ellis, is at {bg[bg.name == 'Colten Ellis'].gsax.sum():+.1f} this season and Adin Hill, NHL.com's projected Vegas starter, at {vg[vg.name == 'Adin Hill'].gsax.sum():+.1f}, that gap
tells us less than it looks like. Vegas's starter wasn't named when we published. We'll keep testing goalies as more seasons
of data come in; the cards track them in the meantime.

## What to watch

- **Second chances.** Count Buffalo's shots that come right after another shot. The Sabres' season average is {b.reb_f_pg:.1f}.
- **The goalies.** Whichever goalies start, the table above says how they've done against the chances they've faced.
- **Results vs. chances.** Buffalo is {l5_rec} in its last {nb5} games but has had only {b5:.0%} of the chances in them. Five games
  is a small sample, but over a full season, results that run ahead of the chances tend to fade (see our
  [50-win story](sabres-50-win-mirage.html)). Sunday is a test of whether the Sabres can win the chances, too.
- **Whether the chances turn into goals.** Over a full season, chances carry over from year to year much better than lucky
  or unlucky finishing, which is why we lead with them.

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so
  league xG = league goals (2026-27 factor {cal.loc[SEASON]:.3f}). Share = xGF / (xGF + xGA). Rebound = shot within 3 s of a same-team
  unblocked attempt. Close = within 20 ft. GSAx = xG against minus goals against on unblocked shots, empty net excluded.
- Data through {last_date} ({len(g26)} games). Last-{nb5} shares use each team's five most recent games.
- Goalie test (v0.2, `nhl_game_model.build_frame_g`, `scripts/tune_nhl_game_model_g.py`): starter's blended GSAx/shot x league unblocked
  shots/game as a feature; 2024-25 Brier 0.2375-0.2377 vs. 0.2375 without it; goalie coefficient
  +0.031 at shrink 1000 (wrong sign), matching v0.1 only as the shrink grows very large. Not adopted. Split-half correlation, goalies with 400+
  unblocked shots per half: {', '.join(f'{v:.2f}' for v in rep_g)}; team xGA/game: {', '.join(f'{v:.2f}' for v in rep_t)} (2023-24 to 2025-26).
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`). Team xGF/xGA per game shrunk with K={gmod.K} games toward
  league + {gmod.PRIOR_KEEP} x last season's edge; expected goals = (off + opp def - league) x league goals/xG ratio to date; goals =
  {coef[0]:.3f} + {coef[1]:.3f} x that + {coef[2]:.3f} x home (fit 2023-25); independent Poisson; regulation ties to home at {p_ot:.3f}.
  Brier: 2025-26 {bt[20252026]['brier']:.4f} (home-team rate {bt[20252026]['b_home']:.4f}, record log5 {bt[20252026]['b_rec']:.4f}, coin 0.25);
  2026-27 to date {bt[SEASON]['brier']:.4f} ({bt[SEASON]['b_home']:.4f}, {bt[SEASON]['b_rec']:.4f}). Settings chosen on 2024-25 only
  (`scripts/tune_nhl_game_model.py`). Goalies not in the model. The xG model's final fit includes 2025-26; with xG fit on 2023-25 only,
  QA re-ran the 2025-26 test: Brier 0.2444, buckets 52/48, 57/55, 62/61, 68/70, today's Sabres chance 46.1% vs. {p_b:.1%} published.
"""
    (OUT / "2026-11-08-sabres-vgk-pregame.md").write_text(md)
    (OUT / "2026-11-08-sabres-vgk-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres vs. Vegas, 3:30 p.m.: the matchup",
        "big": [[f"{1 - p_b:.0%}", "Vegas's chance to win, our model (Sabres " + f"{p_b:.0%})"],
                [f"{b.reb_f_pg:.1f}", f"Sabres rebound shots a game ({ordn(rb_rk_f)} of 32)"]],
        "note": (f"Close to a coin flip: our model expects {mu_v:.1f} goals for Vegas, {mu_b:.1f} for Buffalo. Rebounds go in {reb_rate:.1%} "
                 f"of the time, about {reb_rate / non_rate:.1f} times the rate of other shots."),
        "explainer": {"kicker": "How we know", "title": "Every shot has a chance of going in.",
                      "text": (f"A shot from within 10 feet went in {close10:.1%} of the time over the last three seasons; from 60 feet or more, "
                               f"{far60:.1%}. Add up those chances on every shot and you get what a team's chances were worth in goals."),
                      "fmt": "pct", "bars": [["Rebounds", round(float(reb_rate), 3)], ["Other shots", round(float(non_rate), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
