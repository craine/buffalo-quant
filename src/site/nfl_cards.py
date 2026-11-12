"""NFL player card pages: site/cards/nfl/<slug>.html and site/cards/nfl/index.html, from reports/cards/nfl_players.json."""
import html
import json
from datetime import datetime

from src.db import ROOT
from src.site.build import SITE, card_slug, ordn_txt, page, spark_svg

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
GROUP_NAME = {"QB": "quarterbacks", "RB": "running backs", "FB": "fullbacks", "WR": "wide receivers", "TE": "tight ends",
              "OL": "offensive linemen", "DL": "pass rushers", "LB": "linebackers", "CB": "cornerbacks", "S": "safeties"}
GROUP_ORDER = ["QB", "RB", "FB", "WR", "TE", "OL", "DL", "LB", "CB", "S"]
SINGULAR = {"passing yards": "passing yard", "yards from scrimmage": "yard from scrimmage", "receiving yards": "receiving yard",
            "snaps": "snap", "pressures": "pressure", "tackles": "tackle", "passes defended": "pass defended"}


def num(n):
    """1,234 for whole numbers; 7.5 for half sacks."""
    return f"{n:,.0f}" if float(n).is_integer() else f"{n:,.1f}"


def pl(n, one, many):
    return f"{num(n)} {one if n == 1 else many}"


def big_label(c):
    return SINGULAR.get(c["big_label"], c["big_label"]) if c["big"] == 1 else c["big_label"]


def big_txt(c):
    return f"{num(c['big'])} {big_label(c)}"


def team_name(code):
    return NFL_COLORS.get(code, ("", "", code))[2].title().replace("49Ers", "49ers")


def slugs_for(cards):
    """Stable URLs: the name, or name + position when two players share a name, or + id as a last resort. No team or group in it."""
    base = {}
    for c in cards:
        base.setdefault(card_slug(c["name"]), []).append(c)
    out = {}
    for s, who in base.items():
        if len(who) == 1:
            out[who[0]["id"]] = s
            continue
        by_pos = {}
        for c in who:
            by_pos.setdefault(f"{s}-{c['pos'].lower()}", []).append(c)
        for sp, cs in by_pos.items():
            for c in cs:
                out[c["id"]] = sp if len(cs) == 1 else f"{sp}-{c['id'][-4:]}"
    assert len(set(out.values())) == len(out), "NFL card URL collision"
    return out


def pos_label(c):
    from src.reports.nfl_cards import POS_NAME
    return "Edge rusher" if c.get("edge") else POS_NAME.get(c["pos"], c["pos"])


def small_stats(c):
    g, games = c["grp"], (c["gp"], "Game" if c["gp"] == 1 else "Games")
    if g == "QB":
        pa = f"{c['epa_db']:+.2f}" if c["epa_db"] is not None else "&ndash;"
        return [games, (f"{c['pass_td']}-{c['ints']}", "TD-INT"), (pa, "Points added per dropback")]
    if g in ("RB", "FB"):
        td = c["rush_td"] + c["rec_td"]
        return [games, (f"{c['rush_yds'] / c['car']:.1f}" if c["car"] else "&ndash;", "Yards per carry"), (td, "Touchdown" if td == 1 else "Touchdowns")]
    if g in ("WR", "TE"):
        return [games, (f"{c['rec']}/{c['tgt']}", "Catches/targets"), (c["rec_td"], "Touchdown" if c["rec_td"] == 1 else "Touchdowns")]
    if g == "OL":
        return [games, (f"{c['snap_pct']:.0%}" if c["snap_pct"] is not None else "&ndash;", "Snap share"),
                (c["penalties"], "Penalty" if c["penalties"] == 1 else "Penalties")]
    if g == "DL":
        return [games, (num(c["sacks"]), "Sack" if c["sacks"] == 1 else "Sacks"), (c["tackles"], "Tackle" if c["tackles"] == 1 else "Tackles")]
    if g == "LB":
        return [games, (c["tfl"], "Tackles for loss"), (num(c["sacks"]), "Sack" if c["sacks"] == 1 else "Sacks")]
    if g == "S":
        return [games, (c["def_int"], "Interception" if c["def_int"] == 1 else "Interceptions"), (c["pd"], "Passes defended")]
    return [games, (c["def_int"], "Interception" if c["def_int"] == 1 else "Interceptions"), (c["tackles"], "Tackle" if c["tackles"] == 1 else "Tackles")]


def history(c, m):
    g, rows = c["grp"], c["seasons"]
    if g == "QB":
        head, f = ["Season", "Team", "G", "Pass yds", "TD", "INT"], lambda r: [num(r["pass_yds"]), r["pass_td"], r["ints"]]
    elif g in ("RB", "FB"):
        head, f = ["Season", "Team", "G", "Rush yds", "Rec yds", "TD"], lambda r: [num(r["rush_yds"]), num(r["rec_yds"]), r["rush_td"] + r["rec_td"]]
    elif g in ("WR", "TE"):
        head, f = ["Season", "Team", "G", "Catches", "Yds", "TD"], lambda r: [r["rec"], num(r["rec_yds"]), r["rec_td"]]
    elif g == "OL":
        head, f = ["Season", "Team", "Games"], lambda r: []
    else:
        head, f = ["Season", "Team", "G", "Tkl", "Sacks", "INT"], lambda r: [r["tackles"], num(r["sacks"]), r["def_int"]]
    body = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in [r["season"], r["team"], r["gp"], *f(r)]) + "</tr>" for r in rows)
    note = f"<p class=\"small\">NFL seasons from {m['hist_from']} on; {m['season']} through Week {m['week']}.</p>"
    return "<table><tr>" + "".join(f"<th>{h}</th>" for h in head) + f"</tr>{body}</table>{note}"


def season_line(c):
    g = c["grp"]
    yd = lambda n: pl(n, "yard", "yards")
    car = pl(c["car"], "carry", "carries")
    td = lambda n: pl(n, "touchdown", "touchdowns")
    if g == "QB":
        if not (c["att"] or c["car"] or c["sacked"]):
            return f"Played {pl(c['gp'], 'game', 'games')} but hasn't thrown a pass or run the ball this season."
        return (f"{c['cmp']} of {c['att']} passing for {yd(c['pass_yds'])}, {td(c['pass_td'])}, "
                f"{pl(c['ints'], 'interception', 'interceptions')}; sacked {pl(c['sacked'], 'time', 'times')}; {car} for {yd(c['rush_yds'])}"
                f"{', ' + td(c['rush_td']) if c['rush_td'] else ''}. {pl(c['n_db'], 'dropback', 'dropbacks')} (passes, sacks and scrambles).")
    off = ""
    if g in ("RB", "FB", "WR", "TE"):
        if not (c["car"] or c["tgt"]):
            return f"Played {pl(c['gp'], 'game', 'games')} but hasn't had a carry or a target this season."
        run = f"{car} for {yd(c['rush_yds'])} and {td(c['rush_td'])}; " if c["car"] else ""
        dfn = (f" On defense: {pl(c['tackles'], 'tackle', 'tackles')}, {pl(c['def_int'], 'interception', 'interceptions')}, "
               f"{pl(c['pd'], 'pass defended', 'passes defended')}." if c["def_int"] or c["pd"] or c["tackles"] >= 3 else "")
        return (f"{run}{pl(c['rec'], 'catch', 'catches')} on {pl(c['tgt'], 'target', 'targets')} for {yd(c['rec_yds'])}"
                f"{' and ' + td(c['rec_td']) if c['rec_td'] or not c['car'] else ''}. {pl(c['fum_lost'], 'fumble', 'fumbles')} lost.{dfn}")
    if g == "OL":
        share = f" ({c['snap_pct']:.0%} of his team's plays in the games he played)" if c["snap_pct"] is not None else ""
        return f"{pl(c['snaps'], 'snap', 'snaps')}{share}; {pl(c['penalties'], 'penalty', 'penalties')} called on him."
    if c["rec"] or c["car"]:
        off = f" On offense: {pl(c['rec'], 'catch', 'catches')} for {yd(c['rec_yds'])}" + (f", {car} for {yd(c['rush_yds'])}" if c["car"] else "") + "."
    cov = (f" In coverage he's been thrown at {pl(c['cov_tgt'], 'time', 'times')}, allowing {pl(c['cov_cmp'], 'catch', 'catches')} for {yd(c['cov_yds'])}."
           if g in ("CB", "S") and c["cov_tgt"] else "")
    dtd = f", {pl(c['def_td'], 'defensive touchdown', 'defensive touchdowns')}" if c["def_td"] else ""
    return (f"{pl(c['tackles'], 'tackle', 'tackles')} ({c['tfl']} for a loss), {pl(c['sacks'], 'sack', 'sacks')}, "
            f"{pl(c['def_int'], 'interception', 'interceptions')}, {pl(c['pd'], 'pass defended', 'passes defended')} (interceptions included), "
            f"{pl(c['ff'], 'forced fumble', 'forced fumbles')}{dtd}. From game charting: {pl(c['pressures'], 'pressure', 'pressures')} on the "
            f"quarterback and {pl(c['missed_tk'], 'missed tackle', 'missed tackles')}.{cov}{off}")


def rank_text(c, m):
    if c["rk"] is None:
        if c["grp"] == "OL":
            return "no ranking for linemen"
        if c["grp"] == "FB":
            return "fullbacks aren't ranked"
        need = f"{m['min_db']} dropbacks" if c["grp"] == "QB" else f"{m['min_gp']} games played"
        return f"not ranked: fewer than {need}"
    val = f" ({c['epa_db']:+.2f})" if c["grp"] == "QB" else ""
    return f"<b>{ordn_txt(c['rk'])} of {c['of']}</b> {GROUP_NAME[c['grp']]} in {c['rank_what']}{val}"


def league_line(c, m):
    g = c["grp"]
    if g not in m["lg"] or c["rk"] is None:
        return ""
    if g == "QB":
        return f"League average: {m['lg']['QB_all']:+.2f} points added per dropback."
    per = c["big"] / (c["gp_pfr"] if g == "DL" else c["gp"]) if c["gp"] else 0
    return (f"He averages {per:,.1f} {c['rank_what'].replace(' per game', '')} a game; the average for ranked {GROUP_NAME[g]} is "
            f"{m['lg'][g]:,.1f}.")


def tile(c, m):
    tc, ta, tname = NFL_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
    sm = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in small_stats(c))
    return f"""<label class="gc" style="--tc:{tc};--ta:{ta}"><input type="checkbox"><div class="gci">
<div class="gf"><div class="gtop"><div class="tm">{tname}<br>{m['season']}</div><div class="no">{'' if c['number'] is None else c['number']}</div></div>
<div class="gname">{html.escape(c['name'])}</div><div class="gpos">{pos_label(c)}</div>
<div class="gbig"><div class="v">{num(c['big'])}</div><div class="l">{big_label(c)}<br>{rank_text(c, m)}</div></div>
<div class="grow">{sm}</div>
<div class="gspark">{spark_svg(c['spark'], tc, c['big_label'].capitalize() + ", running total")}<small>Running total, game by game</small></div>
{'<div class="gsmall">SMALL SAMPLE</div>' if c['small'] else ''}<div class="gflip">TAP TO FLIP &#8635;</div></div>
<div class="gb" style="overflow-y:auto"><h4>{html.escape(c['name'])}</h4>{history(c, m)}</div></div></label>"""


def howto(m):
    lg = m["lg"]
    pfr_note = f" (through Week {m['pfr_week']})" if m["pfr_week"] < m["week"] else ""
    return f"""<h2>How to read an NFL card</h2>
<p><b>The big number</b> is the stat that matters most for the position: passing yards for quarterbacks, yards from scrimmage (rushing plus
receiving) for running backs, receiving yards for receivers and tight ends, pressures on the quarterback for pass rushers, tackles for
linebackers and safeties, and passes defended (interceptions included) for cornerbacks. The rank compares him per game with everyone at his
position who has played at least {m['min_gp']} games. Games include games he played only on special teams.</p>
<p><b>Quarterbacks are ranked on points added per dropback.</b> Every play changes how many points a team can expect to score on that drive,
based on down, distance and field position. A 15-yard completion on 3rd and 10 adds a lot; a sack loses some. Add that up over every
dropback (passes, sacks and scrambles) and divide: across every dropback in the league this season it's {lg['QB_all']:+.2f}. Quarterbacks
need {m['min_db']} dropbacks to be ranked.</p>
<p><b>Pass rushers</b> are defensive linemen plus the linebackers who mainly rush the passer: at least {m['edge_press']:g} pressure and fewer
than {m['edge_tackles']:g} tackles a game. <b>Pressures</b> (sacks, hits and hurries on the quarterback) come from Pro Football Reference's
game charting{pfr_note}. Sacks and tackles are the official counts, so they can differ a little from the charting.</p>
<p><b>Offensive linemen</b> get playing time and penalties only: the public data doesn't credit individual linemen for blocks or sacks
allowed. Fullbacks aren't ranked.</p>
<p><b>The source:</b> nflverse's weekly player stats, snap counts and play-by-play, and Pro Football Reference charting, regular season only.
Numbers are season totals. The team shown is the one he last played for; it doesn't track trades or releases after his last game.
Cards marked <b>small sample</b> have fewer than {m['min_gp']} games (or {m['min_db']} dropbacks for a quarterback). Not affiliated with
the NFL or any team; card designs are our own.</p>"""


def build_nfl_cards():
    src = ROOT / "reports" / "cards" / "nfl_players.json"
    if not src.exists():
        return None
    d = json.loads(src.read_text())
    m, cards = d["meta"], d["cards"]
    through = f"Week {m['week']} (games through {datetime.strptime(m['week_date'], '%Y-%m-%d'):%b. %-d, %Y})"
    out = SITE / "cards" / "nfl"
    out.mkdir(parents=True, exist_ok=True)
    slugs = slugs_for(cards)
    groups = {}
    for c in cards:
        tc, ta, _ = NFL_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
        tn = team_name(c["team"])
        notes = []
        if c["other_teams"]:
            notes.append(f"He also played for the {', '.join(team_name(t) for t in c['other_teams'])} this season; the card counts his whole season.")
        if c["last_week"] < m["week"]:
            notes.append(f"His last game was Week {c['last_week']}, for the {tn}.")
        ll = league_line(c, m)
        body = f"""<div class="kicker"><a href="index.html">NFL player cards</a> &middot; {tn}</div><h1>{html.escape(c['name'])}</h1>
<p class="dek">{pos_label(c)}, {tn}. {big_txt(c)} in {pl(c['gp'], 'game', 'games')}. Numbers through {through}.</p>
<div class="cards one">{tile(c, m)}</div>
<h2>This season</h2><p>{season_line(c)}</p>
{f'<p>{ll}</p>' if ll else ''}
{''.join(f'<p>{n}</p>' for n in notes)}
{'<p><b>Small sample.</b> These numbers can move a lot.</p>' if c['small'] else ''}
{howto(m)}"""
        (out / f"{slugs[c['id']]}.html").write_text(page(f"{c['name']} | NFL player card | Buffalo Quant Desk", body, "Cards", 2,
                                                       f"{c['name']}, {pos_label(c)}, {tn}: {big_txt(c)} this season."))
        key = ("0" if c["team"] == "BUF" else "1" + tn, GROUP_ORDER.index(c["grp"]))
        groups.setdefault(key, (tn, c["grp"], []))[2].append(
            (-c["big"], c["name"], f'<a class="pcard" href="{slugs[c["id"]]}.html" style="--tc:{tc};--ta:{ta}"><span class="pn">{"" if c["number"] is None else c["number"]}</span>'
                                   f'<span class="pm"><b>{html.escape(c["name"])}</b><br>{tn} &middot; {pos_label(c)} &middot; {big_txt(c)}</span></a>'))
    teams, lists, seen = [], "", set()
    for key in sorted(groups):
        tn, grp, items = groups[key]
        if tn not in teams:
            teams.append(tn)
        idattr = f' id="{card_slug(tn)}"' if tn not in seen else ""
        seen.add(tn)
        lists += f'<h2{idattr} class="tgrp">{tn} {GROUP_NAME[grp]}</h2><div class="plist">{"".join(h for *_, h in sorted(items))}</div>'
    nav = "".join(f'<a href="#{card_slug(t)}" style="display:inline-block;padding:8px 10px;min-height:32px">{t}</a>' for t in teams)
    search = ('<p><input id="cardq" type="search" placeholder="Find a player" aria-label="Find a player" '
              'style="width:100%;max-width:420px;padding:10px 12px;font-size:16px;border:1px solid #C9CDD4;border-radius:8px"></p>'
              '<script>document.getElementById("cardq").addEventListener("input",function(e){var q=e.target.value.toLowerCase();'
              'document.querySelectorAll(".pcard").forEach(function(a){a.style.display=a.textContent.toLowerCase().indexOf(q)>-1?"":"none"});'
              'document.querySelectorAll(".plist").forEach(function(l){var v=[].some.call(l.children,function(a){return a.style.display!=="none"});'
              'l.style.display=v?"":"none";l.previousElementSibling.style.display=v?"":"none"})});</script>')
    missing = len(m["unlinked"])
    cover = (f"One card for every NFL player who has taken an offensive or defensive snap this season ({len(cards):,} of them"
             + (f"; {missing} more we couldn't match to the league's stats" if missing else "") + ")")
    body = f"""<div class="kicker"><a href="../index.html">Player cards</a> &middot; NFL</div><h1>NFL player cards</h1>
<p class="dek">{cover}, through {through}. Bills first. <a href="../index.html">NHL cards are here.</a></p>{search}<p class="small">{nav}</p>{lists}"""
    (out / "index.html").write_text(page("NFL player cards | Buffalo Quant Desk", body, "Cards", 2,
                                         "A card for every NFL player this season: the stat that matters for his position, his rank, and his history."))
    return m["week"]
