"""Bills-Chiefs series, part 4 (Nov. 25, 2026): rain and wind on Thursday night, and what bad weather has done to NFL offenses.

Every regular-season outdoor game, 2018 through Week 10 of 2026, sorted by the weather nflverse records for it. Compares scoring,
completions, 20-yard passes and runs in rain (and in rain with 10+ mph wind, the closest match to Thursday's forecast) with dry games.
Checked a second way against what the same offenses and defenses did in that season's dry outdoor games, and a third way with a
regression. Then Josh Allen in the rain, the last Chiefs-Bills rain game, and where Buffalo's 2026 defense stands.

Writes reports/2026-wk12-kc-weather.md, one PNG (bills-kc-wk12-weather.png) and a hero JSON.

Sources and pins:
- Plays: nflverse play-by-play (re-posted Nov. 25, 2026; 2026 fingerprint asserted); pass and run plays, EPA not null, no two-point
  tries, kneels, spikes or no-plays; regular season; 2018-2025 full seasons, 2026 weeks 1-10 (same window as part 3).
- Weather: nflverse `weather` text and `wind` (mph) per game. Wind fills from the text when the column is empty.
- Forecast: National Weather Service, captured 2026-11-25 11:57 UTC, reports/weather/2026-11-26-orchard-park-nws-2026-11-25T1157Z.json.
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED
from src.reports.wk11_postgame import finish, ordn as _ordn

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-weather"
PNG = "bills-kc-wk12-weather.png"
FORECAST = OUT / "weather" / "2026-11-26-orchard-park-nws-2026-11-25T1157Z.json"
ALLEN_PFR = "AlleJo02"
WK26 = 10
PBP26_FINGERPRINT = (25946, -222.5969)          # same pin as part 3
LIGHT = "#8FA6CF"
PLAYS = """p.season_type = 'REG' AND (p.pass = 1 OR p.rush = 1) AND p.epa IS NOT NULL AND p.play_type <> 'no_play'
           AND COALESCE(p.two_point_attempt, 0) = 0 AND COALESCE(p.qb_kneel, 0) = 0 AND COALESCE(p.qb_spike, 0) = 0
           AND p.posteam IS NOT NULL AND (p.season BETWEEN 2018 AND 2025 OR (p.season = 2026 AND p.week <= {wk}))"""
UNSURE = r"possible|chance|change of|forecasted|threat|scattered"


def ordn(n):
    return _ordn(int(n))


def wx_class(s):
    """Game weather from nflverse's description (the text before 'Temp:'). Forecast-style wording ('chance of rain') is 'unsure'."""
    d = (s if isinstance(s, str) else "").split("Temp:")[0].lower()
    if re.search(r"snow|flurr|flakes", d):
        return "snow"
    if re.search(r"rain|shower|drizzle", d):
        return "unsure" if re.search(UNSURE, d) else "rain"
    return "dry"


def wind_from_text(s):
    m = re.search(r"Wind:\s*[A-Za-z ]*?(\d+)\s*mph", s if isinstance(s, str) else "")
    return float(m.group(1)) if m else np.nan


def team_games():
    p = query(f"""SELECT p.game_id, p.season, p.posteam, p.defteam, MAX(p.weather) weather, MAX(p.wind) wind, MAX(p.roof) roof,
                  SUM(p.pass) db, SUM(CASE WHEN p.pass = 1 AND p.yards_gained >= 20 THEN 1 ELSE 0 END) big,
                  SUM(CASE WHEN p.pass_attempt = 1 AND p.sack = 0 THEN 1 ELSE 0 END) att, SUM(p.complete_pass) cmp, SUM(p.rush) ru
                  FROM raw_pbp p WHERE {PLAYS.format(wk=WK26)} GROUP BY 1, 2, 3, 4""")
    g = p.groupby("game_id").agg(weather=("weather", "max"), wind=("wind", "max"), roof=("roof", "max"))
    g["cls"] = g.weather.map(wx_class)
    g["wtxt"] = g.weather.map(wind_from_text)
    g["w"] = g.wind.fillna(g.wtxt)
    p = p.drop(columns=["weather", "wind", "roof"]).merge(g[["cls", "w", "roof"]], left_on="game_id", right_index=True)
    sc = query("SELECT game_id, home_team, home_score, away_score FROM raw_schedules")
    p = p.merge(sc, on="game_id")
    p["pts"] = np.where(p.posteam == p.home_team, p.home_score, p.away_score).astype(float)
    return p, g


def rates(s):
    return dict(games=int(s.game_id.nunique()), tg=len(s), pts=float(s.pts.mean()), cmp=float(s.cmp.sum() / s.att.sum()),
                big=float(s.big.sum() / s.db.sum()), ru=float(s.ru.mean()), db=float(s.db.mean()))


def expected(s, base):
    """What these offenses and defenses did in that season's dry outdoor games: offense + defense - league, per team-game."""
    out = {}
    for k, num, den in (("pts", "pts", None), ("cmp", "cmp", "att"), ("big", "big", "db"), ("ru", "ru", None)):
        if den is None:
            o, d, lg = (base.groupby(c)[num].mean() for c in (["season", "posteam"], ["season", "defteam"], "season"))
            e = np.array([o[(r.season, r.posteam)] + d[(r.season, r.defteam)] - lg[r.season] for r in s.itertuples()])
            out[k] = float(e.mean())
        else:
            o, d, lg = (base.groupby(c)[[num, den]].sum() for c in (["season", "posteam"], ["season", "defteam"], "season"))
            e = np.array([o.loc[(r.season, r.posteam), num] / o.loc[(r.season, r.posteam), den]
                          + d.loc[(r.season, r.defteam), num] / d.loc[(r.season, r.defteam), den]
                          - lg.loc[r.season, num] / lg.loc[r.season, den] for r in s.itertuples()])
            out[k] = float((e * s[den].values).sum() / s[den].sum())
    return out


def main():
    fp = query(f"SELECT COUNT(*) n, ROUND(SUM(epa), 4) s FROM raw_pbp WHERE season = 2026 AND season_type = 'REG' AND week <= {WK26} AND epa IS NOT NULL").iloc[0]
    assert (int(fp.n), float(fp.s)) == PBP26_FINGERPRINT, f"2026 play-by-play changed since publication: {tuple(fp)}"

    # ---- forecast (saved copy of the National Weather Service forecast)
    fc = json.loads(FORECAST.read_text())
    assert fc["updateTime"] == "2026-11-25T11:57:35+00:00"
    hrs = [h for h in fc["hourly"] if h[0][11:13] in ("20", "21", "22", "23")]          # 8 p.m. to 11 p.m. ET
    gust = {v[0][:13]: v[1] / 1.609344 for v in fc["windGust_kmh"]}
    rows = []
    for h in hrs:
        utc = pd.Timestamp(h[0]).tz_convert("UTC").strftime("%Y-%m-%dT%H")
        rows.append((pd.Timestamp(h[0]).strftime("%-I p.m."), h[1], int(h[2].split()[0]), h[3], round(gust[utc]), h[4], h[5]))
    rain_in = [v[1] for v in fc["qpf_mm"] if v[0].startswith("2026-11-27T00")][0] / 25.4
    t_lo, t_hi = min(r[1] for r in rows), max(r[1] for r in rows)
    w_lo, w_hi = min(r[2] for r in rows), max(r[2] for r in rows)
    g_lo, g_hi = min(r[4] for r in rows), max(r[4] for r in rows)
    assert all(r[5] == 100 for r in rows) and (t_lo, t_hi, w_lo, w_hi, g_lo, g_hi) == (36, 37, 10, 13, 23, 29) and round(rain_in, 2) == 0.35

    # ---- every outdoor game
    P, G = team_games()
    out = P[P.roof.isin(["outdoors", "open"])]
    gcls = out.groupby("game_id").cls.first().value_counts()
    dry, rain = out[out.cls == "dry"], out[out.cls == "rain"]
    rw = rain[rain.w >= 10]
    D, R, RW = rates(dry), rates(rain), rates(rw)
    ER, ERW = expected(rain, dry), expected(rw, dry)
    gw = G[G.roof.isin(["outdoors", "open"])].dropna(subset=["wind", "wtxt"])
    agree = float(((gw.wind - gw.wtxt).abs() <= 1).mean())
    dis = gw[(gw.wind - gw.wtxt).abs() > 1]
    n_both, n_dis, n_dis0 = len(gw), len(dis), int((dis.wind == 0).sum())
    assert (n_both, n_dis, n_dis0) == (1337, 194, 21)
    n_wind_missing = int(out[out.cls == "rain"].groupby("game_id").w.first().isna().sum())

    # third check: regression with offense-season and defense-season terms (dry and rain games with wind known)
    X = out[out.cls.isin(["dry", "rain"])].dropna(subset=["w"]).copy()
    X["rain"] = (X.cls == "rain").astype(float)
    dm = pd.get_dummies(X.season.astype(str) + X.posteam, prefix="o", dtype=float).join(
        pd.get_dummies(X.season.astype(str) + X.defteam, prefix="d", dtype=float))
    M = np.column_stack([X.rain, X.w, dm.values])
    b_pts = np.linalg.lstsq(M, X.pts.values, rcond=None)[0][:2]
    wt = np.sqrt(X.db.values)[:, None]
    b_big = np.linalg.lstsq(M * wt, (X.big / X.db).values * wt[:, 0], rcond=None)[0][:2]
    b_ru = np.linalg.lstsq(M, X.ru.values, rcond=None)[0][:2]
    reg_pts = float(-(b_pts[0] + 12 * b_pts[1]))       # rain plus a 12 mph wind, vs dry and calm

    assert (D["games"], R["games"], RW["games"]) == (1461, 107, 44), (D["games"], R["games"], RW["games"])
    assert 3 <= ER["pts"] - R["pts"] <= 5 and 3.5 <= ERW["pts"] - RW["pts"] <= 5.5 and -4.5 <= b_pts[0] <= -2.5
    assert R["big"] < ER["big"] and RW["big"] < ERW["big"] and b_big[0] < 0 and R["cmp"] < ER["cmp"] - 0.02
    assert R["ru"] > ER["ru"] and b_ru[0] > 0
    # dry games whose note gives no conditions at all (only temperature, humidity, wind, or nothing)
    desc = G.weather.map(lambda x: (x if isinstance(x, str) else "").split("Temp:")[0].strip())
    nodesc = set(G.index[desc == ""]) & set(dry.game_id)
    n_nodesc, n_left_out = len(nodesc), int(gcls.get("snow", 0) + gcls.get("unsure", 0))
    dry2 = dry[~dry.game_id.isin(nodesc)]
    ER2, ERW2 = expected(rain, dry2), expected(rw, dry2)
    # sensitivity: wind read from the note first, column second
    G["w2"] = G.wtxt.fillna(G.wind)
    rw2 = rain[rain.game_id.map(G.w2) >= 10]
    RW2, ERW3 = rates(rw2), expected(rw2, dry)
    assert (n_nodesc, n_left_out, RW2["games"]) == (131, 23, 47)

    # ---- what that means in a game like Thursday's: both teams' 20-yard passes
    big_drop = 2 * RW["db"] * (ERW["big"] - RW["big"])
    assert 0.4 < big_drop < 0.65
    gap, gap_w = ER["pts"] - R["pts"], ERW["pts"] - RW["pts"]
    assert round(gap * 2) / 2 == 3.5 and round(gap_w * 2) / 2 == 4.5

    # ---- Josh Allen in the rain vs dry outdoor games (15+ dropbacks), raw and same-season
    allen = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{ALLEN_PFR}'").gsis_id
    assert len(allen) == 1
    allen = allen.iloc[0]
    a = query(f"""SELECT p.game_id, p.season, COUNT(*) db, SUM(CASE WHEN p.pass_attempt = 1 AND p.sack = 0 THEN 1 ELSE 0 END) att,
                  SUM(p.complete_pass) cmp, SUM(CASE WHEN p.yards_gained >= 20 THEN 1 ELSE 0 END) big
                  FROM raw_pbp p WHERE p.pass = 1 AND COALESCE(p.passer_player_id, p.rusher_player_id) = '{allen}' AND {PLAYS.format(wk=WK26)}
                  GROUP BY 1, 2 HAVING COUNT(*) >= 15""")
    a = a.merge(G[["cls", "roof"]], left_on="game_id", right_index=True)
    a = a[a.roof.isin(["outdoors", "open"])]
    ar, ad = a[a.cls == "rain"], a[a.cls == "dry"]
    a_rc, a_dc = float(ar.cmp.sum() / ar.att.sum()), float(ad.cmp.sum() / ad.att.sum())
    ads = ad.groupby("season")[["cmp", "att"]].sum()
    a_ec = float(sum(r.att * ads.loc[r.season, "cmp"] / ads.loc[r.season, "att"] for r in ar.itertuples()) / ar.att.sum())
    n_a = len(ar)
    assert n_a == 13 and a_rc < a_ec < a_dc + 0.01, (n_a, a_rc, a_ec, a_dc)

    # ---- Mahomes: how many rain starts
    mah = query("SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = 'MahoPa00'").gsis_id.iloc[0]
    m = query(f"""SELECT p.game_id FROM raw_pbp p WHERE p.pass = 1 AND COALESCE(p.passer_player_id, p.rusher_player_id) = '{mah}'
                  AND {PLAYS.format(wk=WK26)} GROUP BY 1 HAVING COUNT(*) >= 15""").merge(G[["cls", "roof"]], left_on="game_id", right_index=True)
    n_m = int(((m.cls == "rain") & m.roof.isin(["outdoors", "open"])).sum())
    assert n_m == 2

    # ---- the last Chiefs-Bills rain game: Oct. 19, 2020, Orchard Park
    gid = "2020_06_KC_BUF"
    assert G.loc[gid, "cls"] == "rain"
    s20 = query(f"SELECT gameday, home_score, away_score FROM raw_schedules WHERE game_id = '{gid}'").iloc[0]
    k20 = query(f"SELECT COUNT(*) n, SUM(rushing_yards) y FROM raw_pbp WHERE game_id = '{gid}' AND posteam = 'KC' AND rush_attempt = 1").iloc[0]
    kc_runs, kc_ryds = int(k20.n), int(k20.y)
    assert (s20.gameday, int(s20.away_score), int(s20.home_score), kc_runs, kc_ryds) == ("2020-10-19", 26, 17, 46, 245)
    kcbuf = [x for x in G.index if re.search(r"_(KC_BUF|BUF_KC)$", x) and x > gid and x in G.index and G.loc[x, "cls"] == "rain"]
    assert kcbuf == [], kcbuf

    # ---- Buffalo's 2026 defense and Kansas City's run game (same measures as part 3)
    q = query(f"""SELECT p.posteam, p.defteam, p.pass AS ps, p.rush AS ru, p.qb_scramble, p.yards_gained, p.success
                  FROM raw_pbp p WHERE p.season = 2026 AND {PLAYS.format(wk=WK26)}""")
    dbs, runs = q[q.ps == 1], q[(q.ru == 1) & (q.qb_scramble.fillna(0) == 0)]
    big_rk = int(dbs.groupby("defteam").yards_gained.apply(lambda x: (x >= 20).mean()).rank(method="min")["BUF"])
    run_rk = int(runs.groupby("defteam").success.mean().rank(method="min")["BUF"])
    kc_rk = int(runs.groupby("posteam").success.mean().rank(ascending=False, method="min")["KC"])
    assert (big_rk, run_rk, kc_rk) == (20, 27, 5)

    # ---- chart: four panels, dry vs rain vs rain + wind, with the "usual" marker
    panels = [("Points per team", "pts", "{:.1f}", 1), ("Passes completed", "cmp", "{:.0%}", 100),
              ("20-yard passes per 100 dropbacks", "big", "{:.1f}", 100), ("Runs per team", "ru", "{:.1f}", 1)]
    labels = [f"Dry\n({D['games']:,} games)", f"Rain\n({R['games']})", f"Rain, wind\n10+ mph ({RW['games']})"]
    fig, axes = plt.subplots(1, 4, figsize=(13, 5.0), dpi=200)
    for ax, (ttl, k, fmt, sc) in zip(axes, panels):
        vals = [D[k] * sc, R[k] * sc, RW[k] * sc]
        ax.bar([0, 1, 2], vals, 0.62, color=[GRAY, LIGHT, BLUE], zorder=2)
        exp = [ER[k] * sc, ERW[k] * sc]
        ax.scatter([1, 2], exp, marker="D", s=46, facecolor="white", edgecolor=INK, linewidth=1.4, zorder=3)
        ax.set_ylim(0, max(vals + exp) * 1.12)
        for i, v in enumerate(vals):
            txt = f"{v:.0f}%" if k == "cmp" else fmt.format(v)
            ax.text(i, v * 0.5, txt, ha="center", va="center", fontsize=10.5, fontweight="bold", color="white" if i else INK, zorder=4)
        ax.set_xticks([0, 1, 2], labels, fontsize=8.6)
        ax.set_title(ttl, fontsize=11, color=INK, loc="left")
        ax.tick_params(axis="x", length=0)
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.subplots_adjust(bottom=0.2, top=0.74, wspace=0.28)
    finish(fig, "Rain has cost NFL teams 3 to 4 points each, and they run more",
           f"Every regular-season outdoor game, 2018 through Week {WK26} of 2026, by the weather recorded for it. Bars: what happened. Diamonds: what those same teams usually did in dry games.",
           "x")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play and game weather; National Weather Service forecast (Nov. 25). "
                           f"Thursday's forecast: light rain, {w_lo}-{w_hi} mph wind, gusts to {g_hi} mph.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    # ---- story
    tbl = "\n".join(f"| {r[0]} | {r[1]}° | {r[3]} {r[2]} mph | {r[4]} mph | {r[5]}%, {r[6].lower()} |" for r in rows)
    md = f"""# Rain and wind Thursday night. Rain has cost NFL teams 3 to 4 points each, and it brings on the run

**The forecast for Thursday night in Orchard Park is light rain the whole game, with a {w_lo} to {w_hi} mph wind and gusts up to {g_hi} mph. In {R['games']} rainy NFL games
since 2018, each team scored {R['pts']:.1f} points, about 3½ fewer than the same teams usually scored against the same opponents in dry weather.
They completed fewer passes, hit fewer long ones, and ran more. For Buffalo that cuts both ways. Rain means a few fewer long passes to defend, but more runs,
and Buffalo ranks {ordn(run_rk)} against the run.**

*Part 4 of our Bills-Chiefs series. [Part 1: Rousseau and the pass rush](bills-chiefs-leonhard-file.html). [Part 2: who's left](bills-chiefs-whos-left.html).
[Part 3: slowing Mahomes](bills-chiefs-slowing-mahomes.html).*

*A "dropback" is any pass play: completions, incompletions, sacks and scrambles.*

![Rain has cost NFL teams 3 to 4 points each]({PNG})

## The forecast

From the National Weather Service, as of Wednesday morning, for the hours of the game:

| Time (ET) | Temp | Wind | Gusts | Rain |
|---|---|---|---|---|
{tbl}

That's about {rain_in:.2f} of an inch of rain from 7 p.m. to 1 a.m. It's not a snow game, and the wind eases as the night goes on. Forecasts this far out can change.

## What rain does to an offense

We sorted every regular-season outdoor game since 2018 by the weather note recorded for it: {gcls['dry']:,} dry, {gcls['rain']} with rain, and {n_left_out} with
snow or only a chance of rain (left out). In {n_nodesc} of the dry games the note doesn't describe conditions at all, so we counted them as dry. Then we compared them. In the rain:

- **Each team scored {R['pts']:.1f} points a game.** In dry games: {D['pts']:.1f}.
- **They completed {R['cmp']:.0%} of their passes**, against {D['cmp']:.0%}.
- **{R['big'] * 100:.1f} of every 100 dropbacks went for 20 yards or more**, against {D['big'] * 100:.1f}.
- **They ran {R['ru']:.1f} times a game**, against {D['ru']:.1f}.

Thursday looks most like the {RW['games']} games with rain and a wind of 10 mph or more. In those, teams scored {RW['pts']:.1f} points a game, completed
{RW['cmp']:.0%} of their passes and ran {RW['ru']:.1f} times. For two teams dropping back about {RW['db']:.0f} times each, that's roughly one fewer 20-yard pass
every other game. Long passes get harder, but they don't go away.

**How we checked it.** Rainy games could just involve worse teams. So for each rainy game we worked out what that offense usually did in dry outdoor games that
season, and what that defense usually allowed, and compared. The answer held: in the rain, teams scored {R['pts']:.1f} points when we'd expect {ER['pts']:.1f}. In rain with wind,
{RW['pts']:.1f} when we'd expect {ERW['pts']:.1f}. A third check, one calculation with every team's season built in, put rain at {-b_pts[0]:.1f} fewer
points a team, and about {-b_pts[1] * 10:.1f} more for every 10 mph of wind.

## Buffalo's two weak spots

In part 3, Buffalo's defense ranked {ordn(big_rk)} at stopping big pass plays and {ordn(run_rk)} against the run. Rain helps a little with the first and leans on the second.
Kansas City's running game ranks {ordn(kc_rk)} this season.

The last time these teams played in the rain in Orchard Park, on Oct. 19, 2020, Kansas City ran the ball {kc_runs} times for {kc_ryds} yards and won
{int(s20.away_score)}-{int(s20.home_score)}.

## The quarterbacks

Josh Allen has played {n_a} outdoor games in the rain. He completed {a_rc:.0%} of his passes, against {a_dc:.0%} in dry outdoor games. Measured against his dry
games in the same seasons, so his rookie year doesn't skew it, we'd expect {a_ec:.0%}. Thirteen games is a small sample.

Patrick Mahomes has started only two rainy games in that time. That's too few to say anything about him.

## What it means Thursday

In past games like this one, teams scored less than usual, ran more and hit a few fewer long passes.

That matters for the recipe in [part 3](bills-chiefs-slowing-mahomes.html). Defenses that slowed Mahomes tended to do three things: get pressure, take away big
passes and stop the run. Pressure doesn't depend on the weather. The other two do. Rain has meant slightly fewer big plays, which helps a little
where Buffalo ranks {ordn(big_rk)}. It has also meant more runs, which puts more weight on a run defense that ranks {ordn(run_rk)}.

## For the stat-heads

- Games: regular season, `roof` outdoors or open, 2018 to 2026 Week {WK26}. Team-game rows: pass + run plays, EPA not null, no two-point tries, kneels, spikes or no-plays.
- Weather class from the nflverse `weather` description (text before "Temp:"): rain/shower/drizzle = rain unless worded as a forecast
  ("possible", "chance", "change of", "threat", "scattered", "forecasted"); snow/flurries = snow. Games: dry {gcls['dry']:,}, rain {gcls['rain']}, snow {gcls['snow']}, unsure {gcls['unsure']}.
  This is a pregame or game-time note, not a measured rain total. {n_nodesc} dry games have no conditions text (temperature/humidity/wind only, or no note);
  dropping them from the dry baseline: rain {R['pts']:.1f} vs {ER2['pts']:.1f} expected; rain + wind 10+ {RW['pts']:.1f} vs {ERW2['pts']:.1f}.
- Wind: nflverse `wind` (mph), filled from the description's "Wind: N mph" when empty. Where both exist they agree within 1 mph {agree:.0%} of the time.
  Rain games with no wind reading after the fill: {n_wind_missing}. Of {n_both:,} games with both, {n_dis} disagree by more than 1 mph, and in {n_dis0} of those
  the column reads 0 when the note gives a real wind. Reading the note first
  makes the rain + wind 10+ group {RW2['games']} games, {RW2['pts']:.1f} vs {ERW3['pts']:.1f} expected.
- Rates: completions = `complete_pass` / (`pass_attempt` minus sacks); 20+ rate = dropbacks (`pass` = 1, incl. sacks and scrambles) with `yards_gained` >= 20;
  runs = `rush` = 1 per team-game. nflverse codes QB scrambles as `pass` = 1, so runs are designed runs (including QB keepers and sneaks).
- Expected values: offense's season rate in dry outdoor games + defense's season rate allowed in dry outdoor games - league dry outdoor rate, per team-game.
  Rain: pts {ER['pts']:.2f}, cmp {ER['cmp']:.3f}, 20+ {ER['big']:.4f}, runs {ER['ru']:.2f}. Rain + wind 10+: {ERW['pts']:.2f}, {ERW['cmp']:.3f}, {ERW['big']:.4f}, {ERW['ru']:.2f}.
- OLS with offense-season and defense-season fixed effects, dry + rain games with wind known: points rain {b_pts[0]:+.2f}, per mph {b_pts[1]:+.3f};
  20+ rate rain {b_big[0]:+.4f}, per mph {b_big[1]:+.5f} (weighted by dropbacks); runs rain {b_ru[0]:+.2f}, per mph {b_ru[1]:+.3f}. Thursday-like (rain + 12 mph) vs dry and calm: {reg_pts:.1f} points.
- Allen: games with 15+ dropbacks as passer or scrambler (gsis from PFR id {ALLEN_PFR}). Rain n = {n_a}; completion {a_rc:.3f}; dry outdoor {a_dc:.3f}; same-season expectation {a_ec:.3f}.
- 2020 game: `{gid}`, KC `rush_attempt` = 1 (box-score carries, incl. kneels) {kc_runs} for {kc_ryds} yards.
- BUF 2026 defense ranks (weeks 1-{WK26}): 20+ dropback rate allowed {ordn(big_rk)}, designed-run success allowed {ordn(run_rk)}; KC designed-run success {ordn(kc_rk)}.
- Forecast: NWS gridpoint BUF/39,42, updated {fc['updateTime']}; hourly temps and sustained wind from the hourly forecast, gusts from grid data (km/h converted),
  rain from the 00-06 UTC quantitative precipitation (7 p.m.-1 a.m. ET). Copy saved in `reports/weather/`.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Rain and wind Thursday",
        "big": [[round(RW["pts"], 1), f"points a team in {RW['games']} NFL games with rain and 10+ mph wind since 2018"],
                [round(ERW["pts"], 1), "what those same teams usually scored in dry games"]],
        "note": f"Forecast: light rain all game, {w_lo}-{w_hi} mph wind. Rain has meant a few fewer long passes and more runs. Buffalo is {ordn(run_rk)} against the run.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
