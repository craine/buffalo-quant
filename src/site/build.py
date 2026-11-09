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
    ("sabres-vegas-postgame-nov-8", "2026-11-08-sabres-vgk.md", "2026-11-08", "Sabres &middot; Post-game",
     "Buffalo's chances were worth more than Vegas's. Adin Hill stopped 28 of 29 and had one of the league's best goalie nights. Our model leaned slightly to Vegas, a hit, but a near coin flip.",
     "sabres-vgk-post-flow.png"),
    ("bills-offense-vs-vikings-defense", "2026-wk09-bills-offense-vs-vikings-defense.md", "2026-11-09", "Bills &middot; Week 9 preview, part 2",
     "The Vikings send five or more rushers on 73% of dropbacks, more than any defense by a mile. Josh Allen has been one of the best in the league against it.",
     "wk09-blitz.png"),
    ("wentz-vs-bills-defense", "2026-wk09-wentz-vs-bills-defense.md", "2026-11-08", "Bills &middot; Week 9 preview, part 1",
     "Carson Wentz starts for Minnesota. Here's where his tendencies meet the Bills defense's weak spots, and what we expect Monday.",
     "wk09a-bills-short-deep.png"),
    ("sabres-vegas-pregame-nov-8", "2026-11-08-sabres-vgk-pregame.md", "2026-11-08", "Sabres &middot; Pregame",
     "Vegas allows fewer chances than almost anyone. Buffalo allows more than most. Where the Sabres' rebound game fits in.",
     "sabres-vgk-chances.png"),
    ("sabres-blue-jackets-nov-6", "2026-11-06-sabres-cbj.md", "2026-11-07", "Sabres &middot; Post-game",
     "Buffalo's most dangerous night of the season came from living around Columbus's crease: 10 rebound shots, their most this year.",
     "sabres-cbj-flow.png"),
    ("sabres-50-win-mirage", "sabres-50-win-mirage.md", "2026-11-06", "Sabres &middot; Why they fell off",
     "Based on the chances they created, last year's Sabres should have had about 91 points. They got 109. Here's what that means now.",
     "sabres-mirage.png"),
    ("josh-allen-2018-to-now", "2026-josh-allen.md", "2026-11-05", "Bills &middot; Josh Allen",
     "Nine seasons, three play-callers, every dropback. Through week 8 he leads the league in passing efficiency, and he's winning off script.",
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
header.site{background:#0B1B3F}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:68px;gap:16px}
.mark{font-weight:900;letter-spacing:.16em;font-size:15px;text-decoration:none;color:#fff;white-space:nowrap}
.mark b{color:#FF5A6E}
nav a{margin-left:22px;text-decoration:none;font-weight:600;font-size:15px;color:#fff}
nav a.on{color:#FFB3BD}nav a:hover{color:#FFB3BD}
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
.hero{background:var(--navy);color:#fff}
.hgrid{display:flex;flex-wrap:wrap;gap:44px;align-items:center;padding-top:56px;padding-bottom:64px;max-width:1160px}
.hcopy{flex:1 1 480px;min-width:0}.hk{font-size:13px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#FFB3BD}
.hero h1{font-family:Inter,-apple-system,"Segoe UI",sans-serif;font-weight:800;font-size:clamp(32px,4.6vw,50px);line-height:1.06;letter-spacing:-.02em;margin:14px 0 16px;color:#fff}
.hdek{font-size:20px;line-height:1.5;color:#D6E0F5;margin:0 0 26px}
.btn{display:inline-block;background:var(--red);color:#fff;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:8px}.btn:hover{color:#fff;background:#A50A28}
.hpanel{flex:1 1 360px;min-width:0;background:#0B1B3F;border-radius:16px;padding:30px}.hpanel img{border:0}
.hlabel{font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#9FB3DA}
.bigs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:18px 0 24px}
.bign{font-size:clamp(56px,8vw,86px);font-weight:800;line-height:1;font-variant-numeric:tabular-nums}.bign.dim{color:#9FB3DA}
.bigl{font-size:15px;color:#D6E0F5;margin-top:8px}
.hbar{display:flex;align-items:center;gap:12px;margin:8px 0}.hbar span{display:block;height:14px;background:#fff;border-radius:4px}.hbar span.dim{background:#9FB3DA}.hbar b{font-size:14px;font-weight:600}
.hnote{font-size:14px;color:#9FB3DA;margin:18px 0 0}
main.home .wrap{max-width:1160px}main.home .wrap>section{margin-top:52px}main.home h2{font-family:Inter,-apple-system,"Segoe UI",sans-serif;font-weight:800;letter-spacing:-.01em}
header.site .wrap,footer .wrap{max-width:1160px}
.shead{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:10px}.shead h2{margin:0}
.sdek{color:var(--muted);margin:6px 0 18px}.small{font-size:13px;color:var(--muted);margin-top:12px}
.lgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.lcard{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px}.lcard.wide{grid-column:span 2}
.lk{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}.lt{font-weight:800;font-size:20px;margin-top:6px}
.lp{font-size:40px;font-weight:800;color:var(--navy);line-height:1.1}.ls{font-size:15px;color:#4A5160;margin-top:6px}
.agrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:18px}
.acard{display:flex;flex-direction:column;gap:8px;background:#fff;border:1px solid var(--line);border-top:8px solid var(--navy);border-radius:12px;padding:20px 22px;text-decoration:none;color:var(--ink)}
.acard.sabres{border-top-color:var(--red)}.acard:hover{border-color:#B9C2D3}
.ak{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--navy)}.acard.sabres .ak{color:var(--red)}
.at{font-weight:800;font-size:19px;line-height:1.3}.ad{font-size:15px;color:#4A5160;line-height:1.5}
.how{background:#fff;border:1px solid var(--line);border-radius:16px;padding:30px;display:flex;flex-wrap:wrap;gap:32px;align-items:center}
.how>div:first-child{flex:1 1 400px;min-width:0}.how .kicker{margin:0 0 6px}.how h2{margin:0 0 10px}.how p{color:#4A5160;margin:0 0 10px}
.xbars{flex:1 1 340px;min-width:0}.xbar{display:flex;align-items:center;gap:12px;margin:10px 0}
.xl{width:72px;font-size:14px;color:#4A5160}.xt{flex:1}.xt span{display:block;height:22px;background:var(--navy);border-radius:4px}.xv{width:52px;font-size:14px;font-variant-numeric:tabular-nums}
@media(max-width:600px){.lcard.wide{grid-column:auto}.hgrid{padding-top:36px;padding-bottom:40px}}
.bio{display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:12px;padding:26px;margin:28px 0}
.bio img{width:180px;height:180px;object-fit:cover;border-radius:50%;border:4px solid var(--navy)}.bio>div{flex:1 1 380px;min-width:0}.bio h2{margin:0 0 8px}.bio .btn{margin-top:4px}
@media(max-width:600px){header.site .wrap{flex-direction:column;align-items:flex-start;justify-content:center;height:auto;padding-top:12px;padding-bottom:10px;gap:6px}nav a{margin:0 16px 0 0;font-size:14px}.mark{font-size:14px}}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:26px;margin:28px 0}
.gc{perspective:1200px;height:440px;cursor:pointer}
.gc input{display:none}
.gci{position:relative;width:100%;height:100%;transition:transform .6s;transform-style:preserve-3d}
.gc input:checked+.gci{transform:rotateY(180deg)}
.gf,.gb{position:absolute;inset:0;backface-visibility:hidden;border-radius:14px;border:8px solid var(--tc);background:#FFFDF6;box-shadow:0 6px 18px rgba(20,23,31,.14);overflow:hidden}
.gb{transform:rotateY(180deg);padding:16px 16px 12px;font-size:13px}
.gtop{background:var(--tc);color:#fff;padding:12px 16px 10px;display:flex;justify-content:space-between;align-items:flex-start}
.gtop .tm{font-size:11px;font-weight:800;letter-spacing:.16em}.gtop .no{font-size:44px;font-weight:900;line-height:.9;color:var(--ta)}
.gname{font-family:Georgia,serif;font-size:24px;font-weight:700;line-height:1.1;margin:12px 16px 2px}
.gpos{margin:0 16px;font-size:11px;letter-spacing:.14em;color:var(--muted);font-weight:700}
.gbig{margin:14px 16px 4px;display:flex;align-items:baseline;gap:10px}.gbig .v{font-size:46px;font-weight:900;color:var(--ink);line-height:1}
.gbig .l{font-size:12px;color:#4A5160;line-height:1.25}
.grow{display:grid;grid-template-columns:1fr 1fr 1fr;margin:10px 16px 0;border-top:2px solid var(--tc)}
.grow div{padding:8px 0 4px}.grow b{display:block;font-size:18px}.grow span{font-size:10.5px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}
.gspark{margin:8px 16px 0}.gspark small{display:block;font-size:10.5px;color:var(--muted)}
.gflip{position:absolute;bottom:8px;right:12px;font-size:10.5px;color:var(--muted);letter-spacing:.08em}
.gsmall{position:absolute;bottom:8px;left:14px;font-size:10.5px;color:var(--red);font-weight:700;letter-spacing:.06em}
.gb h4{margin:0 0 8px;font-family:Georgia,serif;font-size:18px}.gb table{width:100%;border-collapse:collapse;font-size:12.5px;font-variant-numeric:tabular-nums}
.gb th{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:right;padding:4px 2px;border-bottom:2px solid var(--tc)}
.gb th:first-child,.gb td:first-child{text-align:left}.gb td{text-align:right;padding:5px 2px;border-bottom:1px solid var(--line)}
.gb p{margin:10px 0 0;line-height:1.45;color:#3B4150}

.cards.one{grid-template-columns:minmax(260px,330px)}
.plist{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:12px 0 26px}
.pcard{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid var(--line);border-left:10px solid var(--tc);border-radius:10px;padding:12px 16px;text-decoration:none;color:var(--ink)}
.pcard:hover{border-color:var(--tc)}.pn{font-size:30px;font-weight:900;color:var(--ta);min-width:44px;text-align:center}.pm{font-size:14px;color:#4A5160}.pm b{color:var(--ink);font-size:16px}
"""

import hashlib
CSS_V = hashlib.sha1(CSS.encode()).hexdigest()[:8]  # changes whenever the CSS changes, so browsers refetch it

NAV = [("index.html", "Home"), ("analysis/", "Analysis"), ("cards/", "Cards"), ("ledger.html", "Ledger"), ("about.html", "About")]


def page(title, body, active, depth=0, desc="Buffalo Bills and Sabres analytics with receipts.", og="allen-seasons.png", full=False):
    up = "../" * depth
    links = "".join(f'<a href="{up}{h}" class="{"on" if n == active else ""}">{n}</a>' for h, n in NAV)
    t = html.escape(title)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title><meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{DOMAIN}/analysis/{og}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{up}favicon.svg"><link rel="stylesheet" href="{up}style.css?v={CSS_V}"></head><body>
<header class="site"><div class="wrap"><a class="mark" href="{up}index.html">BUFFALO <b>QUANT</b> DESK</a><nav>{links}</nav></div></header>
<main class="{"home" if full else "wrap"}">{body}</main>
<footer><div class="wrap">Buffalo Quant Desk. Every number is computed from public play-by-play
(NFL data via nflverse; NHL data from the league's public game feed). Analysis, not wagering advice. Not affiliated with the Buffalo Bills,
Buffalo Sabres, the NFL or the NHL.</div></footer>
<!-- Cloudflare Web Analytics: cookie-free page counts --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "a26a7c50a2a7415992abfa6838b4ebd6"}}'></script>
</body></html>"""


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
                if float(r.probability) < .5:
                    res += " (we gave it under 50%)"
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


# Stories published before the review gate existed (2026-11-08). Everything else must pass docs/editorial-process.md.
LEGACY = {"bills-offense-vs-vikings-defense", "wentz-vs-bills-defense", "sabres-vegas-pregame-nov-8", "sabres-blue-jackets-nov-6",
          "sabres-50-win-mirage", "josh-allen-2018-to-now", "bills-defense-fixed"}


def check_reviews(articles=None):
    from src.site.review_gate import problems
    bad = {s: problems(ROOT / "reports" / src) for s, src, *_ in (articles or ARTICLES) if s not in LEGACY}
    bad = {s: p for s, p in bad.items() if p}
    if bad:
        raise SystemExit("Review gate (docs/editorial-process.md) blocks:\n" + "\n".join(f"  {s}: {'; '.join(p)}" for s, p in bad.items()))


def build_articles():
    check_reviews()
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


def team_of(kicker):
    return "sabres" if kicker.lower().startswith("sabres") else "bills"


def build_home(articles, texts):
    import json
    slug, src, date, kicker, dek, hero = articles[0]
    title = re.match(r"# (.+)", texts[slug]).group(1)
    hj = ROOT / "reports" / src.replace(".md", ".hero.json")
    hd = json.loads(hj.read_text()) if hj.exists() else None
    if hd:
        numeric = all(isinstance(n, (int, float)) for n, _ in hd["big"])
        top = max(n for n, _ in hd["big"]) if numeric else 1
        nums = "".join(f'<div><div class="bign{" dim" if i else ""}">{n}</div><div class="bigl">{html.escape(l)}</div></div>'
                       for i, (n, l) in enumerate(hd["big"]))
        bars = "".join(f'<div class="hbar"><span style="width:{n / top:.0%}"{" class=dim" if i else ""}></span><b>{n}</b></div>'
                       for i, (n, l) in enumerate(hd["big"])) if numeric else ""
        panel = (f'<div class="hpanel"><div class="hlabel">{html.escape(hd["label"])}</div><div class="bigs">{nums}</div>'
                 f'{bars}<p class="hnote">{html.escape(hd["note"])}</p></div>')
    else:
        panel = f'<div class="hpanel"><img src="analysis/{hero}" alt=""></div>'
    m, _ = ledger_rows()
    if m.empty:
        lcards = ('<div class="lcard"><div class="lk">Next up</div><div class="lt">Bills at Vikings</div>'
                  '<div class="ls">Monday Night Football, Nov. 9</div></div>'
                  '<div class="lcard wide"><div class="ls">The first calls are logged before kickoff and appear here the moment '
                  'they are. Every one gets graded after the game, hit or miss.</div></div>')
        record = "No calls graded yet."
    else:
        open_ = m[~m.outcome.astype(str).isin(["0", "1", "0.0", "1.0"])].tail(3)
        show = open_ if len(open_) else m.tail(3)
        lcards = "".join(f'<div class="lcard"><div class="lp">{float(r.probability):.0%}</div>'
                         f'<div class="ls">{html.escape(r.claim_text)}</div></div>' for r in show.itertuples())
        g = m[m.outcome.astype(str).isin(["0", "1", "0.0", "1.0"])]
        hits = sum((g.probability.astype(float) >= .5) == (g.outcome.astype(float) == 1))
        record = f"Record so far: {hits}-{len(g) - hits} on {len(g)} graded calls." if len(g) else "No calls graded yet."
    cards = "".join(
        f'<a class="acard {team_of(k)}" href="analysis/{s}.html"><span class="ak">{k}</span>'
        f'<span class="at">{html.escape(re.match(r"# (.+)", texts[s]).group(1))}</span><span class="ad">{html.escape(d)}</span></a>'
        for s, _, _, k, d, _ in articles)
    how = ""
    if hd and "explainer" in hd:
        e = hd["explainer"]; mx = max(abs(v) for _, v in e["bars"])
        rows = "".join(f'<div class="xbar"><span class="xl">{html.escape(l)}</span><span class="xt"><span style="width:{max(v, 0) / mx:.0%}"></span></span>'
                       f'<span class="xv">{(f"{v:.1f} pts" if e.get("fmt") == "pts" else f"{v:+.0f} per 100" if e.get("fmt") == "per100" else f"{v:+.1f} goals" if e.get("fmt") == "goals" else f"{v:.1%}")}</span></div>' for l, v in e["bars"])
        how = (f'<section class="how"><div><div class="kicker">{html.escape(e["kicker"])}</div><h2>{html.escape(e["title"])}</h2>'
               f'<p>{html.escape(e["text"])}</p><a href="analysis/{slug}.html">How we measure it &rarr;</a></div><div class="xbars">{rows}</div></section>')
    body = f"""<section class="hero"><div class="wrap hgrid"><div class="hcopy">
<div class="hk">{kicker}</div><h1>{html.escape(title)}</h1><p class="hdek">{html.escape(dek)}</p>
<a class="btn" href="analysis/{slug}.html">Read the story</a></div>{panel}</div></section>
<div class="wrap">
<section><div class="shead"><h2>The Ledger</h2><a href="ledger.html">Every call, graded in public &rarr;</a></div>
<p class="sdek">Every prediction is timestamped before kickoff and graded after. Misses stay up.</p>
<div class="lgrid">{lcards}</div><p class="small">{record}</p></section>
<section><div class="shead"><h2>Latest analysis</h2><a href="analysis/">All stories &rarr;</a></div><div class="agrid">{cards}</div></section>
{how}</div>"""
    (SITE / "index.html").write_text(page("Buffalo Quant Desk | Bills and Sabres analytics", body, "Home", full=True))


LINKEDIN = "https://www.linkedin.com/in/charliecraine/"


def build_about():
    body = f"""<div class="kicker">About</div><h1>Buffalo's quant desk.</h1>
<p class="dek">Most sports coverage tells you what happened. We try to tell you what happens next,
put a probability on it, and show our work.</p>
<section class="bio"><img src="charlie.jpg" alt="Charlie Craine" width="180" height="180">
<div><h2>Charlie Craine</h2>
<p>Charlie grew up in Western New York and has been a Bills and Sabres fan his whole life. He has spent two decades
building digital products and data teams, including nearly ten years as a CTO.</p>
<p>He also spent more than three years at Amazon Web Services as Global Head of Startups for Digital Customer Experience, across AWS's
$6 billion startup business.</p>
<p>He's a Kaggle Grandmaster, the top tier of the world's largest data science competition platform, and builds
AI and machine-learning systems, including his own stock trading models. Buffalo Quant Desk uses the same approach on
the Bills and Sabres: start from every play, measure what actually repeats, put a probability on what happens next, and
keep score in public.</p>
<p><a class="btn" href="{LINKEDIN}" rel="noopener">Connect on LinkedIn</a></p></div></section>
<h2>How we work</h2><ul class="rules">
<li><b>Every play, every shot.</b> Everything starts from the leagues' own public play-by-play. Nothing is hand-entered.</li>
<li><b>Plain English.</b> Every story explains where its numbers come from, with real examples, and saves the jargon for the end.</li>
<li><b>Receipts.</b> Every prediction lives on the <a href="ledger.html">Ledger</a>, logged before kickoff and graded in public.</li>
<li><b>Checked twice.</b> Every story is recomputed by an independent review before it's published.</li></ul>
<h2>What we cover</h2><ul class="rules"><li><b>Bills:</b> game previews with logged predictions, post-game reports, and deep dives on players and coaches.</li>
<li><b>Sabres:</b> built on our own expected-goals model, which measures how good a team's scoring chances really are.</li></ul>
<h2>What we don't do</h2><p>Betting content. No odds, lines, picks or units. Projections are analysis, not wagering advice.</p>
<h2>Media</h2><p>Available for radio, podcast and TV segments on the Bills and Sabres. Reach Charlie on
<a href="{LINKEDIN}" rel="noopener">LinkedIn</a>.</p>"""
    (SITE / "about.html").write_text(page("About | Buffalo Quant Desk", body, "About"))


TEAM_COLORS = {"BUF": ("#003087", "#FFB81C", "SABRES"), "VGK": ("#333F42", "#B4975A", "GOLDEN KNIGHTS")}


def spark_svg(vals, color):
    if not vals:
        return ""
    w, h = 238, 54
    lo, hi = min(min(vals), 0), max(max(vals), 0)
    rng = (hi - lo) or 1
    xs = [i * w / max(len(vals) - 1, 1) for i in range(len(vals))]
    ys = [h - (v - lo) / rng * h for v in vals]
    zero = h - (0 - lo) / rng * h
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return (f'<svg viewBox="0 -4 {w} {h + 8}" width="100%" height="{h + 8}" role="img" aria-label="Goals saved vs average, running total">'
            f'<line x1="0" x2="{w}" y1="{zero:.1f}" y2="{zero:.1f}" stroke="#C9CDD4" stroke-dasharray="3 3"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3.5" fill="{color}"/></svg>')


def card_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def card_tile(c, m):
    tc, ta, tname = TEAM_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
    sign = lambda v: f"{v:+.1f}"
    rows = "".join(f"<tr><td>{r['season']}</td><td>{r['team']}</td><td>{r['gp']}</td><td>{r['sog']}</td>"
                   f"<td>{r['sv']:.3f}</td><td>{sign(r['gsax'])}</td></tr>" for r in c["seasons"])
    close = (f"{c['close_sv']:.3f}" if c["close_sv"] is not None else "&ndash;")
    return f"""<label class="gc" style="--tc:{tc};--ta:{ta}"><input type="checkbox"><div class="gci">
<div class="gf"><div class="gtop"><div class="tm">{tname}<br>{m['season']}</div><div class="no">{c['number'] or ''}</div></div>
<div class="gname">{html.escape(c['name'])}</div><div class="gpos">GOALIE</div>
<div class="gbig"><div class="v">{sign(c['gsax'])}</div><div class="l">goals saved vs. an<br>average goalie<br><b>{c['rk']} of {c['of']}</b> goalies this season</div></div>
<div class="grow"><div><b>{c['gp']}</b><span>Games</span></div><div><b>{c['sv']:.3f}</b><span>Save rate</span></div><div><b>{close}</b><span>Close-in save</span></div></div>
<div class="gspark">{spark_svg(c['spark'], tc)}<small>Goals saved vs. average, running total, game by game (dashed line = average)</small></div>
{'<div class="gsmall">SMALL SAMPLE</div>' if c['small'] else ''}<div class="gflip">TAP TO FLIP &#8635;</div></div>
<div class="gb"><h4>{html.escape(c['name'])}</h4><table><tr><th>Season</th><th>Team</th><th>Games</th><th>Shots</th><th>Save</th><th>vs. Avg</th></tr>{rows}</table>
<p><b>Blended rating: {c['blend']:+.2f}</b> goals saved per 100 shots ({c['blend_rk']} of {c['of']}). It mixes this season with seasons back to 2023-24 and
pulls toward average, so a hot or cold dozen games doesn't take over.</p>
<p>Facing {c['sog']} shots this season, an average goalie would have a {c['xsv']:.3f} save rate; he's at {c['sv']:.3f}.
League close-in save rate (within 20 ft): {m['lg_close_sv']:.3f}.</p></div></div></label>"""


def card_howto(m):
    return f"""<h2>How to read a card</h2>
<p><b>Goals saved vs. an average goalie</b> is the big number. Every shot that reaches the net or misses it has a chance of going in, based on
where it came from and what kind of shot it was. Add up those chances on every shot a goalie faced and you get how many goals an average goalie
would have allowed. Subtract the goals he actually allowed. Positive means he stopped more than an average goalie would have.</p>
<p><b>Save rate</b> is the share of shots on goal he stopped; the league's is {m['lg_sv']:.3f} this season. <b>Close-in save</b> is the same for
shots from within 20 feet, the hardest ones; the league's is {m['lg_close_sv']:.3f}.</p>
<p><b>The blended rating</b> on the back is our best estimate of how good he is, though goalie numbers bounce around a lot
even over half a season. It adds this season's shots to half the weight of his shots from past
seasons (back to 2023-24), plus {m['shrink']} shots of league-average goaltending, so a dozen games can't swing it too far. As this season's shots
pile up, they take over.</p>
<p><b>The source:</b> the NHL's own play-by-play and our expected-goals model, the same one behind our Sabres stories. Cards marked
<b>small sample</b> have fewer than 300 shots this season. Not affiliated with the NHL or any team; card designs are our own.</p>"""


def build_cards():
    import json
    src = ROOT / "reports" / "cards" / "goalies.json"
    out = SITE / "cards"
    out.mkdir(exist_ok=True)
    if not src.exists():
        return
    d = json.loads(src.read_text())
    m = d["meta"]
    asof = datetime.strptime(m["as_of"], "%Y-%m-%d").strftime("%B %-d, %Y")
    groups = {}
    for c in d["cards"]:
        slug = card_slug(c["name"])
        tc, ta, tname = TEAM_COLORS.get(c["team"], ("#00338D", "#C60C30", c["team"]))
        close_n = f" on {c['close_sog']} close-in shots" if c["close_sog"] else ""
        body = f"""<div class="kicker"><a href="index.html">Player cards</a> &middot; {tname.title()}</div><h1>{html.escape(c['name'])}</h1>
<p class="dek">Goalie, {tname.title()}. {sign_txt(c['gsax'])} goals saved compared with an average goalie this season, {c['rk']} of {c['of']}
goalies, over {c['gp']} games and {c['sog']} shots on goal. Numbers through {asof}.</p>
<div class="cards one">{card_tile(c, m)}</div>
<h2>This season</h2><ul class="rules">
<li><b>Save rate {c['sv']:.3f}</b>; an average goalie facing his shots would be at {c['xsv']:.3f}. League: {m['lg_sv']:.3f}.</li>
<li><b>Close-in save rate {c['close_sv']:.3f}</b>{close_n}. League: {m['lg_close_sv']:.3f}.</li>
<li><b>Blended rating {c['blend']:+.2f}</b> goals saved per 100 shots, {c['blend_rk']} of {c['of']}.</li>
{'<li><b>Small sample.</b> Fewer than 300 shots this season; these numbers can move a lot.</li>' if c['small'] else ''}</ul>
{card_howto(m)}"""
        (out / f"{slug}.html").write_text(page(f"{c['name']} | Goalie card | Buffalo Quant Desk", body, "Cards", 1,
                                               f"{c['name']}: {sign_txt(c['gsax'])} goals saved vs. an average goalie this season."))
        groups.setdefault(tname.title(), []).append(
            f'<a class="pcard" href="{slug}.html" style="--tc:{tc};--ta:{ta}"><span class="pn">{c["number"] or ""}</span>'
            f'<span class="pm"><b>{html.escape(c["name"])}</b><br>Goalie &middot; {sign_txt(c["gsax"])} goals saved vs. average</span></a>')
    lists = "".join(f'<h2>{team}</h2><div class="plist">{"".join(items)}</div>' for team, items in groups.items())
    body = f"""<div class="kicker">Player cards</div><h1>Player cards</h1>
<p class="dek">One card per player, built from every shot and updated as the season goes. Goalies first; skaters and the Bills are next.
Numbers through {asof}.</p>{lists}"""
    (out / "index.html").write_text(page("Player cards | Buffalo Quant Desk", body, "Cards", 1, "Player cards with receipts."))


def sign_txt(v):
    return f"{v:+.1f}"


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
    build_cards()
    shutil.copy(ROOT / "assets" / "charlie.jpg", SITE / "charlie.jpg")
    (SITE / "ledger").mkdir(exist_ok=True)
    for f in (PRED_CSV, GRADE_CSV):
        if f.exists():
            shutil.copy(f, SITE / "ledger" / f.name)
        else:
            (SITE / "ledger" / f.name).write_text(",".join(PRED_COLS if f == PRED_CSV else GRADE_COLS) + "\n")
    (SITE / "404.html").write_text(page("Not found | Buffalo Quant Desk", '<h1 style="margin-top:50px">Not found.</h1><p><a href="/">Home</a></p>', ""))
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    urls = (["", "analysis/", "cards/", "ledger.html", "about.html"] + [f"analysis/{a[0]}.html" for a in ARTICLES]
            + [f"cards/{p.name}" for p in sorted((SITE / "cards").glob("*.html")) if p.name != "index.html"])
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{DOMAIN}/{u}</loc></url>" for u in urls) + "</urlset>")
    print("site built:", sorted(str(p.relative_to(SITE)) for p in SITE.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
