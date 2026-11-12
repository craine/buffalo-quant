"""NFL player card pages: site/cards/nfl/<slug>.html and site/cards/nfl/index.html, from reports/cards/nfl_players.json."""
import html
import json

from src.db import ROOT
from src.site.build import SITE, card_slug, ordn_txt, page, plural, spark_svg

NFL_COLORS = {  # card colors are our own approximations of each club's palette
    "BUF": ("#00338D", "#C60C30", "BILLS"), "MIA": ("#008E97", "#FC4C02", "DOLPHINS"), "NE": ("#002244", "#C60C30", "PATRIOTS"),
    "NYJ": ("#125740", "#8F8F8C", "JETS"), "BAL": ("#241773", "#9E7C0C", "RAVENS"), "CIN": ("#111111", "#FB4F14", "BENGALS"),
    "CLE": ("#311D00", "#FF3C00", "BROWNS"), "PIT": ("#111111", "#FFB612", "STEELERS"), "HOU": ("#03202F", "#A71930", "TEXANS"),
    "IND": ("#002C5F", "#A2AAAD", "COLTS"), "JAX": ("#006778", "#D7A22A", "JAGUARS"), "TEN": ("#0C2340", "#4B92DB", "TITANS"),
    "DEN": ("#002244", "#FB4F14", "BRONCOS"), "KC": ("#E31837", "#FFB81C", "CHIEFS"), "LV": ("#111111", "#A5ACAF", "RAIDERS"),
    "LAC": ("#0080C6", "#FFC20E", "CHARGERS"), "DAL": ("#003594", "#869397", "COWBOYS"), "NYG": ("#0B2265", "#A71930", "GIANTS"),
    "PHI": ("#004C54", "#A5ACAF", "EAGLES"), "WAS": ("#5A1414", "#FFB612", "COMMANDERS"), "CHI": ("#0B162A", "#C83803", "BEARS"),
    "DET": ("#0076B6", "#B0B7BC", "LIONS"), "GB": ("#203731", "#FFB612", "PACKERS"), "MIN": ("#4F2683", "#FFC62F", "VIKINGS"),
    "ATL": ("#A71930", "#111111", "FALCONS"), "CAR": ("#0085CA", "#101820", "PANTHERS"), "NO": ("#101820", "#D3BC8D", "SAINTS"),
    "TB": ("#D50A0A", "#34302B", "BUCCANEERS"), "ARI": ("#97233F", "#111111", "CARDINALS"), "LA": ("#003594", "#FFA300", "RAMS"),
    "SF": ("#AA0000", "#B3995D", "49ERS"), "SEA": ("#002244", "#69BE28", "SEAHAWKS"),
}
GROUP_NAME = {"QB": "quarterbacks", "RB": "running backs", "WR": "wide receivers", "TE": "tight ends", "OL": "offensive linemen",
              "DL": "pass rushers", "LB": "linebackers", "DB": "defensive backs"}
GROUP_ORDER = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB"]


SINGULAR = {"passing yards": "passing yard", "yards from scrimmage": "yard from scrimmage", "receiving yards": "receiving yard",
            "snaps": "snap", "pressures": "pressure", "tackles": "tackle", "passes defended": "pass defended"}


def big_txt(c):
    return f"{c['big']:g} {SINGULAR.get(c['big_label'], c['big_label']) if c['big'] == 1 else c['big_label']}"


def pl(n, one, many):
    return f"{n:g} {one if n == 1 else many}"


def team_name(tname):
    return tname.title().replace("49Ers", "49ers")


def slugs_for(cards):
    base = {}
    for c in cards:
        base.setdefault(card_slug(c["name"]), []).append(c)
    out = {}
    for s, who in base.items():
        for c in who:
            if len(who) == 1 or (c["team"] == "BUF" and sum(w["team"] == "BUF" for w in who) == 1):
                out[c["id"]] = s
            else:
                out[c["id"]] = f"{s}-{c['team'].lower()}-{c['grp'].lower()}"
    assert len(set(out.values())) == len(out), "NFL card URL collision"
    return out


def pos_label(c):
    from src.reports.nfl_cards import POS_NAME
    return "Edge rusher" if c.get("edge") else POS_NAME.get(c["pos"], c["pos"])


def small_stats(c, lg):
    g = c["grp"]
    if g == "QB":
        pa = f"{c['epa_db']:+.2f}" if c["epa_db"] is not None else "&ndash;"
        return [(c["gp"], "Games"), (f"{c['pass_td']}-{c['ints']}", "TD-INT"), (pa, "Points added per dropback")]
    if g == "RB":
        ypc = f"{c['rush_yds'] / c['car']:.1f}" if c["car"] else "&ndash;"
        return [(c["gp"], "Games"), (ypc, "Yards per carry"), (c["rush_td"] + c["rec_td"], "Touchdowns")]
    if g in ("WR", "TE"):
        return [(c["gp"], "Games"), (f"{c['rec']}/{c['tgt']}", "Catches/targets"), (c["rec_td"], "Touchdowns")]
    if g == "OL":
        return [(c["gp"], "Games"), (f"{c['snap_pct']:.0%}", "Snap share"), (c["penalties"], "Penalties")]
    if g == "DL":
        return [(c["gp"], "Games"), (f"{c['sacks']:g}", "Sacks"), (c["tackles"], "Tackles")]
    if g == "LB":
        return [(c["gp"], "Games"), (c["tfl"], "Tackles for loss"), (f"{c['sacks']:g}", "Sacks")]
    return [(c["gp"], "Games"), (c["def_int"], "Interceptions"), (c["tackles"], "Tackles")]


def history(c):
    g, rows = c["grp"], c["seasons"]
    if g == "QB":
        head, f = ["Season", "Team", "G", "Pass yds", "TD", "INT", "Rush yds"], lambda r: [r["pass_yds"], r["pass_td"], r["ints"], r["rush_yds"]]
    elif g == "RB":
        head, f = ["Season", "Team", "G", "Rush yds", "Rec yds", "TD"], lambda r: [r["rush_yds"], r["rec_yds"], r["rush_td"] + r["rec_td"]]
    elif g in ("WR", "TE"):
        head, f = ["Season", "Team", "G", "Catches", "Yds", "TD"], lambda r: [r["rec"], r["rec_yds"], r["rec_td"]]
    elif g == "OL":
        return "<p>Offensive linemen don't get individual credit for blocks or sacks allowed in the public data, so this card shows playing time and penalties only.</p>"
    else:
        head, f = ["Season", "Team", "G", "Tackles", "Sacks", "INT", "PD"], lambda r: [r["tackles"], f"{r['sacks']:g}", r["def_int"], r["pd"]]
    if not rows:
        return "<p>No earlier NFL seasons in our data (2018 on).</p>"
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in [r["season"], r["team"], r["gp"], *f(r)]) + "</tr>" for r in rows)
    return "<table><tr>" + "".join(f"<th>{h}</th>" for h in head) + f"</tr>{body}</table>"


def season_line(c):
    g = c["grp"]
    yd = lambda n: pl(n, "yard", "yards")
    car = pl(c["car"], "carry", "carries")
    if g == "QB":
        return (f"{c['cmp']} of {c['att']} passing for {yd(c['pass_yds'])}, {plural(c['pass_td'], 'touchdown')}, "
                f"{plural(c['ints'], 'interception')}; sacked {plural(c['sacked'], 'time')}; {car} for {yd(c['rush_yds'])}. "
                f"{plural(c['n_db'], 'dropback')} (passes, sacks and scrambles).")
    if g == "RB":
        return (f"{car} for {yd(c['rush_yds'])} and {plural(c['rush_td'], 'touchdown')}; "
                f"{pl(c['rec'], 'catch', 'catches')} on {plural(c['tgt'], 'target')} for {yd(c['rec_yds'])}. {plural(c['fum_lost'], 'fumble')} lost.")
    if g in ("WR", "TE"):
        return (f"{pl(c['rec'], 'catch', 'catches')} on {plural(c['tgt'], 'target')} for {yd(c['rec_yds'])} and {plural(c['rec_td'], 'touchdown')}. "
                f"{plural(c['fum_lost'], 'fumble')} lost.")
    if g == "OL":
        return (f"{plural(c['snaps'], 'snap')} ({c['snap_pct']:.0%} of his team's plays in the games he played); "
                f"{pl(c['penalties'], 'penalty', 'penalties')} called on him.")
    cov = (f" In coverage he's been thrown at {plural(c['cov_tgt'], 'time')}, allowing {pl(c['cov_cmp'], 'catch', 'catches')} for {yd(c['cov_yds'])}."
           if g == "DB" and c["cov_tgt"] else "")
    return (f"{plural(c['tackles'], 'tackle')} ({c['tfl']} for a loss), {pl(c['sacks'], 'sack', 'sacks')}, {plural(c['def_int'], 'interception')}, "
            f"{pl(c['pd'], 'pass defended', 'passes defended')}, {pl(c['ff'], 'forced fumble', 'forced fumbles')}. From game charting: "
            f"{plural(c['pressures'], 'pressure')} on the quarterback and {plural(c['missed_tk'], 'missed tackle')}.{cov}")


def rank_text(c, m):
    if c["rk"] is None:
        if c["grp"] == "OL":
            return "no rating for linemen"
        need = f"{m['min_db']} dropbacks" if c["grp"] == "QB" else f"{m['min_gp']} games"
        return f"not ranked yet: fewer than {need}"
    return f"<b>{ordn_txt(c['rk'])} of {c['of']}</b> {GROUP_NAME[c['grp']]} in {c['rank_what']}"


def tile(c, m):
    tc, ta, tname = NFL_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
    sm = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in small_stats(c, m["lg"]))
    return f"""<label class="gc" style="--tc:{tc};--ta:{ta}"><input type="checkbox"><div class="gci">
<div class="gf"><div class="gtop"><div class="tm">{tname}<br>{m['season']}</div><div class="no">{'' if c['number'] is None else c['number']}</div></div>
<div class="gname">{html.escape(c['name'])}</div><div class="gpos">{pos_label(c)}</div>
<div class="gbig"><div class="v">{c['big']:g}</div><div class="l">{big_txt(c).split(' ', 1)[1]}<br>{rank_text(c, m)}</div></div>
<div class="grow">{sm}</div>
<div class="gspark">{spark_svg(c['spark'], tc, c['big_label'].capitalize() + ", running total")}<small>{c['big_label'].capitalize()}, running total, game by game</small></div>
{'<div class="gsmall">SMALL SAMPLE</div>' if c['small'] else ''}<div class="gflip">TAP TO FLIP &#8635;</div></div>
<div class="gb"><h4>{html.escape(c['name'])}</h4>{history(c)}<p><b>This season:</b> {season_line(c)}</p></div></div></label>"""


def howto(m):
    lg = m["lg"]
    pfr_note = f", which runs through Week {m['pfr_week']}" if m["pfr_week"] < m["week"] else ""
    return f"""<h2>How to read an NFL card</h2>
<p><b>The big number</b> is the stat that matters most for the position: passing yards for quarterbacks, yards from scrimmage (rushing plus
receiving) for running backs, receiving yards for receivers and tight ends, pressures on the quarterback for pass rushers, tackles for
linebackers, and passes defended for defensive backs. The rank compares him per game with everyone at his position who has played at
least {m['min_gp']} games.</p>
<p><b>Quarterbacks are ranked on points added per dropback.</b> Every play changes how many points a team can expect to score on that drive,
based on down, distance and field position. A 15-yard completion on 3rd and 10 adds a lot; a sack loses some. Add that up over every
dropback (passes, sacks and scrambles) and divide: across every dropback in the league this season it's {lg['QB_all']:+.2f}. Quarterbacks need {m['min_db']}
dropbacks to be ranked.</p>
<p><b>Pass rushers</b> include defensive linemen and the edge rushers listed as linebackers: a linebacker with at least one pressure and fewer
than five tackles a game is carded with the pass rushers. <b>Pressures</b> (sacks, hits and hurries on the quarterback) come from
Pro Football Reference's game charting{pfr_note}. Sacks are the official count, so they can differ slightly from the charting.</p>
<p><b>Offensive linemen</b> get playing time and penalties only: the public data doesn't credit individual linemen for blocks or sacks allowed.</p>
<p><b>The source:</b> nflverse's weekly player stats, snap counts and play-by-play, and Pro Football Reference charting, regular season only,
through Week {m['week']}. Stats are season totals; a player who changed teams sits with the team he played for most recently. Cards marked
<b>small sample</b> have fewer than {m['min_gp']} games (or {m['min_db']} dropbacks for a quarterback). Not affiliated with the NFL or any
team; card designs are our own.</p>"""


def build_nfl_cards():
    src = ROOT / "reports" / "cards" / "nfl_players.json"
    if not src.exists():
        return None
    d = json.loads(src.read_text())
    m, cards = d["meta"], d["cards"]
    out = SITE / "cards" / "nfl"
    out.mkdir(parents=True, exist_ok=True)
    slugs = slugs_for(cards)
    groups = {}
    for c in cards:
        tc, ta, tname = NFL_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
        moved = f" He also played for {', '.join(c['other_teams'])} this season; the card counts his whole season." if c["other_teams"] else ""
        body = f"""<div class="kicker"><a href="index.html">NFL player cards</a> &middot; {team_name(tname)}</div><h1>{html.escape(c['name'])}</h1>
<p class="dek">{pos_label(c)}, {team_name(tname)}. {big_txt(c)} in {plural(c['gp'], 'game')}. Numbers through Week {m['week']} of the {m['season']} season.{moved}</p>
<div class="cards one">{tile(c, m)}</div>
<h2>This season</h2><p>{season_line(c)}</p>
{'<p><b>Small sample.</b> These numbers can move a lot.</p>' if c['small'] else ''}
{howto(m)}"""
        (out / f"{slugs[c['id']]}.html").write_text(page(f"{c['name']} | NFL player card | Buffalo Quant Desk", body, "Cards", 2,
                                                       f"{c['name']}, {pos_label(c)}, {team_name(tname)}: {big_txt(c)} this season."))
        key = ("0" if c["team"] == "BUF" else "1" + tname, GROUP_ORDER.index(c["grp"]))
        groups.setdefault(key, (team_name(tname), c["grp"], []))[2].append(
            (-c["big"], f'<a class="pcard" href="{slugs[c["id"]]}.html" style="--tc:{tc};--ta:{ta}"><span class="pn">{"" if c["number"] is None else c["number"]}</span>'
                        f'<span class="pm"><b>{html.escape(c["name"])}</b><br>{pos_label(c)} &middot; {big_txt(c)}</span></a>'))
    teams, lists, seen = [], "", set()
    for key in sorted(groups):
        tn, grp, items = groups[key]
        if tn not in teams:
            teams.append(tn)
        idattr = f' id="{card_slug(tn)}"' if tn not in seen else ""
        seen.add(tn)
        lists += f'<h2{idattr} class="tgrp">{tn} {GROUP_NAME[grp]}</h2><div class="plist">{"".join(h for _, h in sorted(items, key=lambda x: x[0]))}</div>'
    nav = " &middot; ".join(f'<a href="#{card_slug(t)}">{t}</a>' for t in teams)
    search = ('<p><input id="cardq" type="search" placeholder="Find a player" aria-label="Find a player" '
              'style="width:100%;max-width:420px;padding:10px 12px;font-size:16px;border:1px solid #C9CDD4;border-radius:8px"></p>'
              '<script>document.getElementById("cardq").addEventListener("input",function(e){var q=e.target.value.toLowerCase();'
              'document.querySelectorAll(".pcard").forEach(function(a){a.style.display=a.textContent.toLowerCase().indexOf(q)>-1?"":"none"});'
              'document.querySelectorAll(".plist").forEach(function(l){var v=[].some.call(l.children,function(a){return a.style.display!=="none"});'
              'l.style.display=v?"":"none";l.previousElementSibling.style.display=v?"":"none"})});</script>')
    body = f"""<div class="kicker"><a href="../index.html">Player cards</a> &middot; NFL</div><h1>NFL player cards</h1>
<p class="dek">One card for every NFL player who has taken an offensive or defensive snap this season ({len(cards)} of them), through Week {m['week']}.
Bills first. <a href="../index.html">NHL cards are here.</a></p>{search}<p class="small">{nav}</p>{lists}"""
    (out / "index.html").write_text(page("NFL player cards | Buffalo Quant Desk", body, "Cards", 2,
                                         "A card for every NFL player this season: the stat that matters for his position, his rank, and his history."))
    return m["week"]
