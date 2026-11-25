"""Sabres pregame: Rangers at Buffalo, Wed Nov 25, 2026, 7:00 PM ET.

The angle: the Rangers get decent chances but finish them worse than any team except two, and their goalies have bailed them out.
Over the last three seasons, finishing hasn't carried from one half of a season to the next; goaltending partly has.

Writes reports/2026-11-25-sabres-nyr-pregame.md, one PNG (sabres-nyr-nov25-finish.png) and a hero JSON.
Expected goals rescaled per season (league xG = goals); unblocked, non-empty-net shots. Win chance from nhl_game_model v0.1, the same model
and inputs src/ledger/log_sabres_nyr_nov25.py logs. Pinned to games through AS_OF (every Nov. 24 game final).
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import nhl_game_model as gmod
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED
from src.reports.sabres_postgame import finish, ordn
from src.reports.sabres_tbl_swing_nov22 import PAST, team_games

OUT = ROOT / "reports"
SLUG = "2026-11-25-sabres-nyr-pregame"
PNG = "sabres-nyr-nov25-finish.png"
SEASON, LY, US, THEM = 20262027, 20252026, "BUF", "NYR"
AS_OF = "2026-11-24"
RATINGS_BEFORE = "2026-11-25"
GAME_DATE = "2026-11-25"
NYR_BLUE = "#0038A8"
GARAND, SHESTERKIN = 8482193, 8478048
THOMPSON = 8479420


def main(as_of=AS_OF):
    s = shots()
    gm = query(f"SELECT g.* FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id WHERE c.game_type = 2 AND g.game_date <= '{as_of}'")
    sched = query(f"SELECT game_id FROM raw_nhl_schedule WHERE game_type = 2 AND season = {SEASON} AND game_date <= '{as_of}'")
    assert set(sched.game_id) <= set(gm.game_id), "re-run the NHL ingest"
    assert (gm[gm.season == SEASON].game_state.isin(["OFF", "FINAL"])).all()
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    g26 = gm[gm.season == SEASON]
    assert g26.game_date.max() == as_of

    # records
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        rows.append(g26.rename(columns={side: "team", opp: "opp", f"{side}_score": "gf", f"{opp}_score": "ga"})
                    [["game_id", "game_date", "team", "opp", "gf", "ga", "last_period_type"]].assign(home=side == "home"))
    rec = pd.concat(rows)
    ot = rec.last_period_type.isin(["OT", "SO"])
    rec["w"], rec["otl"] = rec.gf > rec.ga, (rec.gf < rec.ga) & ot

    def rstr(x):
        return f"{int(x.w.sum())}-{int((~x.w & ~x.otl).sum())}-{int(x.otl.sum())}"

    def pts(tm):
        x = rec[rec.team == tm]
        return int(2 * x.w.sum() + x.otl.sum())
    b_home = rec[(rec.team == US) & rec.home]
    n_road = rec[(rec.team == THEM) & ~rec.home]
    assert (rstr(rec[rec.team == US]), rstr(rec[rec.team == THEM]), rstr(b_home), rstr(n_road)) == ("10-10-4", "13-9-1", "4-6-0", "4-6-1")

    # team season profile (per game): chances, finishing, saves
    tg_ = team_games(g26[["game_id", "season", "game_date", "home", "away", "home_score", "away_score", "last_period_type"]], cur)
    tm = tg_.groupby("team").agg(gp=("game_id", "size"), xgf=("xgf", "sum"), xga=("xga", "sum"), ngf=("ngf", "sum"), nga=("nga", "sum"))
    tm["share"] = tm.xgf / (tm.xgf + tm.xga)
    tm["fin"] = (tm.ngf - tm.xgf) / tm.gp
    tm["sv"] = (tm.xga - tm.nga) / tm.gp
    tm["fin_tot"], tm["sv_tot"] = tm.ngf - tm.xgf, tm.xga - tm.nga
    for c_ in ("share", "fin", "sv"):
        tm[f"{c_}_rk"] = tm[c_].rank(ascending=False, method="min").astype(int)
    b, n = tm.loc[US], tm.loc[THEM]
    assert (int(n.fin_rk), int(n.sv_rk), int(n.share_rk), int(b.share_rk)) == (30, 6, 9, 22)
    n_fin_bottom = int((tm.fin < n.fin).sum())

    # what carries over: first 41 vs last 41 games, 2023-24 to 2025-26 (same method as the Nov. 22 recap)
    keep_all = gm[["game_id", "season", "game_date", "home", "away", "home_score", "away_score", "last_period_type"]]
    ta = team_games(keep_all, u)
    ta["fin"], ta["sv"] = ta.ngf - ta.xgf, ta.xga - ta.nga
    r = []
    for (se, tm_), d in ta[ta.season.isin(PAST)].sort_values(["game_date", "game_id"]).groupby(["season", "team"]):
        d = d.reset_index(drop=True)
        h = len(d) // 2
        o, e = d.iloc[:h], d.iloc[h:]
        r.append(dict(fin_o=o.fin.sum(), fin_e=e.fin.sum(), sv_o=o.sv.sum(), sv_e=e.sv.sum(), n=len(d)))
    r = pd.DataFrame(r)
    assert len(r) == 96 and (r.n == 82).all()
    botf = r[r.fin_o <= r.fin_o.quantile(0.25)]
    topsv = r[r.sv_o >= r.sv_o.quantile(0.75)]
    bot_fin_o, bot_fin_e = float(botf.fin_o.mean()), float(botf.fin_e.mean())
    top_sv_o, top_sv_e = float(topsv.sv_o.mean()), float(topsv.sv_e.mean())
    assert bot_fin_o < -10 and abs(bot_fin_e) < abs(bot_fin_o) / 2 and top_sv_e > 0

    # how a chance gets its value: this season's shots
    sh10, sh40 = cur[cur.dist < 10], cur[cur.dist >= 40]
    p10, p40 = float(sh10.goal.mean()), float(sh40.goal.mean())
    assert round(p10, 3) == 0.135 and round(p40, 3) == 0.022
    net = float(n.fin_tot + n.sv_tot)
    keep_fin, keep_sv = bot_fin_e / bot_fin_o, top_sv_e / top_sv_o
    assert abs(net) < 2 and keep_fin < keep_sv

    # goalies
    gk = cur[cur.goalie_id.notna()].groupby(["opp", "goalie_id"]).agg(gp=("game_id", "nunique"), sog=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["gsax"], gk["name"], gk["sv"] = gk.xga - gk.ga, gk.goalie_id.map(names), 1 - gk.ga / gk.sog
    tot = gk.groupby("goalie_id").gsax.sum()
    gk["rk"] = gk.goalie_id.map(tot.rank(ascending=False, method="min").astype(int))
    n_gk = len(tot)
    ng = gk[gk.opp == THEM].sort_values("gp", ascending=False)
    bg = gk[gk.opp == US].sort_values("gp", ascending=False)
    gar, shes = ng[ng.goalie_id == GARAND].iloc[0], ng[ng.goalie_id == SHESTERKIN].iloc[0]
    assert (int(gar.gp), int(shes.gp)) == (16, 5)
    starts = cur.groupby(["game_id", "opp", "goalie_id"]).size().reset_index().sort_values(0, ascending=False).groupby(["game_id", "opp"]).head(1)

    # scorers
    gl_ty = s[(s.goal == 1) & (s.season == SEASON)]
    sc = gl_ty.groupby(["team", "shooter_id"]).size()
    tom_g = int(sc.loc[(US, THOMPSON)])
    league_g = gl_ty.groupby("shooter_id").size()
    tom_rk = int(league_g.rank(ascending=False, method="min")[THOMPSON])
    nyr_top = sc.loc[THEM].sort_values(ascending=False)
    en = gl_ty[gl_ty.empty_net_against == 1].groupby("shooter_id").size()
    tom_en = int(en.get(THOMPSON, 0))
    n1, n1_g = names[nyr_top.index[0]], int(nyr_top.iloc[0])
    n1_en = int(en.get(nyr_top.index[0], 0))
    nyx = cur[cur.team == THEM].groupby("shooter_id").agg(g=("goal", "sum"), x=("xg", "sum"))
    nyx["gap"] = nyx.g - nyx.x
    cold = nyx.sort_values("gap").iloc[0]
    cold_id = nyx.sort_values("gap").index[0]
    cold_name = names[cold_id]

    # rest and meetings
    last_b = rec[rec.team == US].game_date.max()
    last_n = rec[rec.team == THEM].game_date.max()
    rest_b = (pd.Timestamp(GAME_DATE) - pd.Timestamp(last_b)).days - 1
    rest_n = (pd.Timestamp(GAME_DATE) - pd.Timestamp(last_n)).days - 1
    assert (rest_b, rest_n) == (2, 2)
    ly = gm[(gm.season == LY) & (((gm.home == US) & (gm.away == THEM)) | ((gm.home == THEM) & (gm.away == US)))]
    ly_w = int(sum((x.home_score > x.away_score) == (x.home == US) for x in ly.itertuples()))
    assert (ly_w, len(ly)) == (2, 3)
    sch = query(f"SELECT game_date, start_utc, home, away FROM raw_nhl_schedule WHERE season = {SEASON} AND game_type = 2 AND game_date = '{GAME_DATE}' AND home = '{US}'").iloc[0]
    assert (sch.away, sch.start_utc) == (THEM, "2026-11-26T00:00:00Z")

    # ---- prediction
    tg, coef, p_ot, home_rate = gmod.train()
    off_r, def_r, lg_r, ratio = gmod.ratings(tg, SEASON, RATINGS_BEFORE)
    mu_b = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, US, THEM), 1)
    mu_n = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, THEM, US), 0)
    p_b, p_tie = gmod.win_prob(mu_b, mu_n, p_ot)
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.game_id == "NHL_20262027_2026-11-25_NYR_at_BUF"] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace('T', ' ').rstrip('Z')} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- chart: every team, finishing vs. saves, per game
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    oth = tm.drop([US, THEM])
    ax.scatter(oth.fin, oth.sv, s=36, color=GRAY, alpha=0.7, lw=0, zorder=2)
    for tm_, col_, lab in ((US, BLUE, "Sabres"), (THEM, NYR_BLUE, "Rangers")):
        x_, y_ = tm.loc[tm_, "fin"], tm.loc[tm_, "sv"]
        ax.scatter([x_], [y_], s=110, color=col_ if tm_ == US else "white", edgecolor=col_, lw=2.2, zorder=4)
        ax.annotate(lab, (x_, y_), xytext=(8, 8), textcoords="offset points", fontsize=11, fontweight="bold", color=col_)
    ax.axhline(0, color="#D5D8DE", lw=1); ax.axvline(0, color="#D5D8DE", lw=1)
    lim = max(tm.fin.abs().max(), tm.sv.abs().max()) * 1.15
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.text(lim * 0.97, -lim * 0.95, "Finish well,\nweak goaltending", ha="right", va="bottom", fontsize=8.5, color=MUTED)
    ax.text(-lim * 0.97, lim * 0.95, "Don't finish,\ngoalies bail them out", ha="left", va="top", fontsize=8.5, color=MUTED)
    ax.text(lim * 0.97, lim * 0.95, "Finish well,\ngoalies stop more", ha="right", va="top", fontsize=8.5, color=MUTED)
    ax.text(-lim * 0.97, -lim * 0.95, "Don't finish,\nweak goaltending", ha="left", va="bottom", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Finishing: goals scored above what the team's chances were worth, per game")
    ax.set_ylabel("Goaltending: goals saved vs. an average goalie, per game")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "The Rangers don't finish their chances. Their goalies make up for it",
           f"Every NHL team, 2026-27 regular season through {pd.Timestamp(as_of):%b. %-d}. Per game, empty-net goals left out.",
           "x")
    fig.texts[-1].set_text(f"Source: NHL play-by-play, Buffalo Quant Desk chances model. {len(tm)} teams, {len(g26)} games.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if x.opp == US else 'Rangers'} | {link(x['name'])} | {int(x.gp)} | {x.sv:.1%} | {('0.0, about average,' if abs(x.gsax) < 0.05 else f'{x.gsax:+.1f}')} ({ordn(x.rk)} of {n_gk}) |"
                        for _, x in pd.concat([bg[bg.gp >= 3], ng[ng.gp >= 3]]).iterrows())

    md = f"""# Sabres vs. Rangers: New York can't finish its chances, and that probably won't last

**The Rangers get {n.share:.0%} of the chances in their games, {ordn(n.share_rk)} in the NHL. Buffalo gets {b.share:.0%}, {ordn(b.share_rk)}. What the Rangers don't do is finish:
they've scored about {abs(n.fin_tot):.0f} fewer goals than their chances were worth, {ordn(n.fin_rk)} of 32. Their goalies have made up for it, saving about {n.sv_tot:.0f} more than an
average goalie would ({ordn(n.sv_rk)} per game). Over the last three seasons, bad finishing hasn't lasted, so the Rangers should score more than they have. Their goaltending will probably cool off some too.
Our model gives the Sabres {p_b:.0%} tonight.**

*Rangers at Sabres, Wednesday, Nov. 25, 7 p.m. ET. Sabres {rstr(rec[rec.team == US])} ({pts(US)} points), Rangers {rstr(rec[rec.team == THEM])} ({pts(THEM)} points), through Nov. {pd.Timestamp(as_of).day}.*

![The Rangers don't finish their chances. Their goalies make up for it]({PNG})

## The Rangers' two-sided season

**Finishing.** Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays.
This season, a shot from within 10 feet has gone in about {p10:.0%} of the time; one from 40 feet or more, about {p40:.0%}. Add those up and you get
what a team's chances were worth. The Rangers' chances have been worth about {n.ngf + abs(n.fin_tot):.0f} goals this season; they've scored {int(n.ngf)} (not counting empty nets).
Only {n_fin_bottom} {'team has' if n_fin_bottom == 1 else 'teams have'} finished worse. {cold_name} has the biggest gap on the team: {int(cold.g)} goals on chances worth about {cold.x:.0f}.

**Goaltending.** Dylan Garand has played in {int(gar.gp)} of their {int(n.gp)} games, Igor Shesterkin in {int(shes.gp)}. Both have been better than average.

## Why that matters: what lasts

In Sunday's [Tampa Bay recap](sabres-lightning-postgame-nov-22.html), we split every NHL team's season from the last three years ({len(r)} team-seasons) into its first 41 games
and its last 41. Finishing didn't carry over; goaltending partly did. The same split, for the teams in the Rangers' spot:

- **Teams in the bottom quarter for finishing** in the first half were about {abs(bot_fin_o):.0f} goals below average. In the second half, about {abs(bot_fin_e):.0f} {'below' if bot_fin_e < 0 else 'above'}.
- **Teams in the top quarter for saves** in the first half were about {top_sv_o:.0f} goals better than average. In the second half, still {top_sv_e:.0f} better.

If the Rangers follow that pattern, their shooting comes around and their goaltending stays good, just not this good. Right now the two nearly cancel out: about
{abs(n.fin_tot):.0f} goals missed, about {n.sv_tot:.0f} saved. Finishing is what tends to bounce back, so the bigger change from here is more Rangers goals. It won't necessarily show up in one game. Buffalo, for its part, finishes and saves at about an average rate ({ordn(b.fin_rk)} and {ordn(b.sv_rk)}).

## Who to watch

- **Tage Thompson** has {tom_g} goals, {ordn(tom_rk)} in the NHL.
- **{n1}** leads the Rangers with {n1_g} goals.
- **Buffalo at home:** the Sabres are {rstr(b_home)} in Buffalo this season. The Rangers are {rstr(n_road)} on the road.
- **Rest:** both teams last played Sunday.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good. Goalies with three or more games.

| Team | Goalie | Games | Save % | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies this season. Starters weren't confirmed when we published.

## Our prediction: Sabres {p_b:.0%}, Rangers {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_n:.1f} for New York**, with about a {p_tie:.0%} chance the game is tied after 60 minutes. It works from each team's chances
this season, blended with last season's, plus home ice. It rates the Rangers a little ahead, even on the road, because they've gotten more of the chances. It doesn't count finishing or goaltending, so it already treats the Rangers as average shooters with average goalies.
Last season Buffalo won {ly_w} of the {len(ly)} games between them.

## For the stat-heads

- xG: our model on unblocked, non-empty-net shots, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). Data through {as_of} ({len(g26)} games).
- Goalie games are appearances, including relief. Player goal totals are official, including empty-net goals ({n1} {n1_en} of {n1_g}, Thompson {tom_en} of {tom_g}).
- Net NYR finishing + saves {net:+.1f}. Share kept in the second half: worst-finishing quarter {keep_fin:.0%}, best-goaltending quarter {keep_sv:.0%}. NYR saves rank by season total: {int(tm.sv_tot.rank(ascending=False, method='min')[THEM])}.
- NYR: xG share {n.share:.3f} ({int(n.share_rk)}); G - xG {n.fin_tot:+.1f} ({n.fin:+.2f}/gp, {int(n.fin_rk)}); xGA - GA {n.sv_tot:+.1f} ({n.sv:+.2f}/gp, {int(n.sv_rk)}).
  BUF: share {b.share:.3f} ({int(b.share_rk)}); G - xG {b.fin_tot:+.1f} ({int(b.fin_rk)}); xGA - GA {b.sv_tot:+.1f} ({int(b.sv_rk)}).
- Split-half (games 1-41 vs 42-82), 2023-24 to 2025-26, {len(r)} team-seasons: bottom-quartile first-half finishing {bot_fin_o:+.1f} -> {bot_fin_e:+.1f} (n {len(botf)});
  top-quartile first-half saves {top_sv_o:+.1f} -> {top_sv_e:+.1f} (n {len(topsv)}).
- Win chance: NHL game model {gmod.VERSION}, ratings from games through {as_of}. Goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home; independent Poisson;
  regulation ties to home at {p_ot:.3f}. No goalie, finishing or rest term.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Rangers at Sabres, Wednesday 7 p.m.",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Rangers {1 - p_b:.0%})"],
                [f"{ordn(n.fin_rk)}", "the Rangers' rank in finishing their chances, out of 32 teams"]],
        "note": f"New York's goalies have covered for its shooting. Over the last three seasons, bad finishing hasn't lasted.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
