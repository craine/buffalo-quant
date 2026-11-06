"""Static site -> site/. Cloudflare Pages serves site/ as-is (no build command).

Content comes only from committed files: reports/*.md + PNGs and ledger/*.csv.
"""
import html
import re
import shutil
from datetime import datetime, timezone

import markdown
import pandas as pd

from src.db import ROOT
from src.ledger.ledger import GRADE_COLS, GRADE_CSV, PRED_COLS, PRED_CSV, _read

SITE = ROOT / "site"
DOMAIN = "https://buffaloquant.com"
ARTICLES = [  # newest first: (slug, report file, date, kicker, dek, hero image)
    ("josh-allen-2018-to-now", "2026-josh-allen.md", "2026-11-05", "Bills &middot; Josh Allen",
     "Nine seasons, four play-callers, every dropback. He's the most efficient passer in football, and he's winning off script.",
     "allen-seasons.png"),
    ("bills-defense-fixed", "2026-defense-baseline.md", "2026-11-05", "Bills &middot; Defense",
     "The run defense improved. The pass defense collapsed. Seven games of evidence, opponent-adjusted.",
     "defense-rank-shift.png"),
]

CSS = """
:root{--navy:#00338D;--red:#C60C30;--ink:#14171F;--muted:#5B6270;--line:#E3E6EB;--bg:#FBFBF9;--card:#fff}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
a{color:var(--navy)}a:hover{color:var(--red)}
.wrap{max-width:860px;margin:0 auto;padding:0 22px}
header.site{border-bottom:4px solid var(--navy);background:#fff}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:68px;gap:16px}
.mark{font-weight:900;letter-spacing:.14em;font-size:15px;text-decoration:none;color:var(--ink);white-space:nowrap}
.mark b{color:var(--red)}
nav a{margin-left:22px;text-decoration:none;font-weight:600;font-size:15px;color:var(--ink)}
nav a.on{color:var(--red)}
.kicker{font-size:12px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--red);margin:44px 0 8px}
h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(32px,5vw,48px);line-height:1.1;margin:0 0 14px;letter-spacing:-.01em}
h2{font-family:Georgia,serif;font-size:26px;margin:40px 0 10px}
.dek{font-size:20px;color:var(--muted);margin:0 0 24px}
.meta{font-size:13px;color:var(--muted);margin-bottom:28px}
img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:15px;margin:14px 0 22px;background:#fff}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
td:not(:first-child),th:not(:first-child){font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:22px 24px;margin:22px 0}
.card h3{margin:0 0 6px;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--navy)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:18px 0}
.stat{background:#fff;border:1px solid var(--line);border-radius:8px;padding:16px}
.stat .n{font-size:34px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.stat .l{font-size:13px;color:var(--muted);margin-top:6px}
.rules{padding-left:20px}.rules li{margin:6px 0}
.hit{color:#0A7A3E;font-weight:700}.miss{color:var(--red);font-weight:700}.open{color:var(--muted)}
blockquote{margin:18px 0;padding:4px 0 4px 18px;border-left:4px solid var(--red);font-size:19px}
footer{border-top:1px solid var(--line);margin-top:70px;padding:26px 0 40px;font-size:13px;color:var(--muted)}
@media(max-width:600px){header.site .wrap{flex-direction:column;align-items:flex-start;justify-content:center;height:auto;padding-top:12px;padding-bottom:10px;gap:6px}nav a{margin:0 16px 0 0;font-size:14px}.mark{font-size:14px}}
"""

NAV = [("index.html", "Home"), ("analysis/", "Analysis"), ("ledger.html", "Ledger"), ("about.html", "About")]


def page(title, body, active, depth=0, desc="Buffalo Bills and Sabres analytics with receipts.", og="allen-seasons.png"):
    up = "../" * depth
    links = "".join(f'<a href="{up}{h}" class="{"on" if n == active else ""}">{n}</a>' for h, n in NAV)
    t = html.escape(title)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title><meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{DOMAIN}/analysis/{og}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}favicon.svg"><link rel="stylesheet" href="{up}style.css"></head><body>
<header class="site"><div class="wrap"><a class="mark" href="{up}index.html">BUFFALO <b>QUANT</b> DESK</a><nav>{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Buffalo Quant Desk. Every number is computed from public play-by-play
(nflverse). Analysis, not wagering advice. Not affiliated with the Buffalo Bills,
Buffalo Sabres, or the NFL.</div></footer></body></html>"""


def md_to_html(text):
    h = markdown.markdown(text, extensions=["tables"])
    return h.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")


def ledger_rows():
    p, g = _read(PRED_CSV, PRED_COLS), _read(GRADE_CSV, GRADE_COLS)
    if p.empty:
        return p, None
    m = p.merge(g, left_on="id", right_on="prediction_id", how="left")
    return m, g


def build_ledger():
    m, g = ledger_rows()
    if m.empty:
        stats = ('<div class="stats"><div class="stat"><div class="n">0</div><div class="l">calls logged</div></div>'
                 '<div class="stat"><div class="n">0</div><div class="l">graded</div></div>'
                 '<div class="stat"><div class="n">&ndash;</div><div class="l">Brier score (lower is better)</div></div></div>')
        table = ('<div class="card"><h3>First card</h3>The first calls are logged before kickoff of '
                 'Bills at Vikings, Monday Night Football, November 9. They appear here the moment they are logged.</div>')
    else:
        graded = m[m.outcome.notna() & (m.outcome != "")]
        brier = f"{graded.brier.astype(float).mean():.3f}" if len(graded) else "&ndash;"
        stats = (f'<div class="stats"><div class="stat"><div class="n">{len(m)}</div><div class="l">calls logged</div></div>'
                 f'<div class="stat"><div class="n">{len(graded)}</div><div class="l">graded</div></div>'
                 f'<div class="stat"><div class="n">{brier}</div><div class="l">Brier score (coin flip = 0.250)</div></div></div>')
        rows = []
        for r in m.itertuples():
            if isinstance(r.outcome, str) and r.outcome != "":
                res = '<span class="hit">Hit</span>' if (float(r.probability) >= .5) == (r.outcome == "1") else '<span class="miss">Miss</span>'
                res += f" &middot; {html.escape(str(r.actual_value))}"
            else:
                res = '<span class="open">Open</span>'
            rows.append(f"<tr><td>{r.id}</td><td>{html.escape(r.claim_text)}<br><small>{r.game_id} &middot; logged {r.created_at_utc}</small></td>"
                        f"<td>{float(r.probability):.0%}</td><td>{res}</td></tr>")
        table = ('<div class="tablewrap"><table><tr><th>ID</th><th>Call</th><th>Prob.</th><th>Result</th></tr>'
                 + "".join(rows) + "</table></div>")
    body = f"""<div class="kicker">The Ledger</div><h1>Every call. Every miss. Forever.</h1>
<p class="dek">Each prediction is logged with a probability and a timestamp before kickoff, then graded
from the play-by-play. Nothing is deleted or edited.</p>{stats}{table}
<h2>How grading works</h2><ul class="rules">
<li><b>Before kickoff or it doesn't count.</b> The system rejects any call logged after the game starts.</li>
<li><b>Probabilities, not hot takes.</b> A 70% call should hit about 70% of the time. Calibration is the score.</li>
<li><b>Brier score</b> = (probability &minus; outcome)&sup2;, averaged. 0 is perfect, 0.25 is a coin flip.</li>
<li><b>Benchmarks</b> are a naive baseline and public models. Never betting lines.</li>
<li><b>Append-only.</b> Corrections are new rows that reference the old one. The full record is downloadable as <a href="ledger/predictions.csv">CSV</a>.</li></ul>"""
    (SITE / "ledger.html").write_text(page("The Ledger | Buffalo Quant Desk", body, "Ledger"))


def build_articles():
    out = SITE / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    cards = []
    for slug, src, date, kicker, dek, hero in ARTICLES:
        text = (ROOT / "reports" / src).read_text()
        title = re.match(r"# (.+)", text).group(1)
        text = re.sub(r"^# .+\n", "", text, count=1)
        for img in re.findall(r"\]\(([^)]+\.png)\)", text):
            shutil.copy(ROOT / "reports" / img, out / img)
        when = datetime.strptime(date, "%Y-%m-%d").strftime("%B %-d, %Y")
        body = (f'<div class="kicker">{kicker}</div><h1>{html.escape(title)}</h1>'
                f'<p class="dek">{html.escape(dek)}</p><div class="meta">{when} &middot; Buffalo Quant Desk</div>'
                + md_to_html(text))
        (out / f"{slug}.html").write_text(page(f"{title} | Buffalo Quant Desk", body, "Analysis", 1, dek, hero))
        cards.append(f'<div class="card"><h3>{when}</h3><a href="{slug}.html"><b>{html.escape(title)}</b></a><br>{html.escape(dek)}</div>')
    idx = '<div class="kicker">Analysis</div><h1>The work</h1>' + "".join(cards)
    (out / "index.html").write_text(page("Analysis | Buffalo Quant Desk", idx, "Analysis", 1))
    return ARTICLES, {a[0]: (ROOT / "reports" / a[1]).read_text() for a in ARTICLES}


def build_home(articles, texts):
    slug, _, date, kicker, dek, hero = articles[0]
    text = texts[slug]
    title = re.match(r"# (.+)", text).group(1)
    finding = re.search(r"\*\*Finding: (.+?)\*\*", text, re.S).group(1).replace("\n", " ")
    more = "".join(f'<li><a href="analysis/{a[0]}.html">{html.escape(re.match(r"# (.+)", texts[a[0]]).group(1))}</a></li>' for a in articles[1:])
    body = f"""<div class="kicker">Buffalo sports, by the numbers</div>
<h1>The quant desk for the Bills and Sabres.</h1>
<p class="dek">Predictive analysis built on every play, with a public, graded record of every call we make.</p>
<div class="card"><h3>Latest</h3><a href="analysis/{slug}.html"><b>{html.escape(title)}</b></a>
<blockquote>{html.escape(finding)}</blockquote>
<a href="analysis/{slug}.html"><img src="analysis/{hero}" alt="{html.escape(title)}"></a>
{f'<p><b>Also:</b></p><ul class="rules">{more}</ul>' if more else ''}</div>
<div class="card"><h3>The Ledger</h3>Every prediction is timestamped before kickoff and graded after.
First card: <b>Bills at Vikings, Monday Night Football</b>. <a href="ledger.html">See the record &rarr;</a></div>
<h2>The rules</h2><ul class="rules">
<li><b>Receipts.</b> Every call is logged before kickoff and graded in public. Misses stay up.</li>
<li><b>Predictive over descriptive.</b> What happens next, and why.</li>
<li><b>Plain English.</b> One sentence you can repeat, one chart you can read.</li>
<li><b>Traceable.</b> Every number is computed from public play-by-play, and every method is written down.</li>
<li><b>No betting content.</b> This is analysis. No odds, no picks, no lines.</li></ul>"""
    (SITE / "index.html").write_text(page("Buffalo Quant Desk | Bills and Sabres analytics", body, "Home"))


def build_about():
    body = """<div class="kicker">About</div><h1>Buffalo's quant desk.</h1>
<p class="dek">Built by a data scientist and lifelong Buffalo fan, using the same methods
behind systematic trading models and competitive machine learning.</p>
<p>Most sports coverage tells you what happened. We try to tell you what happens next, attach a
probability to it, and show our work. Every number on this site is computed from public
play-by-play data, with the method published alongside it. Every prediction lives on the <a href="ledger.html">Ledger</a>,
graded in public.</p>
<h2>What we cover</h2><ul class="rules"><li><b>Bills:</b> weekly post-game reports, Thursday previews with logged calls, coaching and roster deep dives.</li>
<li><b>Sabres:</b> coming this season, built on our own expected-goals model.</li></ul>
<h2>What we don't do</h2><p>Betting content. No odds, lines, picks or units. Projections are analysis, not wagering advice.</p>
<h2>Media</h2><p>Available for radio, podcast and TV segments on the Bills and Sabres.</p>"""
    (SITE / "about.html").write_text(page("About | Buffalo Quant Desk", body, "About"))


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "style.css").write_text(CSS)
    (SITE / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#00338D"/>'
                                      '<path d="M8 22h4V14H8zm6 0h4V9h-4zm6 0h4v-5h-4z" fill="#fff"/><rect x="7" y="24" width="18" height="2" fill="#C60C30"/></svg>')
    articles, texts = build_articles()
    build_home(articles, texts)
    build_ledger()
    build_about()
    (SITE / "ledger").mkdir(exist_ok=True)
    for f in (PRED_CSV, GRADE_CSV):
        if f.exists():
            shutil.copy(f, SITE / "ledger" / f.name)
        else:
            (SITE / "ledger" / f.name).write_text(",".join(PRED_COLS if f == PRED_CSV else GRADE_COLS) + "\n")
    (SITE / "404.html").write_text(page("Not found | Buffalo Quant Desk", '<h1 style="margin-top:50px">Not found.</h1><p><a href="/">Home</a></p>', ""))
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    urls = ["", "analysis/", "ledger.html", "about.html"] + [f"analysis/{a[0]}.html" for a in ARTICLES]
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{DOMAIN}/{u}</loc></url>" for u in urls) + "</urlset>")
    print("site built:", sorted(str(p.relative_to(SITE)) for p in SITE.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
