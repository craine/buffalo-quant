"""Week 11 post-game: Dolphins at Bills (Nov. 22, 2026). Bills 26, Dolphins 9.

Writes reports/2026-wk11-postgame.md, two PNGs (wk11d-*) and a hero JSON. Every number is computed here from raw_pbp /
raw_schedules (nflverse). Completion chance per throw is nflverse's `cp` (its completion-probability model). Pinned: games
through 2026 week 11 that were in the play-by-play when this ran (Sunday late, Sunday night and Monday games left out of league context).
Ledger P0021 graded by src/ledger/grade_wk11.py. Pregame projection reproduced with src/ledger/log_bills_wk11.py's inputs.
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger.ledger import GRADE_COLS, GRADE_CSV, PRED_COLS, PRED_CSV, _read
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, WEEK = 2026, 11
GAME = "2026_11_MIA_BUF"
SLUG = "2026-wk11-postgame"
ALLEN = "00-0034857"
NOT_FINAL = ("2026_11_NYJ_LAC", "2026_11_JAX_NYG", "2026_11_LV_DEN", "2026_11_MIN_SF", "2026_11_CIN_WAS")  # not in play-by-play when this ran
SRC = "Source: nflverse play-by-play and schedules (completion chance: nflverse model). Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def clock(qtr, sec_left_in_game):
    t = int(sec_left_in_game) - (4 - int(qtr)) * 900
    return f"{t // 60}:{t % 60:02d}"


def main():
    s = query(f"SELECT home_team, home_score, away_team, away_score FROM raw_schedules WHERE game_id='{GAME}'").iloc[0]
    assert s.home_team == "BUF" and s.away_team == "MIA"
    buf, mia = int(s.home_score), int(s.away_score)
    assert (buf, mia) == (26, 9)

    # pregame projection: the values logged with P0021 (the Nov. 19 story's numbers), not a re-run
    lp0 = _read(PRED_CSV, PRED_COLS)
    note = lp0[lp0.id == "P0021"].notes.iloc[0]
    pb, pmi = (float(x) for x in re.search(r"projections BUF ([\d.]+), MIA ([\d.]+)", note).groups())
    p_win = float(lp0[lp0.id == "P0021"].probability.iloc[0])
    assert (pb, pmi, p_win) == (30.3, 19.5, 0.81)

    # ---- plays
    p = query(f"""SELECT game_id, week, play_id, qtr, game_seconds_remaining AS gsr, down, ydstogo, posteam, pass_attempt, sack, complete_pass,
                  interception, air_yards, cp, epa, success, passer_player_id, receiver_player_name, rush, pass, qb_kneel, qb_spike,
                  two_point_attempt, touchdown, field_goal_result, field_goal_attempt, kick_distance, yardline_100, drive, score_differential, wp, play_type, desc
                  FROM raw_pbp WHERE season={SEASON} AND season_type='REG' AND week<={WEEK}""")
    p = p[~p.game_id.isin(NOT_FINAL)]
    assert set(p[p.week == WEEK].game_id) == {"2026_11_IND_HOU", "2026_11_MIA_BUF", "2026_11_BAL_CAR", "2026_11_NO_CHI", "2026_11_TEN_DAL", "2026_11_TB_DET", "2026_11_ARI_KC", "2026_11_PIT_PHI"}
    g = p[p.game_id == GAME]
    thr = p[(p.pass_attempt == 1) & (p.sack == 0) & p.air_yards.notna()]
    al_all = thr[thr.passer_player_id == ALLEN]
    a = al_all[al_all.game_id == GAME].copy()
    rest = al_all[al_all.game_id != GAME]
    att_all = g[(g.posteam == "BUF") & (g.pass_attempt == 1) & (g.sack == 0) & (g.passer_player_id == ALLEN)]
    n_att, n_cmp, n_int = len(att_all), int(att_all.complete_pass.sum()), int(att_all.interception.sum())
    yds = int(query(f"SELECT SUM(passing_yards) FROM raw_pbp WHERE game_id='{GAME}' AND passer_player_id='{ALLEN}'").iloc[0, 0])
    n_td = int(g[(g.passer_player_id == ALLEN) & (g.touchdown == 1) & (g.pass_attempt == 1)].shape[0])
    assert (n_att, n_cmp, n_int, yds, n_td) == (45, 27, 2, 304, 1)
    no_target = n_att - len(a)                     # throws with no air-yards value
    no_tgt = int(a.cp.isna().sum())                # thrown away, no listed target
    assert no_target == 0 and no_tgt == 2
    a["deep"] = a.air_yards >= 20
    a["short"] = a.air_yards < 10
    q1 = a[a.qtr == 1]
    later = a[a.qtr > 1]
    deep_n, deep_c = int(a.deep.sum()), int(a[a.deep].complete_pass.sum())
    q1_n, q1_deep = len(q1), int(q1.deep.sum())
    later_n, later_deep = len(later), int(later.deep.sum())
    short_g, short_rest = float(a.short.mean()), float(rest.air_yards.lt(10).mean())
    lg_short, lg_deep = float(thr.air_yards.lt(10).mean()), float(thr.air_yards.ge(20).mean())
    deep_rest = float(rest.air_yards.ge(20).mean())
    xc = a[a.cp.notna()]
    exp_c, act_c = float(xc.cp.sum()), int(xc.complete_pass.sum())
    easy = xc[(xc.complete_pass == 0) & (xc.cp >= 0.7)].sort_values("play_id")
    assert len(easy) == 5 and q1_deep == 5 and deep_n == 7 and deep_c == 2 and q1_n == 11
    gap_g = float((xc.complete_pass - xc.cp).mean())
    rx = rest[rest.cp.notna()]
    gap_rest = float((rx.complete_pass - rx.cp).mean())
    ints = a[a.interception == 1].sort_values("play_id")
    assert len(ints) == 2 and (ints.qtr == 2).all()
    int_d = [int(x) for x in ints.air_yards]
    short_c = act_c - round(exp_c)                 # completions short of an average QB (rounded)
    close = xc[(xc.wp >= 0.10) & (xc.wp <= 0.90)]
    cl_n, cl_c, cl_x = len(close), int(close.complete_pass.sum()), float(close.cp.sum())
    easy_close = int(((easy.wp >= 0.10) & (easy.wp <= 0.90)).sum())
    easy_up14 = int((easy.score_differential >= 14).sum())
    easy_2min = int(((easy.qtr == 2) & (easy.gsr - 1800 <= 120) & (easy.score_differential >= 14)).sum())
    late = easy[easy.qtr == 4].iloc[0]
    late_lead = (int(late.score_differential), int(late.wp * 1000) / 10)
    assert (cl_n, cl_c, easy_close, easy_up14, easy_2min) == (25, 18, 1, 4, 3) and late_lead[0] == 14
    targeted_short_rest = float(rest[rest.cp.notna()].air_yards.lt(10).mean())

    # his career: every regular-season game since 2018 with 15+ throws, ranked by completions minus expected
    car = query(f"""SELECT game_id, complete_pass, cp FROM raw_pbp WHERE passer_player_id='{ALLEN}' AND season_type='REG'
                    AND pass_attempt=1 AND sack=0 AND cp IS NOT NULL AND (season < 2026 OR (season = 2026 AND week <= 11))""")
    cg = car.groupby("game_id").agg(n=("cp", "size"), c=("complete_pass", "sum"), x=("cp", "sum")).query("n >= 15")
    cg["gap"] = (cg.c - cg.x) / cg.n
    car_rank, car_n = int(cg.gap.rank(method="min").loc[GAME]), len(cg)

    # ---- defense
    pl = p[((p["pass"] == 1) | (p.rush == 1)) & p.epa.notna() & (p.qb_kneel == 0) & (p.qb_spike == 0) & (p.two_point_attempt == 0) & (p.play_type != "no_play")]
    tg = pl.groupby(["game_id", "posteam"]).agg(epa=("epa", "mean"), n=("epa", "size"), sr=("success", "mean")).reset_index()
    tg["rk"] = tg.epa.rank(method="min")
    m_row = tg[(tg.game_id == GAME) & (tg.posteam == "MIA")].iloc[0]
    b_row = tg[(tg.game_id == GAME) & (tg.posteam == "BUF")].iloc[0]
    mia_td = int(g[(g.posteam == "MIA") & (g.touchdown == 1)].shape[0])
    mia_fg = int(g[(g.posteam == "MIA") & (g.field_goal_result == "made")].shape[0])
    mia_sk = int(g[(g.posteam == 'MIA')].sack.sum())
    mia_int = int(g[(g.posteam == 'MIA')].interception.sum())
    assert mia_td == 0 and mia_fg == 3 and (mia_sk, mia_int) == (2, 1)

    # ---- Bills drives: red zone
    dv = g[g.posteam == "BUF"].groupby("drive").agg(mn=("yardline_100", "min"), td=("touchdown", "max"),
                                                    fg=("field_goal_result", lambda x: int((x == "made").any())))
    rz = dv[dv.mn <= 20]
    rz_n, rz_td, rz_fg = len(rz), int(rz.td.sum()), int(rz.fg.sum())
    b_fg = int(g[(g.posteam == "BUF") & (g.field_goal_result == "made")].shape[0])
    fga = g[(g.posteam == "BUF") & (g.field_goal_attempt == 1)]
    b_fga = len(fga)
    miss = fga[fga.field_goal_result != "made"].iloc[0]
    assert (rz_n, rz_td, rz_fg, b_fg, b_fga) == (5, 2, 3, 4, 5) and int(miss.kick_distance) == 54 and int(miss.qtr) == 3

    # ---- next game
    nx = query(f"SELECT week, home_team, away_team, gameday, gametime FROM raw_schedules WHERE season={SEASON} AND (home_team='BUF' OR away_team='BUF') AND week>{WEEK} ORDER BY week LIMIT 1").iloc[0]
    assert (nx.home_team, nx.away_team, nx.gameday) == ("BUF", "KC", "2026-11-26")

    # ---- Ledger
    lp, lgr = _read(PRED_CSV, PRED_COLS), _read(GRADE_CSV, GRADE_COLS)
    mg = lp.merge(lgr, left_on="id", right_on="prediction_id")
    me = mg[mg.id == "P0021"].iloc[0]
    assert int(me.outcome) == 1
    hit = (mg.probability.astype(float) >= 0.5) == (mg.outcome.astype(int) == 1)
    nfl = mg.sport.fillna("NFL").ne("NHL")

    # ---- chart 1: every Allen throw, completion chance vs where it went
    fig, ax = plt.subplots(figsize=(9.5, 5.3), dpi=200)
    for sel, col, lab, mk in ((xc.complete_pass == 1, GRAY, "Caught", "o"), ((xc.complete_pass == 0) & (xc.interception == 0), BLUE, "Incomplete", "o"),
                              (xc.interception == 1, RED, "Intercepted", "X")):
        d = xc[sel]
        ax.scatter(d.air_yards, d.cp, s=70 if mk == "o" else 110, color=col, marker=mk, label=lab, zorder=3, edgecolor="white", lw=0.8)
    ax.axhspan(0.7, 1.0, color=BLUE, alpha=0.06, lw=0)
    ax.text(38, 0.97, "Usually caught (70%+)", ha="right", va="top", fontsize=9, color=MUTED)
    ax.axvline(20, color="#D5D8DE", lw=1, ls="--")
    ax.text(20.6, 0.08, "Deep (20+ yards)", fontsize=9, color=MUTED)
    ax.set_xlabel("How far past the line the ball was thrown (yards)")
    ax.set_ylabel("Chance this throw is caught")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylim(0, 1.0); ax.set_xlim(-12, 40)
    ax.legend(frameon=False, loc="lower left", fontsize=9.5); ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Five easy Josh Allen throws fell incomplete or were picked off",
           "Every Josh Allen pass with a target vs. Miami, Nov. 22. Blue band: throws caught 70%+ of the time.",
           f"{len(xc)} throws. Each throw's chance comes from where it went, the down and distance, and other game details.")
    fig.savefig(OUT / "wk11d-allen-throws.png"); plt.close(fig)

    # ---- chart 2: deep shots by quarter
    fig, ax = plt.subplots(figsize=(9.5, 4.3), dpi=200)
    qs = [1, 2, 3, 4]
    dn = [int(a[(a.qtr == q) & a.deep].shape[0]) for q in qs]
    sn = [int(a[(a.qtr == q) & ~a.deep].shape[0]) for q in qs]
    x = np.arange(4)
    ax.bar(x, sn, 0.6, color=GRAY, label="Shorter throws", zorder=2)
    ax.bar(x, dn, 0.6, bottom=sn, color=BLUE, label="Deep throws (20+ yards)", zorder=2)
    for i in range(4):
        ax.text(x[i], sn[i] + dn[i] + 0.3, f"{dn[i]} deep of {sn[i] + dn[i]}", ha="center", fontsize=10, color=INK)
    ax.set_xticks(x, ["1st quarter", "2nd", "3rd", "4th"]); ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Passes thrown"); ax.legend(frameon=False, loc="upper right", fontsize=9.5)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True); ax.set_ylim(0, max(np.add(sn, dn)) + 3)
    finish(fig, f"Josh Allen went deep {q1_deep} times in the first quarter vs. Miami, twice after that" if later_deep == 2 else f"Josh Allen went deep {q1_deep} times in the first quarter vs. Miami, {later_deep} after that",
           "Josh Allen's passes vs. Miami, Nov. 22, by quarter. Deep = thrown 20+ yards past the line.", f"Deep throws completed: {deep_c} of {deep_n}. Totals include {no_tgt} passes thrown away with no target.")
    fig.savefig(OUT / "wk11d-deep-by-quarter.png"); plt.close(fig)

    easy_rows = "\n".join(
        f"| {int(r.qtr)} | {clock(r.qtr, r.gsr)} | {int(r.down)} and {int(r.ydstogo)} | {r.receiver_player_name or 'no target listed'} | "
        f"{int(r.air_yards)} | {r.cp:.0%} | {'Intercepted' if r.interception == 1 else 'Incomplete'} | {('Bills up ' + str(int(r.score_differential))) if r.score_differential > 0 else 'Tied' if r.score_differential == 0 else 'Bills down ' + str(-int(r.score_differential))} |" for r in easy.itertuples())

    rec_w = query(f"SELECT COUNT(*) FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={WEEK} AND ((home_team='BUF' AND home_score>away_score) OR (away_team='BUF' AND away_score>home_score))").iloc[0, 0]
    rec_l = query(f"SELECT COUNT(*) FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={WEEK} AND ((home_team='BUF' AND home_score<away_score) OR (away_team='BUF' AND away_score<home_score))").iloc[0, 0]
    assert (rec_w, rec_l) == (9, 1)
    md = f"""# Bills 26, Dolphins 9: the defense kept Miami out of the end zone, and five easy Josh Allen throws fell incomplete

**Buffalo's defense held Miami to three field goals and no touchdowns. Josh Allen threw for {yds} yards, but five throws that usually get caught fell
incomplete or were picked off. On the same {len(xc)} throws, an average quarterback would have completed about {exp_c:.0f}. Allen completed {act_c}.
Four of those five came with Buffalo already up by 14 or more. And the Bills settled for field goals on {rz_fg} of their {rz_n} trips inside the Miami 20.**

*One game, Nov. 22, in Buffalo. The Bills are {rec_w}-{rec_l}. [Our preview](nfl-mismatches.html).*

![Every Allen throw](wk11d-allen-throws.png)

## Josh Allen: {n_cmp} of {n_att}, {yds} yards, {n_td} touchdown, {n_int} interceptions

Every throw has a chance of being caught, based on how far it went, where on the field, the down and distance, and other game details.
Add those chances up and you get how many completions an average quarterback would get on the same throws. On Sunday that was about {exp_c:.0f}. Allen got {act_c},
about {abs(short_c)} short. In his other nine games this season, he'd completed more than an average quarterback would have. Of his {car_n} regular-season games
with 15 or more throws since 2018, this ranks {ordn(car_rank)}-worst. A bad day, but not one of his worst.

While the game was still in doubt, it looked different. With the Bills' chance of winning between 10% and 90%, he completed {cl_c} of {cl_n} targeted throws,
where an average quarterback would have completed about {cl_x:.0f}.

The five throws that usually get caught but weren't:

| Quarter | Time | Down | Intended for | Yards past the line of scrimmage | Chance it's caught | Result | Score |
|---|---|---|---|---|---|---|---|
{easy_rows}

Four of the five came with Buffalo already up by 14 or more: three in the two-minute drill before halftime, and one with under three minutes left in a
23-9 game. A missed throw isn't always the quarterback's fault: some of these could be drops or tipped balls. The play-by-play doesn't say which.

![Deep throws by quarter](wk11d-deep-by-quarter.png)

**Did he pass up open short receivers?** The public data can't show who was open on each play. That takes tracking data the NFL doesn't release.
What we can see: two of every three passes ({short_g:.0%}) went less than 10 yards past the line of scrimmage, more than his {short_rest:.0%} the rest of the season
(league so far: {lg_short:.0%}). All five easy misses were short throws. The problem wasn't skipping the short guy; it was the short ball not connecting.

The deep shots came early. He threw {q1_deep} of his {q1_n} first-quarter passes 20 or more yards. After that, just twice in {later_n} passes.
{ {2: 'Two'}.get(deep_c, str(deep_c)) } of his { {7: 'seven'}.get(deep_n, str(deep_n)) } deep throws were caught. Both interceptions came in the second quarter, on throws {int_d[0]} and {int_d[1]} yards downfield.

Play-by-play charting that marks catchable balls, interception-worthy throws and which read each pass went to usually posts a day or two after the game.
When it does, we'll check these throws against it.

## The defense

Miami's offense averaged {m_row.epa:+.2f} points per play over {int(m_row.n)} plays, the {ordn(int(m_row.rk))}-worst of {len(tg)} team games this season (through Sunday's early games).
Only 1 in 4 of its plays gained enough yards to keep a drive on track. Buffalo sacked Kyle McCord twice and picked him off once, and Miami's only points came on three field goals.

"Points per play" is how much each play helped or hurt a team's chances of scoring, based on down, distance and field position, averaged over the game. Zero is average.

## Field goals instead of touchdowns

Buffalo reached the Miami 20 five times and scored two touchdowns. Tyler Bass made {b_fg} of {b_fga} field goals; he missed from {int(miss.kick_distance)} yards in the third quarter.
Buffalo's offense averaged {b_row.epa:+.2f} points per play, about average.

## Receipts: our pregame call

Before the game we logged **an {p_win:.0%} chance the Bills win** on the [Ledger](../ledger.html). They won, so the call goes down as right. It scores {float(me.brier):.3f} on our scorecard,
where 0 is perfect and a coin flip scores 0.25. Our model expected about {pb:.0f} points for Buffalo and {pmi:.0f} for Miami. Buffalo scored {buf}; Miami scored {mia}, about {('10 and a half' if abs(pmi - mia - 10.5) < 1e-9 else f'{pmi - mia:.0f}')} fewer than we expected.
We've now got {int(hit.sum())} of our {len(mg)} graded calls right, {int(hit[nfl].sum())} of {int(nfl.sum())} on Bills games.

## What's next

Kansas City in Buffalo on Thanksgiving night. We'll have a preview with logged calls before kickoff.

## For the stat-heads

- Completion chance: nflverse `cp` per pass attempt (sacks excluded). CPOE this game {gap_g * 100:+.1f} on {len(xc)} attempts with cp; 2026 before this game {gap_rest * 100:+.1f} ({len(rx)} attempts).
  Win probability 0.10-0.90 only: {cl_c} of {cl_n}, expected {cl_x:.1f}. Easy misses (cp 0.70+) inside that window: {easy_close} of {len(easy)}.
  {no_tgt} attempts had no listed target (thrown away): out of the expected-completions numbers, in the throw-depth numbers.
  Career rank: completions minus expected per attempt, regular-season games 2018 through 2026 week 11 with 15+ attempts.
- Throw depth (air yards), all {len(a)} attempts: deep = 20+, short = under 10. Game {a.deep.mean():.1%} deep, {short_g:.1%} short; Allen 2026 before {deep_rest:.1%} / {short_rest:.1%}
  (targeted only: {targeted_short_rest:.1%} short); league 2026 {lg_deep:.1%} / {lg_short:.1%}.
- Miami EPA/play {m_row.epa:+.3f}, success rate {m_row.sr:.3f} (plays: pass or rush with EPA; no kneels, spikes, two-point tries or no-plays); rank {int(m_row.rk)} of {len(tg)} 2026 team-games, lowest first.
  League context leaves out week 11 games not in the play-by-play when this ran: {', '.join(NOT_FINAL)}.
- Pregame: points model v0.1, values as logged with Ledger P0021 (data through week 10): BUF {pb:.1f}, MIA {pmi:.1f}, P(BUF) {p_win:.2f}. Brier {float(me.brier):.4f}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Josh Allen vs. Miami",
        "big": [[act_c, "Completions"], [round(exp_c), "Expected from an average QB on the same throws"]],
        "note": "Bills 26, Dolphins 9. Five Allen throws that usually get caught (70%+ of the time) fell incomplete or were picked off.",
        "explainer": {"kicker": "The defense", "title": "Miami's points per play", "text": "How much each play helped Miami, on average:", "fmt": "score",
                      "bars": [["League average", 0.0], ["Miami on Sunday", round(float(m_row.epa), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
