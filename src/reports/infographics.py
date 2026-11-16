"""Social-ready infographics, rendered from HTML to PNG with headless Chrome so they match the designs Charlie picked
(MVP race board, AFC ladder, Bills clinch calendar). Every number arrives from a story generator; nothing is typed here.

Fonts are vendored in assets/fonts (SIL Open Font License, texts alongside), so renders don't depend on the network.
"""
import base64
import html
import pathlib
from functools import lru_cache

from src.db import ROOT

FONTS = ROOT / "assets" / "fonts"
NAVY, RED, INK = "#00338D", "#C60C30", "#121826"
CHROME = "/usr/bin/google-chrome"


@lru_cache(maxsize=None)
def _font(name):
    return base64.b64encode((FONTS / name).read_bytes()).decode()


def _page(body, w, h, bg):
    ff = lambda fam, fn, wt, kind: (f"@font-face{{font-family:'{fam}';src:url(data:font/{kind};base64,{_font(fn)}) "
                                    f"format('{'truetype' if kind == 'ttf' else 'opentype'}');font-weight:{wt}}}")
    faces = "".join([ff("Space Grotesk", "SpaceGrotesk.ttf", "300 700", "ttf")] +
                    [ff("Inter", f"Inter-{n}.otf", wt, "otf") for n, wt in (("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700))])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
{faces}
html,body{{margin:0}} *{{box-sizing:border-box}}
.root{{width:{w}px;height:{h}px;background:{bg};font-family:Inter,sans-serif;display:flex;flex-direction:column}}
.g{{font-family:'Space Grotesk',sans-serif;font-weight:700}}
.kick{{font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase}}
</style></head><body><div class="root">{body}</div></body></html>"""


def render(page_html, out, w, h, scale=1):
    from playwright.sync_api import sync_playwright
    out = pathlib.Path(out)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.set_content(page_html, wait_until="load")
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(out), clip={"x": 0, "y": 0, "width": w, "height": h})
        b.close()
    return out


def e(x):
    return html.escape(str(x))


def mvp_board(rows, out, kicker, title, sub, foot):
    """rows: dicts with name, team, record, pts (number), share (0-1), highlight (bool). Top row first."""
    mx = max(r["pts"] for r in rows)
    items = []
    for i, r in enumerate(rows):
        hl = r.get("highlight")
        bar = RED if hl else ("#FFFFFF" if i == 0 else "#5B78C7")
        ring = RED if hl else "#8FA3D6"
        sh = round(r["share"] * 100)
        items.append(f"""
<div style="display:grid;grid-template-columns:56px 300px minmax(0,1fr) 110px 96px;align-items:center;gap:20px;padding:18px 22px;border-radius:16px;background:{'rgba(198,12,48,.16)' if hl else 'rgba(255,255,255,.04)'}">
 <div class="g" style="font-size:44px;color:{'#FFF' if i == 0 else '#8FA3D6'}">{i + 1}</div>
 <div><div style="font-size:30px;font-weight:700">{e(r['name'])}</div><div style="font-size:19px;color:#A9B6DA;margin-top:4px">{e(r['team'])} · {e(r['record'])}</div></div>
 <div style="height:22px;border-radius:11px;background:rgba(255,255,255,.10);overflow:hidden"><div style="height:22px;border-radius:11px;width:{r['pts'] / mx * 100:.1f}%;background:{bar}"></div></div>
 <div class="g" style="font-size:48px;text-align:right">{r['pts']:.0f}</div>
 <div style="display:flex;justify-content:center"><div style="width:62px;height:62px;border-radius:50%;background:conic-gradient({ring} 0 {sh}%,rgba(255,255,255,.12) 0);display:flex;align-items:center;justify-content:center"><div style="width:44px;height:44px;border-radius:50%;background:#0B1530;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700">{sh}%</div></div></div>
</div>""")
    body = f"""<div style="flex:1;padding:72px 72px 56px;color:#FFF;display:flex;flex-direction:column;gap:36px">
<div style="display:flex;flex-direction:column;gap:14px"><div class="kick" style="color:#8FA3D6">{e(kicker)}</div>
<div class="g" style="font-size:84px;line-height:.95">{title}</div><div style="font-size:24px;line-height:1.4;color:#C9D3EE;max-width:880px">{e(sub)}</div></div>
<div style="display:flex;flex-direction:column;gap:14px;flex:1">{''.join(items)}</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:24px;font-size:18px;color:#8FA3D6"><div style="max-width:760px;line-height:1.45">{e(foot)}</div><div style="font-weight:700;color:#FFF;font-size:22px">buffaloquant.com</div></div></div>"""
    return render(_page(body, 1080, 1350, "#0B1530"), out, 1080, 1350)


def ladder(rows, out, kicker, title, sub, foot, cut=7):
    """rows: dicts with name, record, p (0-1), d (0-1), hatched (bool), highlight (bool). Best first."""
    pct = lambda x: "99%+" if x >= .995 else ("<1%" if 0 < x < .005 else f"{x:.0%}")
    items = []
    for i, r in enumerate(rows):
        if i == cut:
            items.append(f"""<div style="display:flex;align-items:center;gap:12px;margin:2px 0;font-size:15px;font-weight:700;color:{RED};letter-spacing:.1em;text-transform:uppercase"><div style="flex:1;border-top:3px dashed {RED}"></div>Playoff line<div style="flex:1;border-top:3px dashed {RED}"></div></div>""")
        bar = RED if r.get("highlight") else (f"repeating-linear-gradient(135deg,{NAVY} 0 8px,#4D6DB8 8px 14px)" if r.get("hatched") else NAVY)
        bg = "#FCECEF" if r.get("highlight") else ("#FFF" if i % 2 else "#F7F8FB")
        items.append(f"""<div style="display:grid;grid-template-columns:260px minmax(0,1fr) 110px 120px;gap:16px;align-items:center;padding:7px 16px;border-radius:12px;background:{bg}">
 <div style="display:flex;align-items:baseline;gap:10px"><div style="font-size:24px;font-weight:700">{e(r['name'])}</div><div style="font-size:17px;color:#6B7488">{e(r['record'])}</div></div>
 <div style="height:20px;border-radius:10px;background:#EEF0F5;overflow:hidden"><div style="height:20px;border-radius:10px;width:{max(r['p'] * 100, .8):.1f}%;background:{bar}"></div></div>
 <div class="g" style="font-size:28px;text-align:right">{pct(r['p'])}</div><div style="font-size:20px;color:#4A5368;text-align:right">{pct(r['d'])}</div></div>""")
    body = f"""<div style="flex:1;padding:56px 72px 44px;color:{INK};display:flex;flex-direction:column;gap:20px">
<div style="display:flex;flex-direction:column;gap:12px"><div class="kick" style="color:{NAVY}">{e(kicker)}</div><div class="g" style="font-size:66px;line-height:.98">{e(title)}</div><div style="font-size:22px;line-height:1.4;color:#4A5368">{e(sub)}</div></div>
<div style="display:grid;grid-template-columns:260px minmax(0,1fr) 110px 120px;gap:16px;font-size:16px;font-weight:700;color:#6B7488;text-transform:uppercase;letter-spacing:.08em;padding:0 16px"><div>Team</div><div>Playoff chance</div><div style="text-align:right">Playoffs</div><div style="text-align:right">Division</div></div>
<div style="display:flex;flex-direction:column;gap:4px">{''.join(items)}</div>
<div style="margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:17px;color:#4A5368;gap:24px"><div style="max-width:760px;line-height:1.45">{e(foot)}</div><div style="font-weight:700;color:{NAVY};font-size:22px">buffaloquant.com</div></div></div>"""
    return render(_page(body, 1080, 1350, "#FFFFFF"), out, 1080, 1350)


def clinch_calendar(weeks, out, kicker, title, sub_html, foot, best_week):
    """weeks: dicts with n, opp, date, by (0-1 chance clinched by the end of that week)."""
    tiles = []
    for w in weeks:
        hot = w["n"] == best_week
        tiles.append(f"""<div style="position:relative;overflow:hidden;border-radius:20px;background:rgba(255,255,255,.10);padding:20px;display:flex;flex-direction:column;justify-content:space-between;border:3px solid {'#FFF' if hot else 'transparent'}">
 <div style="position:absolute;left:0;right:0;bottom:0;height:{w['by'] * 100:.1f}%;background:{RED if hot else 'rgba(255,255,255,.22)'}"></div>
 <div style="position:relative"><div style="font-size:18px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#DCE4F7">Week {w['n']}</div><div style="font-size:20px;font-weight:600;margin-top:4px">{e(w['opp'])}</div><div style="font-size:16px;color:#DCE4F7;margin-top:4px">{e(w['date'])}</div></div>
 <div class="g" style="position:relative;font-size:58px">{'—' if w['by'] < .005 else f"{w['by']:.0%}"}</div></div>""")
    body = f"""<div style="flex:1;padding:64px;color:#FFF;display:flex;flex-direction:column;gap:34px">
<div style="display:flex;flex-direction:column;gap:12px"><div class="kick" style="color:#B9C8EE">{e(kicker)}</div><div class="g" style="font-size:70px;line-height:.98">{title}</div><div style="font-size:22px;color:#DCE4F7">{sub_html}</div></div>
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;flex:1">{''.join(tiles)}</div>
<div style="display:flex;justify-content:space-between;align-items:flex-end;font-size:17px;color:#DCE4F7;gap:24px"><div style="max-width:720px;line-height:1.45">{e(foot)}</div><div style="font-weight:700;color:#FFF;font-size:22px">buffaloquant.com</div></div></div>"""
    return render(_page(body, 1080, 1080, NAVY), out, 1080, 1080)
