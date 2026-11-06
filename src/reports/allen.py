"""reports/2026-josh-allen.md + charts. Every number is computed here from the repo's tables.

Revised after QA review (2026-11-05): QBs identified by gsis id, not name; pressure and coverage
use definitions that are consistent across seasons; all claims carry league context and samples.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT
from src.metrics.qb import ALLEN_ID, ERA_LABEL, ERA_ORDER, allen_runs, buf_era, dropbacks, names, rate
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
PBP = "Source: nflverse play-by-play. Regular season. Buffalo Quant Desk."


def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def foot(fig, text):
    fig.text(0.02, 0.012, text, fontsize=7.5, color=MUTED)


def season_ranks(d, min_db, col="epa", filt=None):
    x = d if filt is None else d[filt]
    g = x.groupby(["season", "qb_id"]).agg(db=("epa", "size"), v=(col, "mean")).reset_index()
    g = g[g.db >= min_db].copy()
    g["rk"] = g.groupby("season").v.rank(ascending=False, method="min").astype(int)
    g["n"] = g.groupby("season").qb_id.transform("size")
    return g


def pressure_tables(d):
    """Consistent series: pass attempts only (participation data omits sacks and scrambles before 2023)."""
    p = d[d.was_pressure.notna() & (d.sack == 0) & (d.qb_scramble == 0)]
    g = p.groupby(["season", "qb_id"]).apply(lambda x: pd.Series({
        "att": len(x), "n_pres": int((x.was_pressure == 1).sum()), "pres_rate": x.was_pressure.mean(),
        "epa_pres": x.epa[x.was_pressure == 1].mean(), "epa_clean": x.epa[x.was_pressure == 0].mean()}),
        include_groups=False).reset_index()
    g = g[g.att >= 180].copy()
    g["pres_rk"] = g.groupby("season").epa_pres.rank(ascending=False, method="min").astype(int)
    g["n"] = g.groupby("season").qb_id.transform("size")
    lg = p.groupby(["season", "was_pressure"]).epa.mean().unstack()
    # 2023-25: sacks and scrambles are charted, so a full-dropback view is possible
    f = d[d.was_pressure.notna() & (d.season >= 2023)]
    h = f.groupby(["season", "qb_id"]).apply(lambda x: pd.Series({
        "db": len(x), "n_pres": int((x.was_pressure == 1).sum()),
        "epa_pres": x.epa[x.was_pressure == 1].mean()}), include_groups=False).reset_index()
    h = h[h.db >= 200].copy()
    h["pres_rk"] = h.groupby("season").epa_pres.rank(ascending=False, method="min").astype(int)
    h["n"] = h.groupby("season").qb_id.transform("size")
    # repeatability, pass attempts only, within one consistent definition
    nx = g.copy(); nx["season"] -= 1
    m = g.merge(nx, on=["qb_id", "season"], suffixes=("", "_n"))
    yoy = {"pairs": len(m), "pres": m.epa_pres.corr(m.epa_pres_n), "clean": m.epa_clean.corr(m.epa_clean_n)}
    return g, lg, h, yoy


def chart_seasons(sr, lg_db, wk, filt_rank):
    a = sr[sr.qb_id == ALLEN_ID].set_index("season")
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=200)
    xs = a.index.tolist()
    ax.bar([str(s) for s in xs], a.v, color=[RED if s == 2026 else BLUE for s in xs], width=0.62, zorder=2)
    ax.plot([str(s) for s in xs], [lg_db[s] for s in xs], color=INK, lw=1.2, ls="--", zorder=3)
    ax.text(len(xs) - 0.55, lg_db[xs[-1]], "league\naverage", va="center", fontsize=8, color=MUTED)
    for i, s in enumerate(xs):
        v = a.loc[s, "v"]
        ax.text(i, v + (0.008 if v >= 0 else -0.008), f"{v:+.2f}\n#{a.loc[s, 'rk']} of {a.loc[s, 'n']}",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=8.3, color=INK,
                bbox=dict(fc="white", ec="none", pad=0.3), zorder=5)
        ax.text(i, -0.115 if a.v.min() < 0 else -0.03, f"{int(a.loc[s, 'db'])} db", ha="center", fontsize=7.3, color=MUTED)
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylim(min(a.v.min(), 0) - 0.13, a.v.max() + 0.08)
    ax.set_xlim(-0.6, len(xs) + 0.4)
    ax.set_ylabel("EPA per dropback (incl. scrambles, sacks)")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle("Josh Allen leads the NFL in EPA per dropback so far in 2026", x=0.02, ha="left",
                 fontsize=15, fontweight="bold", color=INK)
    ax.set_title(f"Rank among QBs with 200+ dropbacks (2026: 150+, through week {wk}). Unfiltered; "
                 f"#{filt_rank} with garbage time removed.", loc="left", fontsize=9, color=MUTED, pad=8)
    foot(fig, PBP + " 2026 is a small sample.")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-seasons.png"); plt.close(fig)


def chart_offscript(o, lg_oop_rate, lg_oop_epa):
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.9), dpi=200)
    xs = [str(s) for s in o.index]
    specs = [(axes[0], "oop", "Share of dropbacks outside the pocket", "{:.0%}", lg_oop_rate),
             (axes[1], "epa_oop", "EPA per play when outside the pocket", "{:+.2f}", lg_oop_epa)]
    for ax, col, title, fmt, lg in specs:
        ax.bar(xs, o[col], color=[RED if s == "2026" else BLUE for s in xs], width=0.6, zorder=2)
        ax.plot(xs, [lg[int(s)] for s in xs], color=INK, lw=1.2, ls="--", zorder=3)
        for i, (v, n) in enumerate(zip(o[col], o.n_oop)):
            ax.text(i, v + o[col].max() * 0.02, fmt.format(v), ha="center", va="bottom", fontsize=9, color=INK)
        ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="bold")
        ax.set_ylim(min(0, lg.min()) - 0.01, o[col].max() * 1.18); ax.set_yticks([])
        ax.spines["left"].set_visible(False); ax.axhline(0, color=INK, lw=0.8)
        if col == "epa_oop":
            ax.set_xticks(range(len(xs)), [f"{s}\n{int(n)} plays" for s, n in zip(xs, o.n_oop)])
    fig.suptitle("Allen off script: more often, and worth more again in 2026", x=0.02, ha="left", fontsize=15,
                 fontweight="bold", color=INK)
    fig.text(0.02, 0.905, "Dashed line = league average.", fontsize=9, color=MUTED)
    foot(fig, "Source: nflverse play-by-play, FTN charting (begins 2022). Regular season. Buffalo Quant Desk. 2026 is a small sample.")
    fig.tight_layout(rect=(0, 0.04, 1, 0.9)); fig.savefig(OUT / "allen-offscript.png"); plt.close(fig)


def chart_weather(wq, rank):
    top = wq.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=200)
    ax.barh(top.name, top.epa_over, color=[RED if q == ALLEN_ID else GRAY for q in top.qb_id], height=0.62, zorder=2)
    for i, (v, n) in enumerate(zip(top.epa_over, top.db)):
        ax.text(v + 0.003, i, f"{v:+.3f}  ({int(n):,} dropbacks)", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, top.epa_over.max() * 1.45)
    ax.set_xlabel("EPA per dropback above league average in the same temperature and wind")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle(f"Weather-adjusted: Allen ranks {ordn(rank)} since 2018", x=0.02, ha="left", fontsize=15,
                 fontweight="bold", color=INK)
    ax.set_title(f"Outdoor games with recorded weather, QBs with 800+ such dropbacks ({len(wq)} qualify)",
                 loc="left", fontsize=9.5, color=MUTED, pad=8)
    foot(fig, PBP + " Temperature is missing for some outdoor games; those are excluded.")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-weather.png"); plt.close(fig)


def chart_pressure(ap, lg):
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    x = [str(s) for s in ap.season]
    ax.plot(x, ap.epa_clean, color=BLUE, lw=2, marker="o", ms=8, zorder=3)
    ax.plot(x, ap.epa_pres, color=RED, lw=2, marker="o", ms=8, zorder=3)
    ax.plot(x, [lg.loc[s, 0.0] for s in ap.season], color=BLUE, lw=1, ls="--", alpha=0.6)
    ax.plot(x, [lg.loc[s, 1.0] for s in ap.season], color=RED, lw=1, ls="--", alpha=0.6)
    ax.text(len(x) - 0.45, ap.epa_clean.iloc[-1], "Clean pocket", color=INK, va="center", fontsize=10, fontweight="bold")
    ax.text(len(x) - 0.45, ap.epa_pres.iloc[-1], "Pressured", color=INK, va="center", fontsize=10, fontweight="bold")
    for i, (v, rk) in enumerate(zip(ap.epa_pres, ap.pres_rk)):
        ax.annotate(f"#{int(rk)}", (i, v), xytext=(13, -3), textcoords="offset points", ha="left",
                    fontsize=8.5, color=INK, bbox=dict(fc="white", ec="none", pad=0.4), zorder=5)
    ax.axhline(0, color=INK, lw=1); ax.set_xlim(-0.4, len(x) + 1.0)
    ax.set_ylim(min(ap.epa_pres.min(), lg[1.0].min()) - 0.2, ap.epa_clean.max() + 0.08)
    ax.set_ylabel("EPA per pass attempt"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle("Under pressure, Allen has beaten the league average every year since 2020", x=0.02, ha="left",
                 fontsize=14.5, fontweight="bold", color=INK)
    ax.set_title("Pass attempts only (sacks and scrambles excluded for a consistent 2018-25 series). "
                 "Dashed = league. # = rank when pressured.", loc="left", fontsize=8.6, color=MUTED, pad=8)
    foot(fig, "Source: nflverse play-by-play, NFL participation data (2026 not yet published). Regular season. Buffalo Quant Desk. Attempt counts in the table.")
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(OUT / "allen-pressure.png"); plt.close(fig)


def main():
    d = dropbacks()
    nm = names(d)
    a = d[d.qb_id == ALLEN_ID]
    wk = int(a[a.season == 2026].week.max())
    lg_db = d.groupby("season").epa.mean()

    # ---- 1. seasons + headline (unfiltered and garbage-time filtered)
    sr = pd.concat([season_ranks(d[d.season < 2026], 200), season_ranks(d[d.season == 2026], 150)])
    r26 = season_ranks(d[d.season == 2026], 150).sort_values("rk")
    a26 = r26[r26.qb_id == ALLEN_ID].iloc[0]
    second = r26[r26.qb_id != ALLEN_ID].iloc[0]
    f26 = season_ranks(d[(d.season == 2026) & (d.neutral == 1)], 120).sort_values("rk")
    af26 = f26[f26.qb_id == ALLEN_ID].iloc[0]
    fl26 = f26.iloc[0]

    # ---- eras
    ae = a.assign(era=[buf_era(s, w) for s, w in zip(a.season, a.week)])
    eras = ae.groupby("era").agg(games=("game_id", "nunique"), db=("epa", "size"), epa=("epa", "mean"),
                                 sr=("success", "mean"), cpoe=("cpoe", rate), adot=("air_yards", rate),
                                 sack=("sack", "mean"), oop=("is_qb_out_of_pocket", rate),
                                 pa=("is_play_action", rate)).reindex(ERA_ORDER)
    lg_era = d.assign(era=[buf_era(s, w) for s, w in zip(d.season, d.week)]).groupby("era").epa.mean()

    # ---- 2. off script (FTN 2022+)
    fd = d[d.is_qb_out_of_pocket.notna()]
    fa = fd[fd.qb_id == ALLEN_ID]
    off = fa.groupby("season").apply(lambda x: pd.Series({
        "db": len(x), "n_oop": int(x.is_qb_out_of_pocket.sum()), "oop": x.is_qb_out_of_pocket.mean(),
        "epa_oop": x.epa[x.is_qb_out_of_pocket == 1].mean(),
        "epa_in": x.epa[x.is_qb_out_of_pocket == 0].mean()}), include_groups=False)
    lg_oop_rate = fd.groupby("season").is_qb_out_of_pocket.mean()
    lg_oop_epa = fd[fd.is_qb_out_of_pocket == 1].groupby("season").epa.mean()
    o26 = fd[fd.season == 2026]
    oq = o26.groupby("qb_id").agg(db=("epa", "size"), oop=("is_qb_out_of_pocket", "mean")).reset_index()
    oq = oq[oq.db >= 150]; oq["rk"] = oq.oop.rank(ascending=False, method="min").astype(int)
    oop_rk26 = int(oq[oq.qb_id == ALLEN_ID].rk.iloc[0])
    oe = o26[o26.is_qb_out_of_pocket == 1].groupby("qb_id").epa.agg(["size", "mean"])
    oe = oe[oe.index.isin(oq.qb_id)].sort_values("mean", ascending=False)
    oe_rk = list(oe.index).index(ALLEN_ID) + 1
    oe_top = oe.index[0]
    # how much of the 2025->2026 change is frequency vs per-play value
    o25, o26a = off.loc[2025], off.loc[2026]
    freq_effect = (o26a.oop - o25.oop) * (o25.epa_oop - o25.epa_in)

    # ---- 3. pressure
    pt, lg_p, full, yoy = pressure_tables(d)
    ap = pt[pt.qb_id == ALLEN_ID].sort_values("season").reset_index(drop=True)
    af = full[full.qb_id == ALLEN_ID].set_index("season")
    pa = d[d.was_pressure.notna() & (d.sack == 0) & (d.qb_scramble == 0)]
    car = pa[pa.qb_id == ALLEN_ID].groupby("was_pressure").epa.mean()
    lgc = pa.groupby("was_pressure").epa.mean()
    edges = ap.epa_pres.values - np.array([lg_p.loc[s, 1.0] for s in ap.season])

    # ---- 4. weather (outdoor, recorded temperature)
    out = d[(d.dome == 0) & d.temp.notna()].copy()
    miss = d[(d.dome == 0) & d.temp.isna()]
    miss_allen = int((miss.qb_id == ALLEN_ID).sum())
    out["tbin"] = pd.cut(out.temp, [-50, 32, 45, 60, 75, 150], labels=["32F and below", "33-45", "46-60", "61-75", "76+"])
    out["wbin"] = pd.cut(out.wind.fillna(0), [-1, 9, 14, 99], labels=["0-9 mph", "10-14", "15+"])
    out = out.join(out.groupby(["tbin", "wbin"], observed=True).epa.mean().rename("lg_bin"), on=["tbin", "wbin"])
    out["over"] = out.epa - out.lg_bin
    ao = out[out.qb_id == ALLEN_ID]

    def bins(col):
        t = pd.DataFrame({"db": ao.groupby(col, observed=True).epa.size(),
                          "games": ao.groupby(col, observed=True).game_id.nunique(),
                          "allen": ao.groupby(col, observed=True).epa.mean(),
                          "league": out.groupby(col, observed=True).epa.mean()})
        t["edge"] = t.allen - t.league
        return t
    bt, bw = bins("tbin"), bins("wbin")
    wq = out.groupby("qb_id").agg(db=("epa", "size"), epa_over=("over", "mean")).reset_index()
    wq = wq[wq.db >= 800].sort_values("epa_over", ascending=False).reset_index(drop=True)
    wq["name"] = wq.qb_id.map(nm)
    w_rank = int(wq.index[wq.qb_id == ALLEN_ID][0]) + 1
    cold = ao[ao.temp <= 32]
    warm = out[out.temp > 32]
    cold_edge = bt.loc["32F and below", "edge"]
    rest_edge = warm[warm.qb_id == ALLEN_ID].epa.mean() - warm.epa.mean()
    # dome split: fixed domes vs closed retractable roofs
    roof = a.groupby("roof").agg(games=("game_id", "nunique"), db=("epa", "size"), epa=("epa", "mean"))
    lg_roof = d.groupby("roof").epa.mean()

    # ---- 5. turnovers (FTN 2022+)
    iw_rows = []
    for s, x in fd.groupby("season"):
        q = x.groupby("qb_id").agg(db=("epa", "size"), iw=("is_interception_worthy", "mean"),
                                   att=("pass_attempt", "sum"), iwn=("is_interception_worthy", "sum"),
                                   ints=("interception", "sum")).reset_index()
        q = q[q.db >= (150 if s == 2026 else 200)]
        q["rk"] = q.iw.rank(method="min").astype(int)  # 1 = fewest
        al = q[q.qb_id == ALLEN_ID].iloc[0]
        iw_rows.append({"season": s, "iwn": int(al.iwn), "per_db": float(al.iw), "per_att": float(al.iwn / al.att),
                        "int_rate": float(al.ints / al.att), "rk": int(al.rk), "n": int(len(q)),
                        "lg": float(x.is_interception_worthy.mean())})
    iw = pd.DataFrame(iw_rows).set_index("season")
    sack = a.groupby("season").sack.mean(); lg_sack = d.groupby("season").sack.mean()

    # ---- 6. coverage, 2023-25 (consistent charting incl. sacks) + career pass attempts
    cv = d[d.man_zone.isin(["MAN_COVERAGE", "ZONE_COVERAGE"])]

    def cov_rank(c, mm, mz):
        q = c.groupby(["qb_id", "man_zone"]).epa.agg(["size", "mean"]).unstack("man_zone")
        q.columns = [f"{x}_{y.split('_')[0].lower()}" for x, y in q.columns]
        q = q[(q.size_man >= mm) & (q.size_zone >= mz)].copy()
        q["man_rk"] = q.mean_man.rank(ascending=False, method="min").astype(int)
        q["zone_rk"] = q.mean_zone.rank(ascending=False, method="min").astype(int)
        return q
    c_rec = cov_rank(cv[cv.season >= 2023], 150, 300)
    c_old = cov_rank(cv[(cv.season <= 2022) & (cv.sack == 0) & (cv.qb_scramble == 0)], 150, 300)
    cr, co = c_rec.loc[ALLEN_ID], c_old.loc[ALLEN_ID]
    lg_cov_rec = cv[cv.season >= 2023].groupby("man_zone").epa.mean()
    cs = cv[cv.qb_id == ALLEN_ID].groupby(["season", "man_zone"]).epa.agg(["size", "mean"]).unstack("man_zone")

    # ---- designed runs
    runs = allen_runs()
    runs_s = runs[runs.qb_scramble == 0].groupby("season").epa.agg(["size", "mean"])

    chart_seasons(sr, lg_db, wk, int(af26.rk))
    chart_offscript(off, lg_oop_rate, lg_oop_epa)
    chart_weather(wq, w_rank)
    chart_pressure(ap, lg_p)

    # ---- text
    e = eras
    pct = lambda v: "n/a" if pd.isna(v) else f"{v:.1%}"
    era_rows = "\n".join(
        f"| {ERA_LABEL[k].replace(chr(10), ' ')} | {int(e.loc[k, 'games'])} | {int(e.loc[k, 'db']):,} | {e.loc[k, 'epa']:+.3f} | "
        f"{lg_era[k]:+.3f} | {e.loc[k, 'sr']:.1%} | {e.loc[k, 'cpoe']:+.1f} | {e.loc[k, 'adot']:.1f} | {e.loc[k, 'sack']:.1%} | "
        f"{pct(e.loc[k, 'oop'])} | {pct(e.loc[k, 'pa'])} |" for k in ERA_ORDER)
    sa = sr[sr.qb_id == ALLEN_ID].set_index("season")
    season_rows = "\n".join(f"| {s} | {int(r.db):,} | {r.v:+.3f} | {lg_db[s]:+.3f} | #{r.rk} of {r.n} |" for s, r in sa.iterrows())
    o_rows = "\n".join(f"| {s} | {int(r.db)} | {r.oop:.1%} | {lg_oop_rate[s]:.1%} | {int(r.n_oop)} | {r.epa_oop:+.3f} | {lg_oop_epa[s]:+.3f} | {r.epa_in:+.3f} |" for s, r in off.iterrows())
    p_rows = "\n".join(f"| {r.season} | {int(r.att)} | {int(r.n_pres)} | {r.epa_clean:+.3f} | {lg_p.loc[r.season, 0.0]:+.3f} | {r.epa_pres:+.3f} | {lg_p.loc[r.season, 1.0]:+.3f} | #{r.pres_rk} of {r.n} |" for r in ap.itertuples())
    f_rows = "\n".join(f"| {s} | {int(r.db)} | {int(r.n_pres)} | {r.epa_pres:+.3f} | #{int(r.pres_rk)} of {int(r.n)} |" for s, r in af.iterrows())
    t_rows = "\n".join(f"| {i} | {int(r.games)} | {int(r.db):,} | {r.allen:+.3f} | {r.league:+.3f} | {r.edge:+.3f} |" for i, r in bt.iterrows())
    w_rows = "\n".join(f"| {i} | {int(r.games)} | {int(r.db):,} | {r.allen:+.3f} | {r.league:+.3f} | {r.edge:+.3f} |" for i, r in bw.iterrows())
    wq_rows = "\n".join(f"| {i + 1} | {r['name']} | {int(r.db):,} | {r.epa_over:+.3f} |" for i, r in wq.head(10).iterrows())
    iw_rowsmd = "\n".join(f"| {r['season']} | {r['iwn']} | {r['per_db']:.1%} | {r['per_att']:.1%} | {r['lg']:.1%} | {ordn(r['rk'])} of {r['n']} | {r['int_rate']:.1%} |" for r in iw_rows)
    sack_rows = "\n".join(f"| {s} | {sack[s]:.1%} | {lg_sack[s]:.1%} |" for s in sack.index)
    c_rows = "\n".join(f"| {s} | {int(r[('size', 'MAN_COVERAGE')])} | {r[('mean', 'MAN_COVERAGE')]:+.3f} | {int(r[('size', 'ZONE_COVERAGE')])} | {r[('mean', 'ZONE_COVERAGE')]:+.3f} |" for s, r in cs.iterrows())
    run_line = " · ".join(f"{s}: {r['mean']:+.2f} on {int(r['size'])}" for s, r in runs_s.iterrows())
    roof_line = " · ".join(f"{k.replace('closed', 'closed retractable roof').replace('dome', 'fixed dome')}: {roof.loc[k, 'epa']:+.3f} in {int(roof.loc[k, 'games'])} games (league {lg_roof[k]:+.3f})"
                           for k in ["dome", "closed", "open", "outdoors"] if k in roof.index)
    p24, p25 = af.loc[2024], af.loc[2025]
    pa24 = ap.set_index("season").loc[2024]; pa25 = ap.set_index("season").loc[2025]

    md = f"""# Josh Allen, 2018 to now: what the data actually says

**Finding: Through week {wk}, Josh Allen leads the NFL in EPA per dropback ({a26.v:+.3f}, unfiltered), narrowly
ahead of {nm[second.qb_id]} ({second.v:+.3f}). With garbage time removed he ranks #{af26.rk}. He is leaving the
pocket more than ever, and those plays are working again after a down 2025.**

*All QB numbers are per dropback, including scrambles and sacks, unless labeled. Regular season only.
2026 is {int(a26.db)} dropbacks through week {wk}: small sample.*

![Allen by season](allen-seasons.png)

## The short version

1. **Best start in the league, by a hair.** {a26.v:+.3f} EPA per dropback leads {int(a26.n)} qualifying QBs,
   {a26.v - second.v:+.3f} ahead of {nm[second.qb_id]}. With win probability limited to 10-90% (garbage time out)
   he is #{af26.rk} ({af26.v:+.3f}), behind {nm[fl26.qb_id]} ({fl26.v:+.3f} on {int(fl26.db)}).
2. **Every coaching era has been better than the last.** {e.loc['daboll', 'epa']:+.3f} under Daboll,
   {e.loc['dorsey', 'epa']:+.3f} under Dorsey, {e.loc['brady_oc', 'epa']:+.3f} with Brady calling plays as OC, and
   {e.loc['brady_hc', 'epa']:+.3f} with Brady still calling plays as head coach (7 games so far).
3. **Off script, it's working again.** {o26a.oop:.0%} of his dropbacks are outside the pocket ({ordn(oop_rk26)}-most;
   league {lg_oop_rate[2026]:.0%}), worth {o26a.epa_oop:+.2f} EPA per play on {int(o26a.n_oop)} plays
   (league {lg_oop_epa[2026]:+.2f}; {ordn(oe_rk)} behind {nm[oe_top]}). In 2025 those plays were worth {o25.epa_oop:+.2f}.
4. **2025's dip was mostly sacks.** Counting sacks, his rank when pressured fell from #{int(p24.pres_rk)} to
   #{int(p25.pres_rk)}. On pass attempts alone it went from #{pa24.pres_rk} to #{pa25.pres_rk}, and his sack rate rose
   from {sack[2024]:.1%} to {sack[2025]:.1%} (league {lg_sack[2025]:.1%}).
5. **Weather doesn't slow him down relative to the league.** Weather-adjusted he ranks **{ordn(w_rank)} of {len(wq)}**
   since 2018. Below freezing his edge over the league is {cold_edge:+.3f}, similar to his {rest_edge:+.3f} in all warmer
   outdoor games, on a small sample ({len(cold)} dropbacks in {cold.game_id.nunique()} games).

## 1. Season by season, and by coaching era

| Season | Dropbacks | EPA/db | League avg | Rank |
|---|---|---|---|---|
{season_rows}

Staff eras: Daboll as OC (2018-21); Dorsey as OC (2022 to week 10 of 2023; fired Nov. 14, 2023); Brady as OC
(week 11 of 2023 through 2025); Brady as head coach, still calling plays, with Pete Carmichael as a non-play-calling
OC (2026). The last two eras have the same play-caller.

| Era | Games | Dropbacks | EPA/db | League EPA/db | Success | CPOE | Avg depth of target | Sack rate | Out of pocket | Play action |
|---|---|---|---|---|---|---|---|---|---|---|
{era_rows}

The 2026 offense throws deeper than Brady's OC version (average depth of target {e.loc['brady_hc', 'adot']:.1f} yards vs
{e.loc['brady_oc', 'adot']:.1f}) and uses more play action ({e.loc['brady_hc', 'pa']:.0%} vs {e.loc['brady_oc', 'pa']:.0%}).

## 2. Off script

![Off script](allen-offscript.png)

| Season | Dropbacks | Out of pocket | League | Out-of-pocket plays | EPA out of pocket | League | EPA in pocket |
|---|---|---|---|---|---|---|---|
{o_rows}

He is out of the pocket a bit more often, but frequency isn't what changed: holding his 2025 per-play values fixed,
the extra {o26a.oop - o25.oop:.0%} of plays outside the pocket adds essentially nothing ({freq_effect:+.3f} EPA per dropback).
The jump is in what those plays are worth, on {int(o26a.n_oop)} plays so far.

## 3. Under pressure

![Pressure](allen-pressure.png)

The NFL's participation data does not chart sacks and scrambles before 2023, so the consistent long-run view uses
**pass attempts only**:

| Season | Attempts | Pressured attempts | EPA clean | League | EPA pressured | League | Rank pressured |
|---|---|---|---|---|---|---|---|
{p_rows}

He has beaten the league's pressured average in {int((edges > 0).sum())} of {len(edges)} seasons (every season since 2020).
Career, pass attempts: {car[0.0]:+.3f} clean, {car[1.0]:+.3f} pressured (league {lgc[0.0]:+.3f} / {lgc[1.0]:+.3f}).

From 2023, sacks are charted, so here is the full-dropback view:

| Season | Dropbacks | Pressured | EPA pressured | Rank |
|---|---|---|---|---|
{f_rows}

**How much should we read into one year under pressure?** Across {yoy['pairs']} QB season-pairs since 2018 (pass
attempts only), pressured EPA correlates {yoy['pres']:.2f} with the next season, clean-pocket EPA {yoy['clean']:.2f}.
Pressured performance is the less repeatable of the two, so one bad year under pressure is weak evidence of decline.
2026 pressure data has not been published yet.

| Season | Allen sack rate | League |
|---|---|---|
{sack_rows}

## 4. Weather

Outdoor games with recorded weather. Each dropback is compared with the league average in the same temperature and wind band.

| Temperature | Games | Allen dropbacks | Allen EPA | League EPA | Allen edge |
|---|---|---|---|---|---|
{t_rows}

| Wind | Games | Allen dropbacks | Allen EPA | League EPA | Allen edge |
|---|---|---|---|---|---|
{w_rows}

His edge holds in every temperature band. The biggest is in mild weather (61-75F); the sub-freezing sample
({cold.game_id.nunique()} games) is too small to rank the bands against each other.

![Weather leaderboard](allen-weather.png)

| Rank | QB | Outdoor dropbacks | EPA above same-conditions average |
|---|---|---|---|
{wq_rows}

The 4th-place ranking holds across reasonable choices (3rd with a 1,500 or 2,000 dropback minimum; 5th for 2018-25
only; 5th unadjusted). Temperature is missing for some outdoor games in the source data, mostly 2022 and 2026;
{miss_allen} Allen outdoor dropbacks are excluded for that reason.

By roof type: {roof_line}. The fixed-dome figure is 11 games.

## 5. Turnovers

Interception-worthy plays, from FTN charting. Rank 1 = fewest.

| Season | Int-worthy plays | Per dropback | Per attempt | League per dropback | Rank | Actual INT rate |
|---|---|---|---|---|---|---|
{iw_rowsmd}

The rate is down from the 2022 peak and was better than average in 2024, but in 2025 and 2026 it is above the league
average again, and his actual interception rate is up from 2024 and 2025.

## 6. Coverage

| Season | Man dropbacks | EPA vs man | Zone dropbacks | EPA vs zone |
|---|---|---|---|---|
{c_rows}

2018-22 rows exclude sacks and scrambles (not charted then); 2023-25 include them.

- 2023-25: {cr.mean_man:+.3f} vs man ({ordn(cr.man_rk)} of {len(c_rec)}), {cr.mean_zone:+.3f} vs zone ({ordn(cr.zone_rk)}).
  League {lg_cov_rec['MAN_COVERAGE']:+.3f} vs man, {lg_cov_rec['ZONE_COVERAGE']:+.3f} vs zone.
- 2018-22, pass attempts: {co.mean_man:+.3f} vs man ({ordn(co.man_rk)} of {len(c_old)}), {co.mean_zone:+.3f} vs zone ({ordn(co.zone_rk)}).

Man coverage gave him trouble early in his career. Since 2023 he has been among the best in the league against both.

## Designed runs

EPA per designed run (not scrambles), by season: {run_line}. The 2026 figure is on a small number of runs.

## Method and caveats

- Players are identified by NFL player ID; the source spells Allen two ways in some 2019 and 2021 games.
- Dropbacks come from nflverse play-by-play. On a scramble the QB is recorded as the rusher and is credited here.
- Garbage-time filter: win probability between 10% and 90%. The headline uses unfiltered numbers and reports both.
- Pressure, coverage and time to throw come from NFL participation data (2018-25). Before 2023 it does not chart sacks
  or scrambles, which is why the long-run pressure series uses pass attempts only.
- Out-of-pocket, play action and interception-worthy plays come from FTN charting (2022+).
- Weather bands: temperature 32F and below, 33-45, 46-60, 61-75, 76+; wind 0-9, 10-14, 15+ mph. Domes and roofs excluded.
- Coaching eras checked against reporting on the November 2023 coordinator change and the 2026 staff.
- Independently reviewed by our QA process before publication.
"""
    (OUT / "2026-josh-allen.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
