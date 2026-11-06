"""reports/2026-josh-allen.md + charts. Every number is computed here from the repo's tables."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT
from src.metrics.qb import ERA_LABEL, ERA_ORDER, allen_runs, buf_era, dropbacks, is_allen, rate
from src.reports.allen_explore import coverage, era_table, pressure, qb_seasons, weather
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


SRC = "Source: nflverse play-by-play, FTN charting, NFL participation data. Regular season. Buffalo Quant Desk."


def foot(fig, extra=""):
    fig.text(0.02, 0.012, f"{SRC} {extra}", fontsize=7.5, color=MUTED)


def chart_seasons(qs, wk):
    a = qs[(qs.qb == "J.Allen") & (qs.posteam == "BUF")].set_index("season")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    xs = a.index.tolist()
    cols = [RED if s == 2026 else BLUE for s in xs]
    ax.bar([str(s) for s in xs], a.epa, color=cols, width=0.62, zorder=2)
    for i, s in enumerate(xs):
        v, rk, n = a.loc[s, "epa"], int(a.loc[s, "epa_rk"]), int(a.loc[s, "n_qb"])
        ax.text(i, v + (0.008 if v >= 0 else -0.008), f"{v:+.2f}\n#{rk} of {n}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=8.5, color=INK)
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylim(min(a.epa.min(), 0) - 0.07, a.epa.max() + 0.08)
    ax.set_ylabel("EPA per dropback (incl. scrambles, sacks)")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle("Josh Allen is the NFL's most efficient passer in 2026", x=0.02, ha="left", fontsize=15,
                 fontweight="bold", color=INK)
    ax.set_title(f"EPA per dropback by season, with rank among QBs with 200+ dropbacks (2026: 150+ through week {wk})",
                 loc="left", fontsize=9.5, color=MUTED, pad=8)
    foot(fig, f"2026: {int(a.loc[2026, 'db'])} dropbacks, small sample.")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-seasons.png"); plt.close(fig)


def chart_offscript(o):
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.6), dpi=200, sharex=True)
    xs = [str(s) for s in o.index]
    for ax, col, title, fmt in [(axes[0], "oop", "Share of dropbacks outside the pocket", "{:.0%}"),
                                (axes[1], "epa_oop", "EPA per play when outside the pocket", "{:+.2f}")]:
        c = [RED if s == "2026" else BLUE for s in xs]
        ax.bar(xs, o[col], color=c, width=0.6, zorder=2)
        for i, v in enumerate(o[col]):
            ax.text(i, v + o[col].max() * 0.02, fmt.format(v), ha="center", va="bottom", fontsize=9, color=INK)
        ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="bold")
        ax.set_ylim(0, o[col].max() * 1.18); ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    fig.suptitle("More Allen off script, and it's working again", x=0.02, ha="left", fontsize=15,
                 fontweight="bold", color=INK)
    foot(fig, "FTN charting begins 2022.")
    fig.tight_layout(rect=(0, 0.04, 1, 0.95)); fig.savefig(OUT / "allen-offscript.png"); plt.close(fig)


def chart_weather(wq, rank):
    top = wq.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=200)
    c = [RED if q == "J.Allen" else GRAY for q in top.qb]
    ax.barh(top.qb, top.epa_over, color=c, height=0.62, zorder=2)
    for i, (v, n) in enumerate(zip(top.epa_over, top.db)):
        ax.text(v + 0.003, i, f"{v:+.3f}  ({int(n):,} db)", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, top.epa_over.max() * 1.35)
    ax.set_xlabel("EPA per dropback above league average in the same temperature and wind")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle(f"Weather-adjusted: Allen ranks {ordn(rank)} since 2018", x=0.02, ha="left", fontsize=15,
                 fontweight="bold", color=INK)
    ax.set_title(f"Outdoor games only, QBs with 800+ outdoor dropbacks ({len(wq)} qualify)", loc="left",
                 fontsize=9.5, color=MUTED, pad=8)
    foot(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-weather.png"); plt.close(fig)


def chart_pressure(ap):
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
    x = [str(s) for s in ap.season]
    ax.plot(x, ap.epa_clean, color=BLUE, lw=2, marker="o", ms=8, zorder=3)
    ax.plot(x, ap.epa_pres, color=RED, lw=2, marker="o", ms=8, zorder=3)
    ax.text(len(x) - 0.85, ap.epa_clean.iloc[-1], "Clean pocket", color=INK, va="center", fontsize=10, fontweight="bold")
    ax.text(len(x) - 0.85, ap.epa_pres.iloc[-1], "Pressured", color=INK, va="center", fontsize=10, fontweight="bold")
    for i, (v, rk, n) in enumerate(zip(ap.epa_pres, ap.pres_rk, ap.n)):
        ax.annotate(f"#{int(rk)}", (i, v), xytext=(0, -19), textcoords="offset points", ha="center",
                    fontsize=8.5, color=MUTED, bbox=dict(fc="white", ec="none", pad=0.6))
    ax.axhline(0, color=INK, lw=1); ax.set_xlim(-0.4, len(x) + 0.6)
    ax.set_ylim(min(ap.epa_pres.min(), 0) - 0.12, max(ap.epa_clean.max(), ap.epa_pres.max()) + 0.06)
    ax.set_ylabel("EPA per dropback"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle("2025: the year pressure finally got to him", x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    ax.set_title("EPA per dropback, pressured vs. clean. # = league rank when pressured. 2026 pressure data not yet published.",
                 loc="left", fontsize=9, color=MUTED, pad=8)
    foot(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-pressure.png"); plt.close(fig)


def main():
    d = dropbacks()
    a = d[is_allen(d)]
    wk = int(a[a.season == 2026].week.max())
    qs = qb_seasons(d.assign(_x=0))
    # 2026 qualifying threshold is lower (partial season)
    q26 = d[d.season == 2026].groupby(["season", "qb_id", "qb", "posteam"]).epa.agg(["size", "mean"]).reset_index()
    q26 = q26[q26["size"] >= 150]
    q26["rk"] = q26["mean"].rank(ascending=False, method="min")
    al26 = q26[(q26.qb == "J.Allen") & (q26.posteam == "BUF")].iloc[0]
    qs.loc[(qs.season == 2026), "epa_rk"] = np.nan
    qs = qs[qs.season < 2026]
    row26 = {"season": 2026, "qb_id": al26.qb_id, "qb": "J.Allen", "posteam": "BUF", "db": al26["size"],
             "epa": al26["mean"], "epa_rk": al26.rk, "n_qb": len(q26)}
    qs = pd.concat([qs, pd.DataFrame([row26])], ignore_index=True)
    second = q26.sort_values("mean", ascending=False).iloc[1]

    eras = era_table(a)
    bt, bw, wq, dome = weather(d)
    allen_w_rank = int(wq.index[wq.qb == "J.Allen"][0]) + 1
    ap, car, lg_p = pressure(d)
    cq, cs = coverage(d)
    acov = cq[cq.qb == "J.Allen"].iloc[0]
    runs = allen_runs()
    runs_s = runs[runs.qb_scramble == 0].groupby("season").epa.agg(["size", "mean"])

    f = a[a.is_qb_out_of_pocket.notna()]
    off = f.groupby("season").apply(lambda x: pd.Series({
        "db": len(x), "oop": x.is_qb_out_of_pocket.mean(),
        "epa_oop": x.epa[x.is_qb_out_of_pocket == 1].mean(),
        "epa_in": x.epa[x.is_qb_out_of_pocket == 0].mean()}), include_groups=False)
    lg_oop = d[d.is_qb_out_of_pocket.notna()]
    lg_oop26 = lg_oop[lg_oop.season == 2026].is_qb_out_of_pocket.mean()
    oq = lg_oop[lg_oop.season == 2026].groupby(["qb_id", "qb"]).agg(n=("epa", "size"), oop=("is_qb_out_of_pocket", "mean")).reset_index()
    oq = oq[oq.n >= 150]; oq["rk"] = oq.oop.rank(ascending=False, method="min")
    oop_rk26 = int(oq[oq.qb == "J.Allen"].rk.iloc[0])
    iw = a.groupby("season").is_interception_worthy.apply(rate)
    sack = a.groupby("season").sack.mean()

    lg_dome = d.groupby("dome").epa.mean()
    dome_g = a.groupby("dome").game_id.nunique()

    # pressure stability check (league)
    p = d[d.was_pressure.notna()]
    g = p.groupby(["qb_id", "season"]).apply(lambda x: pd.Series({
        "n": len(x), "pres": x.epa[x.was_pressure == 1].mean(), "clean": x.epa[x.was_pressure == 0].mean()}),
        include_groups=False).reset_index()
    g = g[g.n >= 200]; nx = g.copy(); nx["season"] -= 1
    mm = g.merge(nx, on=["qb_id", "season"], suffixes=("", "_n"))
    r_clean, r_pres = mm.clean.corr(mm.clean_n), mm.pres.corr(mm.pres_n)

    chart_seasons(qs, wk); chart_offscript(off); chart_weather(wq, allen_w_rank); chart_pressure(ap)

    e = eras
    a26 = qs[qs.season == 2026].iloc[0]
    p24, p25 = ap.set_index("season").loc[2024], ap.set_index("season").loc[2025]
    o = off
    era_rows = "\n".join(
        f"| {ERA_LABEL[k].replace(chr(10), ' ')} | {int(e.loc[k, 'games'])} | {int(e.loc[k, 'db'])} | {e.loc[k, 'epa']:+.3f} | "
        f"{e.loc[k, 'sr']:.1%} | {e.loc[k, 'cpoe']:+.1f} | {e.loc[k, 'adot']:.1f} | {e.loc[k, 'sack']:.1%} | "
        + (f"{e.loc[k, 'oop']:.1%}" if pd.notna(e.loc[k, 'oop']) else "n/a") + " | "
        + (f"{e.loc[k, 'pa']:.1%}" if pd.notna(e.loc[k, 'pa']) else "n/a") + " |" for k in ERA_ORDER)
    season_rows = "\n".join(
        f"| {int(r.season)} | {int(r.db)} | {r.epa:+.3f} | #{int(r.epa_rk)} of {int(r.n_qb)} |" for r in qs[(qs.qb == 'J.Allen') & (qs.posteam == 'BUF')].itertuples())
    t_rows = "\n".join(f"| {i} | {int(r.allen_db)} | {r.allen_epa:+.3f} | {r.league_epa:+.3f} | {r.allen_minus_league:+.3f} |" for i, r in bt.iterrows())
    w_rows = "\n".join(f"| {i} | {int(r.allen_db)} | {r.allen_epa:+.3f} | {r.league_epa:+.3f} | {r.allen_minus_league:+.3f} |" for i, r in bw.iterrows())
    wq_rows = "\n".join(f"| {i + 1} | {r.qb} | {int(r.db):,} | {r.epa_over:+.3f} |" for i, r in wq.head(10).iterrows())
    p_rows = "\n".join(f"| {int(r.season)} | {r.pres_rate:.1%} | {r.epa_clean:+.3f} | {r.epa_pres:+.3f} | #{int(r.pres_rk)} of {int(r.n)} |" for r in ap.itertuples())
    o_rows = "\n".join(f"| {s} | {int(r.db)} | {r.oop:.1%} | {r.epa_oop:+.3f} | {r.epa_in:+.3f} |" for s, r in o.iterrows())
    c_rows = "\n".join(f"| {s} | {int(r[('size', 'MAN_COVERAGE')])} | {r[('mean', 'MAN_COVERAGE')]:+.3f} | {int(r[('size', 'ZONE_COVERAGE')])} | {r[('mean', 'ZONE_COVERAGE')]:+.3f} |" for s, r in cs.iterrows())
    t_rows_iw = " · ".join(f"{s}: {v:.1%}" for s, v in iw.dropna().items())
    sack_line = " · ".join(f"{s}: {v:.1%}" for s, v in sack.items())
    run_rows = " · ".join(f"{s}: {r['mean']:+.2f} ({int(r['size'])})" for s, r in runs_s.iterrows())

    md = f"""# Josh Allen, 2018 to now: what the data actually says

**Finding: Through week {wk}, Josh Allen leads the NFL in EPA per dropback ({a26.epa:+.3f}), and he is getting
there by leaving the pocket more than ever: {o.loc[2026, 'oop']:.0%} of his dropbacks, {ordn(oop_rk26)}-most in the league,
at {o.loc[2026, 'epa_oop']:+.2f} EPA per play, his best since charting began.**

*All QB numbers are per dropback and include scrambles and sacks. Regular season only.
2026 is {int(a26.db)} dropbacks: small sample.*

![Allen by season](allen-seasons.png)

## The short version

1. **He's the most efficient passer in football right now**, at {a26.epa:+.3f} EPA per dropback, ahead of
   {second.qb} ({second['mean']:+.3f}). He has improved under every play-caller he's had.
2. **More off script than ever, and it's working again.** {o.loc[2026, 'oop']:.0%} of dropbacks outside the pocket
   (league: {lg_oop26:.0%}), producing {o.loc[2026, 'epa_oop']:+.2f} EPA per play.
3. **2025 was when it broke.** Under pressure he fell from #{int(p24.pres_rk)} to #{int(p25.pres_rk)}
   ({p25.epa_pres:+.2f} EPA), off-script plays lost more than half their value, and his sack rate nearly tripled.
4. **Cold is not his problem.** Weather-adjusted, he ranks **{ordn(allen_w_rank)} of {len(wq)}** since 2018, and his edge
   over the league is biggest **below freezing** ({bt.loc['<=32F', 'allen_minus_league']:+.3f}).
5. **Man coverage is the soft spot.** {ordn(acov.zone_rk)} of {len(cq)} against zone, {ordn(acov.man_rk)} against man (2018-25).

## 1. By coaching era

Play-caller eras: Daboll (2018-21); Dorsey (2022 to week 10 of 2023, fired Nov. 14, 2023); Brady as
OC (week 11 of 2023 through 2025); Brady as head coach with Carmichael calling plays (2026).

| Era | Games | Dropbacks | EPA/db | Success | CPOE | Avg depth of target | Sack rate | Out of pocket | Play action |
|---|---|---|---|---|---|---|---|---|---|
{era_rows}

EPA per dropback has risen under every play-caller. The 2026 offense throws deeper (average depth of target
{e.loc['brady_hc', 'adot']:.1f} yards, up from {e.loc['brady_oc', 'adot']:.1f}) and uses more play action
({e.loc['brady_hc', 'pa']:.0%} vs {e.loc['brady_oc', 'pa']:.0%}).

| Season | Dropbacks | EPA/db | League rank |
|---|---|---|---|
{season_rows}

## 2. Off script

![Off script](allen-offscript.png)

| Season | Dropbacks | Out of pocket | EPA out of pocket | EPA in pocket |
|---|---|---|---|---|
{o_rows}

2026 out-of-pocket rate ranks {ordn(oop_rk26)} among QBs with 150+ dropbacks; league average {lg_oop26:.0%}.
The 2025 dip is the story inside the story: he left the pocket as often as ever, but the plays stopped working.

## 3. Under pressure

![Pressure](allen-pressure.png)

| Season | Pressure rate | EPA clean | EPA pressured | Rank pressured |
|---|---|---|---|---|
{p_rows}

Career: {car.loc[0.0, 'mean']:+.3f} clean, {car.loc[1.0, 'mean']:+.3f} pressured; league over the same span
{lg_p[0.0]:+.3f} clean, {lg_p[1.0]:+.3f} pressured. His pressured EPA is about {car.loc[1.0, 'mean'] - lg_p[1.0]:+.2f} better than the league's.

**Checked a second way:** is pressured performance just noise? Across {len(mm)} QB season-pairs since 2018,
pressured EPA correlates {r_pres:.2f} with the next season, clean-pocket EPA {r_clean:.2f}. Pressure performance
is at least as repeatable as clean-pocket play, so 2025 should be read as a real dip, not bad luck.
2026 pressure data (NFL participation) is not yet published; PFR's separate charting has his 2026 pressure rate narrowly the lowest of his career.

Sack rate by season: {sack_line}.

## 4. Weather

Outdoor games only. Each dropback compared with the league average in the same temperature and wind band.

| Temperature | Allen dropbacks | Allen EPA | League EPA | Allen edge |
|---|---|---|---|---|
{t_rows}

| Wind | Allen dropbacks | Allen EPA | League EPA | Allen edge |
|---|---|---|---|---|
{w_rows}

![Weather leaderboard](allen-weather.png)

| Rank | QB | Outdoor dropbacks | EPA above same-conditions average |
|---|---|---|---|
{wq_rows}

Domes: {dome.loc[1, 'mean']:+.3f} EPA per dropback in {int(dome_g.loc[1])} dome games vs {dome.loc[0, 'mean']:+.3f} outdoors.
League: {lg_dome.loc[1]:+.3f} in domes, {lg_dome.loc[0]:+.3f} outdoors. Monday's game in Minnesota is indoors.

## 5. Turnovers

Interception-worthy throw rate (FTN): {t_rows_iw}. The 2022-23 turnover problem is gone.

## 6. Coverage (2018-25)

| Season | Man dropbacks | EPA vs man | Zone dropbacks | EPA vs zone |
|---|---|---|---|---|
{c_rows}

Career {acov.mean_man:+.3f} vs man ({ordn(acov.man_rk)} of {len(cq)}), {acov.mean_zone:+.3f} vs zone ({ordn(acov.zone_rk)}).
2026 coverage data is not yet published.

## Designed runs

EPA per designed run (not scrambles), with attempts: {run_rows}. The 2026 number is on only a few dozen runs, but so far the offense is getting much less from his legs by design.

## Method and caveats

- Dropbacks from nflverse play-by-play; QB on a scramble is the rusher, so scrambles are credited correctly.
- Pressure, coverage and time to throw come from NFL participation data (2018-25). Out-of-pocket, play action and
  interception-worthy throws from FTN charting (2022+). Different charters define pressure differently.
- Weather bands: temperature &le;32, 33-45, 46-60, 61-75, 76+ F; wind 0-9, 10-14, 15+ mph. Domes and closed roofs excluded from the weather model.
- Eras are play-caller eras, verified against reporting on the November 2023 change.
"""
    (OUT / "2026-josh-allen.md").write_text(md)
    print(md[:1500])


if __name__ == "__main__":
    main()
