"""Exploratory pass over all six Josh Allen angles. Prints tables; the report module formats them."""
import numpy as np
import pandas as pd

from src.metrics.qb import ERA_ORDER, allen_runs, buf_era, dropbacks, is_allen, rate

pd.set_option("display.width", 200)
MIN_DB = 200  # qualifying QB-season


def qb_seasons(d):
    g = d.groupby(["season", "qb_id", "qb", "posteam"])
    t = g.agg(db=("epa", "size"), epa=("epa", "mean"), cpoe=("cpoe", rate), sr=("success", "mean"),
              sack=("sack", "mean"), adot=("air_yards", rate), scr=("qb_scramble", "mean"),
              pres=("was_pressure", rate), ttt=("time_to_throw", rate),
              iw=("is_interception_worthy", rate), oop=("is_qb_out_of_pocket", rate)).reset_index()
    t = t[t.db >= MIN_DB]
    for m in ["epa", "cpoe", "sr"]:
        t[m + "_rk"] = t.groupby("season")[m].rank(ascending=False, method="min")
    t["n_qb"] = t.groupby("season").qb.transform("size")
    return t


def era_table(a):
    a = a.assign(era=[buf_era(s, w) for s, w in zip(a.season, a.week)])
    g = a.groupby("era")
    t = g.agg(games=("game_id", "nunique"), db=("epa", "size"), epa=("epa", "mean"), sr=("success", "mean"),
              cpoe=("cpoe", rate), adot=("air_yards", rate), sack=("sack", "mean"), scr=("qb_scramble", "mean"),
              pres=("was_pressure", rate), ttt=("time_to_throw", rate), iw=("is_interception_worthy", rate),
              oop=("is_qb_out_of_pocket", rate), pa=("is_play_action", rate))
    return t.reindex(ERA_ORDER)


def weather(d):
    out = d[(d.dome == 0) & d.temp.notna()].copy()
    out["tbin"] = pd.cut(out.temp, [-50, 32, 45, 60, 75, 150], labels=["<=32F", "33-45", "46-60", "61-75", "76+"])
    out["wbin"] = pd.cut(out.wind.fillna(0), [-1, 9, 14, 99], labels=["0-9 mph", "10-14", "15+"])
    lg = out.groupby(["tbin", "wbin"], observed=True).epa.mean().rename("lg_bin")
    out = out.join(lg, on=["tbin", "wbin"])
    out["epa_over_bin"] = out.epa - out.lg_bin
    al = out[is_allen(out)]
    by_t = pd.DataFrame({
        "allen_db": al.groupby("tbin", observed=True).epa.size(),
        "allen_epa": al.groupby("tbin", observed=True).epa.mean(),
        "league_epa": out.groupby("tbin", observed=True).epa.mean(),
    })
    by_t["allen_minus_league"] = by_t.allen_epa - by_t.league_epa
    by_w = pd.DataFrame({
        "allen_db": al.groupby("wbin", observed=True).epa.size(),
        "allen_epa": al.groupby("wbin", observed=True).epa.mean(),
        "league_epa": out.groupby("wbin", observed=True).epa.mean(),
    })
    by_w["allen_minus_league"] = by_w.allen_epa - by_w.league_epa
    # weather-adjusted QB ranking: mean EPA over same-conditions league average, outdoor only
    q = out.groupby(["qb_id", "qb"]).agg(db=("epa", "size"), epa_over=("epa_over_bin", "mean"),
                                         cold_db=("temp", lambda s: (s <= 32).sum())).reset_index()
    q = q[q.db >= 800].sort_values("epa_over", ascending=False).reset_index(drop=True)
    dome = d[is_allen(d)].groupby("dome").epa.agg(["size", "mean"])
    return by_t, by_w, q, dome


def pressure(d):
    p = d[d.was_pressure.notna()]
    q = p.groupby(["season", "qb_id", "qb", "posteam"]).apply(
        lambda x: pd.Series({"db": len(x), "pres_rate": x.was_pressure.mean(),
                             "epa_pres": x.epa[x.was_pressure == 1].mean(),
                             "epa_clean": x.epa[x.was_pressure == 0].mean()}), include_groups=False).reset_index()
    q = q[q.db >= MIN_DB]
    q["gap"] = q.epa_clean - q.epa_pres
    q["pres_rk"] = q.groupby("season").epa_pres.rank(ascending=False, method="min")
    q["n"] = q.groupby("season").qb.transform("size")
    allen = q[(q.qb == "J.Allen") & (q.posteam == "BUF")]
    car = p[is_allen(p)]
    lg = p.groupby("was_pressure").epa.mean()
    return allen, car.groupby("was_pressure").epa.agg(["size", "mean"]), lg


def coverage(d):
    c = d[d.man_zone.isin(["MAN_COVERAGE", "ZONE_COVERAGE"])]
    q = c.groupby(["qb_id", "qb", "posteam", "man_zone"]).epa.agg(["size", "mean"]).unstack("man_zone")
    q.columns = [f"{a}_{b.split('_')[0].lower()}" for a, b in q.columns]
    q = q[(q.size_man >= 300) & (q.size_zone >= 600)].reset_index()
    q["man_rk"] = q.mean_man.rank(ascending=False, method="min")
    q["zone_rk"] = q.mean_zone.rank(ascending=False, method="min")
    a = c[is_allen(c)]
    by_season = a.groupby(["season", "man_zone"]).epa.agg(["size", "mean"]).unstack("man_zone")
    return q, by_season


def main():
    d = dropbacks()
    a = d[is_allen(d)]
    print("== QB-season ranks (Allen) ==")
    qs = qb_seasons(d)
    print(qs[(qs.qb == "J.Allen") & (qs.posteam == "BUF")][["season", "db", "epa", "epa_rk", "cpoe", "cpoe_rk", "n_qb", "sack", "adot", "scr", "pres", "ttt", "iw", "oop"]].round(3).to_string(index=False))
    print("\n== Eras ==")
    print(era_table(a).round(3).to_string())
    print("\n== Weather ==")
    bt, bw, wq, dome = weather(d)
    print(bt.round(3)); print(bw.round(3)); print("dome split (1=dome):\n", dome.round(3))
    print("weather-adjusted outdoor EPA over same-conditions league, 2018-26, 800+ outdoor db:")
    print(wq.head(12).round(3).to_string()); print("Allen rank:", wq.index[wq.qb == "J.Allen"].tolist(), "of", len(wq))
    print("\n== Pressure ==")
    ap, car, lg = pressure(d)
    print(ap.round(3).to_string(index=False)); print(car.round(3)); print("league:", lg.round(3).to_dict())
    print("\n== Coverage (2018-25) ==")
    cq, cs = coverage(d)
    print(cq.sort_values("mean_man", ascending=False).head(8).round(3).to_string(index=False))
    print(cq[cq.qb == "J.Allen"].round(3).to_string(index=False), "of", len(cq))
    print(cs.round(3))
    print("\n== Runs ==")
    r = allen_runs()
    print(r.groupby(["season", "qb_scramble"]).epa.agg(["size", "mean", "sum"]).round(2).unstack().to_string())


if __name__ == "__main__":
    main()
