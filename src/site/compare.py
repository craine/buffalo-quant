"""Compare page: filter and rank Buffalo players against the league. Static page + slim JSON built from the committed card files.

Reads reports/cards/skaters_league.json, goalies_league.json and nfl_players.json (the same files the player cards use,
refreshed daily/weekly by the bots). Writes site/compare/index.html, site/compare/nhl.json and site/compare/nfl.json.
Every number shown is a card number or simple arithmetic on card numbers (per game, percentages) done in this file.
"""
import json

from src.db import ROOT

CARDS = ROOT / "reports" / "cards"


def _r(x, n=3):
    return None if x is None else round(float(x), n)


def _pg(x, gp, n=2):
    return None if not gp or x is None else round(x / gp, n)


def _pct(a, b, n=3):
    return None if not b else round(a / b, n)


# --- columns: key, label, format (int | f1 | f2 | pct | signed), higher-is-better
NHL_SK = [("gp", "Games", "int", 1), ("g", "Goals", "int", 1), ("a", "Assists", "int", 1), ("p", "Points", "int", 1),
          ("p_pg", "Points a game", "f2", 1), ("g_pg", "Goals a game", "f2", 1), ("sog", "Shots on goal", "int", 1),
          ("ixg", "Chances (worth in goals)", "f1", 1), ("ixg_pg", "Chances a game", "f2", 1), ("fin", "Goals vs. chances", "signed", 1),
          ("hits", "Hits", "int", 1), ("blocks", "Blocked shots", "int", 1), ("take", "Takeaways", "int", 1), ("give", "Giveaways", "int", 0),
          ("fo_pct", "Faceoffs won", "pct", 1)]
NHL_G = [("gp", "Games", "int", 1), ("sog", "Shots faced", "int", 1), ("sv", "Save %", "pct", 1), ("xsv", "Average goalie's save % on his shots", "pct", 1),
         ("gsax", "Goals saved vs. an average goalie", "signed", 1), ("close_sv", "Save % on close shots", "pct", 1)]
QB = [("gp", "Games", "int", 1), ("att", "Pass attempts", "int", 1), ("cmp_pct", "Completion %", "pct", 1), ("pass_yds", "Passing yards", "int", 1),
      ("pass_ypg", "Passing yards a game", "f1", 1), ("pass_td", "Passing TDs", "int", 1), ("ints", "Interceptions", "int", 0),
      ("sacked", "Times sacked", "int", 0), ("epa_db", "Points added per dropback", "f2", 1), ("rush_yds", "Rushing yards", "int", 1)]
RB = [("gp", "Games", "int", 1), ("car", "Carries", "int", 1), ("rush_yds", "Rushing yards", "int", 1), ("ypc", "Yards a carry", "f1", 1),
      ("rush_td", "Rushing TDs", "int", 1), ("rec", "Catches", "int", 1), ("rec_yds", "Receiving yards", "int", 1),
      ("scrim", "Yards from scrimmage", "int", 1), ("scrim_pg", "Scrimmage yards a game", "f1", 1), ("fum_lost", "Fumbles lost", "int", 0)]
WR = [("gp", "Games", "int", 1), ("tgt", "Targets", "int", 1), ("rec", "Catches", "int", 1), ("catch_pct", "Catch rate", "pct", 1),
      ("rec_yds", "Receiving yards", "int", 1), ("rec_ypg", "Receiving yards a game", "f1", 1), ("ypr", "Yards a catch", "f1", 1),
      ("rec_td", "Receiving TDs", "int", 1), ("snap_pct", "Share of offensive snaps", "pct", 1)]
FRONT = [("gp", "Games", "int", 1), ("snaps", "Snaps", "int", 1), ("tackles", "Tackles", "int", 1), ("tfl", "Tackles for loss", "int", 1),
         ("sacks", "Sacks", "f1", 1), ("pressures", "Pressures", "int", 1), ("press_pg", "Pressures a game", "f1", 1),
         ("missed_tk", "Missed tackles", "int", 0)]
BACK = [("gp", "Games", "int", 1), ("snaps", "Snaps", "int", 1), ("tackles", "Tackles", "int", 1), ("def_int", "Interceptions", "int", 1),
        ("pd", "Passes defended", "int", 1), ("cov_tgt", "Times thrown at", "int", 0), ("cov_cmp_pct", "Completion % allowed", "pct", 0),
        ("cov_yds", "Yards allowed in coverage", "int", 0), ("missed_tk", "Missed tackles", "int", 0)]
OL = [("gp", "Games", "int", 1), ("snaps", "Snaps", "int", 1), ("snap_pct", "Share of offensive snaps", "pct", 1), ("penalties", "Penalties", "int", 0)]
K = [("gp", "Games", "int", 1), ("fg_made", "Field goals made", "int", 1), ("fg_att", "Field goals tried", "int", 1), ("fg_pct", "Field goal %", "pct", 1),
     ("fg_long", "Longest field goal", "int", 1), ("fg_50", "Made from 50+", "int", 1), ("pat_pct", "Extra point %", "pct", 1)]
P = [("gp", "Games", "int", 1), ("punts", "Punts", "int", 1), ("net_avg", "Net yards a punt", "f1", 1), ("punt_i20", "Inside the 20", "int", 1),
     ("punt_tb", "Touchbacks", "int", 0)]

GROUPS = {
    "nhl": [("F", "Forwards", NHL_SK, "ixg_pg", "g_pg", 8), ("D", "Defense", NHL_SK, "p_pg", "ixg_pg", 8),
            ("G", "Goalies", NHL_G, "gsax", "sv", 5)],
    "nfl": [("QB", "Quarterbacks", QB, "epa_db", "pass_ypg", 4), ("RB", "Running backs", RB, "scrim_pg", "ypc", 4),
            ("WR", "Receivers", WR, "rec_ypg", "catch_pct", 4), ("TE", "Tight ends", WR, "rec_ypg", "catch_pct", 4),
            ("DL", "Defensive line", FRONT, "press_pg", "tackles", 4), ("LB", "Linebackers", FRONT, "tackles", "press_pg", 4),
            ("CB", "Cornerbacks", BACK, "pd", "cov_cmp_pct", 4), ("S", "Safeties", BACK, "tackles", "pd", 4),
            ("OL", "Offensive line", OL, "snap_pct", "penalties", 4), ("K", "Kickers", K, "fg_pct", "fg_long", 4), ("P", "Punters", P, "net_avg", "punt_i20", 4)],
}


def nhl_rows(slugs):
    sk = json.loads((CARDS / "skaters_league.json").read_text())
    gk = json.loads((CARDS / "goalies_league.json").read_text())
    rows = []
    for c in sk["cards"]:
        gp = c["gp"]
        rows.append(dict(id=c["id"], n=c["name"], t=c["team"], pos=c["pos"], grp=c["grp"], o=bool(c.get("other_team")),
                         u=f"../cards/{slugs[('S', c['id'])]}.html", gp=gp, g=c["g"], a=c["a"], p=c["p"], p_pg=_pg(c["p"], gp), g_pg=_pg(c["g"], gp),
                         sog=c["sog"], ixg=_r(c["ixg"], 1), ixg_pg=_r(c["ixg_pg"], 2), fin=_r(c["fin"], 1), hits=c["hits"], blocks=c["blocks"],
                         take=c["take"], give=c["give"], fo_pct=_r(c["fo_pct"]) if (c.get("fo_n") or 0) >= 50 else None))
    for c in gk["cards"]:
        rows.append(dict(id=c["id"], n=c["name"], t=c["team"], pos="G", grp="G", o=bool(c.get("other_team")),
                         u=f"../cards/{slugs[('G', c['id'])]}.html", gp=c["gp"], sog=c["sog"], sv=_r(c["sv"]), xsv=_r(c["xsv"]),
                         gsax=_r(c["gsax"], 1), close_sv=_r(c["close_sv"])))
    import datetime as dt
    d0 = dt.date.fromisoformat(sk["meta"]["as_of"])
    return rows, dict(label=f"Games through {d0:%b.} {d0.day}, {sk['meta']['season']} season.")


def nfl_rows():
    from src.site.nfl_cards import slugs_for
    d = json.loads((CARDS / "nfl_players.json").read_text())
    cards = d["cards"]
    slugs = slugs_for(cards)
    rows = []
    for c in cards:
        grp = c["grp"]
        if grp not in {"QB", "RB", "WR", "TE", "DL", "LB", "CB", "S", "OL", "K", "P"} or not c["gp"]:
            continue
        gp = c["gp"]
        r = dict(id=c["id"], n=c["name"], t=c["team"], pos=c["pos"], grp=grp, o=bool(c.get("other_teams")), u=f"../cards/nfl/{slugs[c['id']]}.html", gp=gp)
        if grp == "QB":
            r.update(att=c["att"], cmp_pct=_pct(c["cmp"], c["att"]), pass_yds=c["pass_yds"], pass_ypg=_pg(c["pass_yds"], gp, 1), pass_td=c["pass_td"],
                     ints=c["ints"], sacked=c["sacked"], epa_db=_r(c["epa_db"], 2) if (c.get("n_db") or 0) >= d["meta"]["min_db"] else None, rush_yds=c["rush_yds"])
        elif grp == "RB":
            r.update(car=c["car"], rush_yds=c["rush_yds"], ypc=_pg(c["rush_yds"], c["car"], 1) if c["car"] >= 20 else None, rush_td=c["rush_td"],
                     rec=c["rec"], rec_yds=c["rec_yds"], scrim=c["scrim"], scrim_pg=_pg(c["scrim"], gp, 1), fum_lost=c["fum_lost"])
        elif grp in ("WR", "TE"):
            r.update(tgt=c["tgt"], rec=c["rec"], catch_pct=_pct(c["rec"], c["tgt"]) if c["tgt"] >= 10 else None, rec_yds=c["rec_yds"],
                     rec_ypg=_pg(c["rec_yds"], gp, 1), ypr=_pg(c["rec_yds"], c["rec"], 1) if c["rec"] >= 5 else None, rec_td=c["rec_td"],
                     snap_pct=_r(c["snap_pct"]) if c.get("snap_data") else None)
        elif grp in ("DL", "LB"):
            r.update(snaps=c["snaps"], tackles=c["tackles"], tfl=c["tfl"], sacks=c["sacks"], pressures=c["pressures"],
                     press_pg=_pg(c["pressures"], c["gp_pfr"], 1) if c.get("gp_pfr") else None, missed_tk=c["missed_tk"])
        elif grp in ("CB", "S"):
            r.update(snaps=c["snaps"], tackles=c["tackles"], def_int=c["def_int"], pd=c["pd"], cov_tgt=c["cov_tgt"],
                     cov_cmp_pct=_pct(c["cov_cmp"], c["cov_tgt"]) if c["cov_tgt"] >= 10 else None, cov_yds=c["cov_yds"], missed_tk=c["missed_tk"])
        elif grp == "OL":
            r.update(snaps=c["snaps"], snap_pct=_r(c["snap_pct"]) if c.get("snap_data") else None, penalties=c["penalties"])
        elif grp == "K":
            r.update(fg_made=c["fg_made"], fg_att=c["fg_att"], fg_pct=_r(c["fg_pct"]) if c["fg_att"] >= d["meta"]["min_fga"] else None,
                     fg_long=c["fg_long"], fg_50=c.get("fg_50") or 0, pat_pct=_pct(c["pat_made"], c["pat_att"]))
        elif grp == "P":
            r.update(punts=c["punts"], net_avg=_r(c["net_avg"], 1) if c["punts"] >= d["meta"]["min_punts"] else None,
                     punt_i20=c["punt_i20"], punt_tb=c["punt_tb"])
        rows.append(r)
    m = d["meta"]
    return rows, dict(label=f"Through Week {m['week']} of the {m['season']} season.")


def config():
    return {s: [dict(id=g, label=lab, cols=[dict(k=k, l=l, f=f, hi=hi) for k, l, f, hi in cols], rank=rk, y=y, min=mn)
                for g, lab, cols, rk, y, mn in gs] for s, gs in GROUPS.items()}


PAGE = r"""
<div class="cmp">
<p class="kicker">Compare</p>
<h1>Compare Buffalo players to the league</h1>
<p class="dek">Pick a group, set the filters, and see where every Sabre or Bill ranks.</p>
<div class="seg" role="group" aria-label="Sport"><button type="button" data-s="nhl">Sabres vs. NHL</button><button type="button" data-s="nfl">Bills vs. NFL</button></div>
<section class="fbox" aria-label="Filters">
<div class="chips" id="groups" role="group" aria-label="Position"></div>
<div class="frow">
<label>Team<select id="team"></select></label>
<label>Minimum games<select id="mingp"></select></label>
<label>Rank by<select id="rank"></select></label>
<label>Chart against<select id="ystat"></select></label>
<label class="rng"><span>Range: <span id="rlab"></span></span><span class="rr"><input id="lo" type="number" step="any" inputmode="decimal" aria-label="Lowest value"> to <input id="hi" type="number" step="any" inputmode="decimal" aria-label="Highest value"></span></label>
</div>
<div class="fbot"><label class="chk"><input type="checkbox" id="bufonly"> <span id="buflab">Show only Sabres</span></label>
<span class="cnt" id="count"></span><button type="button" class="btn sm" id="share">Copy link to this view</button></div>
</section>
<div class="tiles" id="tiles"></div>
<section class="pbox"><div class="phead"><h2 id="ctitle"></h2><div class="leg"><span><i class="dot b"></i><span id="legbuf">Sabres</span></span><span><i class="dot o"></i><span id="legoth">Rest of the NHL</span></span></div></div>
<p class="small" id="csub"></p><div id="chart"></div><div class="tip" id="tip" hidden></div></section>
<section class="pbox tbl"><div class="phead"><h2 id="ttitle"></h2><span class="small">Click a column to sort</span></div>
<div class="tablewrap"><table id="table"></table></div><div class="tfoot"><span id="showing"></span><button type="button" class="lnk" id="more"></button></div></section>
<p class="small" id="foot"></p>
</div>
"""

CSS = """
.cmp{max-width:1160px;margin:0 auto;padding:0 22px}.cmp h1{font-family:Inter,-apple-system,"Segoe UI",sans-serif;font-weight:800;letter-spacing:-.02em}
.seg{display:inline-flex;background:#EDEFF3;border-radius:10px;padding:4px;gap:4px;margin:6px 0 18px}
.seg button{border:0;background:transparent;color:var(--muted);font:600 15px/1 inherit;padding:12px 18px;border-radius:8px;cursor:pointer;min-height:44px}
.seg button.on{background:#fff;color:var(--navy);font-weight:800;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.fbox,.pbox{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 18px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.chips button{border:1px solid #CDD2DA;background:#fff;color:var(--ink);border-radius:999px;padding:8px 14px;font:600 14px inherit;cursor:pointer;min-height:40px}
.chips button.on{background:var(--navy);border-color:var(--navy);color:#fff}
.frow{display:flex;flex-wrap:wrap;gap:14px}.frow label{display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:600;color:var(--muted);flex:1 1 170px;min-width:0}
.frow select,.frow input{font:15px inherit;color:var(--ink);padding:9px 10px;border:1px solid #CDD2DA;border-radius:8px;background:#fff;min-height:44px;width:100%}
.frow .rng{flex:2 1 300px}.rr{display:flex;align-items:center;gap:8px;color:var(--muted)}.rr input{flex:1}
.fbot{display:flex;flex-wrap:wrap;align-items:center;gap:12px;justify-content:space-between;border-top:1px solid #EEF0F3;margin-top:16px;padding-top:12px}
.chk{display:flex;align-items:center;gap:10px;font-weight:600;font-size:15px}.chk input{width:20px;height:20px;accent-color:var(--navy)}
.cnt{font-size:14px;color:var(--muted);margin-left:auto}.btn.sm{padding:10px 16px;font-size:15px;border:0;cursor:pointer}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:0 0 18px}
.tile{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}.tile .k{font-size:13px;font-weight:600;color:var(--muted)}
.tile .v{font-size:28px;font-weight:800;line-height:1.2}.tile .v.b{color:var(--navy)}.tile .s{font-size:15px}
.phead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:10px}.phead h2{margin:0;font-family:Inter,sans-serif;font-size:20px;font-weight:800}
.leg{display:flex;gap:16px;font-size:14px;color:var(--muted)}.leg span{display:flex;align-items:center;gap:6px}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%}.dot.b{background:var(--navy)}.dot.o{background:#B7BDC7}
#chart svg{display:block;width:100%;height:auto}#chart circle{cursor:pointer}
.pbox{position:relative}.tip{position:absolute;pointer-events:none;background:#0B1B3F;color:#fff;font-size:13px;line-height:1.4;padding:8px 10px;border-radius:8px;max-width:240px;z-index:5}
.tbl{padding:12px 0 0}.tbl .phead{padding:0 20px 6px}.tbl table{margin:0;min-width:640px}
.tbl th{cursor:pointer;white-space:nowrap;text-align:right;user-select:none}.tbl th:nth-child(-n+4),.tbl td:nth-child(-n+4){text-align:left}
.tbl td{text-align:right}.tbl td:nth-child(2){white-space:nowrap}.tbl td.key{font-weight:800}.tbl th.on{color:var(--navy)}.tbl tr.buf td{background:#EAF0FB}.tbl tr.buf a{font-weight:800}
.tbl tr.sep td{background:#F6F7F9;font-size:13px;font-weight:700;color:var(--muted);text-align:left}.tbl td.rk{color:var(--muted)}
.tfoot{display:flex;justify-content:space-between;gap:10px;padding:12px 20px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
.lnk{border:0;background:none;color:var(--navy);font:600 14px inherit;cursor:pointer;padding:0}
"""

JS = r"""
(()=>{
const CFG=__CFG__, NAME={nhl:["Sabres","NHL"],nfl:["Bills","NFL"]};
const DATA={}; let S={s:"nhl",g:null,t:"all",m:null,r:null,y:null,b:0,lo:"",hi:"",sk:null,sd:-1,all:0};
const $=id=>document.getElementById(id), esc=x=>String(x).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt=(v,f)=>v==null?"–":f==="int"?Math.round(v).toLocaleString():f==="f1"?v.toFixed(1):f==="f2"?v.toFixed(2):f==="pct"?(v*100).toFixed(1)+"%":(v>0?"+":"")+v.toFixed(1);
const ord=n=>n+(["th","st","nd","rd"][(n%100-20)%10]||["th","st","nd","rd"][n%100]||"th");
function readHash(){const h=new URLSearchParams(location.hash.slice(1));for(const k of Object.keys(S)){if(h.has(k))S[k]=["b","sd","all"].includes(k)?+h.get(k):h.get(k)}}
function writeHash(){const h=new URLSearchParams();for(const k of["s","g","t","m","r","y","b","lo","hi"])if(S[k]!==""&&S[k]!=null)h.set(k,S[k]);history.replaceState(null,"","#"+h)}
async function load(s){if(!DATA[s])DATA[s]=await fetch(s+".json?v=__V__").then(r=>r.json());return DATA[s]}
function grp(){return CFG[S.s].find(g=>g.id===S.g)||CFG[S.s][0]}
function col(k){return grp().cols.find(c=>c.k===k)}
async function render(){
  const D=await load(S.s), G=grp(); S.g=G.id; if(!G.cols.some(c=>c.k===S.r))S.r=G.rank; if(!G.cols.some(c=>c.k===S.y)||S.y===S.r)S.y=G.y===S.r?G.cols.find(c=>c.k!==S.r&&c.k!=="gp").k:G.y;
  if(S.m==null||isNaN(+S.m))S.m=G.min; const [bn,lg]=NAME[S.s];
  document.querySelectorAll(".seg button").forEach(b=>b.classList.toggle("on",b.dataset.s===S.s));
  $("groups").innerHTML=CFG[S.s].map(g=>`<button type="button" data-g="${g.id}" class="${g.id===G.id?"on":""}">${g.label}</button>`).join("");
  const teams=[...new Set(D.rows.map(r=>r.t))].sort();
  $("team").innerHTML=`<option value="all">All ${teams.length} teams</option>`+teams.map(t=>`<option${t===S.t?" selected":""}>${t}</option>`).join("");
  $("mingp").innerHTML=[1,2,4,6,8,10,12,15,20].map(n=>`<option value="${n}"${n==S.m?" selected":""}>${n===1?"Any":n+" or more"}</option>`).join("");
  const opts=k=>G.cols.filter(c=>c.k!=="gp"||k==="y").map(c=>`<option value="${c.k}"${c.k===S[k]?" selected":""}>${c.l}</option>`).join("");
  $("rank").innerHTML=opts("r"); $("ystat").innerHTML=opts("y");
  const R=col(S.r), Y=col(S.y); $("rlab").textContent=R.l.toLowerCase(); $("lo").value=S.lo; $("hi").value=S.hi;
  $("bufonly").checked=!!S.b; $("buflab").textContent=`Show only ${bn}`; $("legbuf").textContent=bn; $("legoth").textContent=`Rest of the ${lg}`;
  // the ranking pool: this position group, enough games, has a value for the stat
  const pool=D.rows.filter(r=>r.grp===G.id&&r.gp>=+S.m&&r[S.r]!=null);
  const sorted=[...pool].sort((a,b)=>R.hi?b[S.r]-a[S.r]:a[S.r]-b[S.r]); const rk=new Map(); sorted.forEach((r,i)=>{const prev=sorted[i-1];rk.set(r,prev&&prev[S.r]===r[S.r]?rk.get(prev):i+1)});
  const tie=new Map();for(const r of pool){const k=rk.get(r);tie.set(k,(tie.get(k)||0)+1)} const rks=r=>{const k=rk.get(r);return tie.get(k)>1?"T-"+k:String(k)}; const rkw=r=>{const k=rk.get(r);return (tie.get(k)>1?"tied for ":"")+ord(k)};
  const avg=pool.reduce((s,r)=>s+r[S.r],0)/(pool.length||1);
  let view=pool.filter(r=>(S.t==="all"||r.t===S.t)&&(S.lo===""||r[S.r]>=+S.lo)&&(S.hi===""||r[S.r]<=+S.hi)&&(!S.b||r.t==="BUF"));
  $("count").textContent=`${view.length} of ${pool.length} ${G.label.toLowerCase()} match`;
  const bufs=sorted.filter(r=>r.t==="BUF");
  const best=bufs[0];
  $("tiles").innerHTML=[best?`<div class="tile"><div class="k">Best ${bn.slice(0,-1)} in ${esc(R.l.toLowerCase())}</div><div class="v b">${rkw(best)} of ${pool.length}</div><div class="s">${esc(best.n)}, ${fmt(best[S.r],R.f)}</div></div>`:`<div class="tile"><div class="k">${bn}</div><div class="v">None</div><div class="s">No ${bn} in this group with ${S.m}+ games</div></div>`,
    `<div class="tile"><div class="k">League average</div><div class="v">${fmt(avg,R.f)}</div><div class="s">${esc(R.l.toLowerCase())}, ${G.label.toLowerCase()} with ${S.m}+ games</div></div>`,
    `<div class="tile"><div class="k">${bn} in the top 25%</div><div class="v">${bufs.filter(r=>rk.get(r)<=Math.ceil(pool.length/4)).length} of ${bufs.length}</div><div class="s">${esc(bufs.filter(r=>rk.get(r)<=Math.ceil(pool.length/4)).map(r=>r.n.split(" ").slice(-1)[0]).join(", ")||"—")}</div></div>`].join("");
  // chart
  $("ctitle").textContent=`${R.l} vs. ${Y.l.toLowerCase()}`; $("csub").textContent=`Each dot is one player. ${R.hi?"Further right is better.":"Further left is better."} Hover or tap a dot for the player.`;
  const pts=view.filter(r=>r[S.y]!=null), W=1100,H=440,L=64,Rm=20,T=16,B=52;
  if(pts.length<2){$("chart").innerHTML='<p class="small">Not enough players with both numbers. Loosen the filters.</p>'}else{
  const xs=pts.map(r=>r[S.r]),ys=pts.map(r=>r[S.y]); let x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
  const px=(x1-x0)*0.06||1,py=(y1-y0)*0.08||1; x0-=px;x1+=px;y0-=py;y1+=py;
  const X=v=>L+(W-L-Rm)*(v-x0)/(x1-x0), Yp=v=>H-B-(H-T-B)*(v-y0)/(y1-y0);
  const tick=(a,b)=>{const st=Math.pow(10,Math.floor(Math.log10((b-a)/5)));const m=[1,2,5,10].find(m=>(b-a)/(st*m)<=6);const s=st*m,out=[];for(let v=Math.ceil(a/s)*s;v<=b;v+=s)out.push(+v.toFixed(6));return out};
  let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(R.l)} against ${esc(Y.l)} for ${pts.length} players, ${bn} in blue">`;
  for(const v of tick(x0,x1))svg+=`<line x1="${X(v)}" x2="${X(v)}" y1="${T}" y2="${H-B}" stroke="#EEF0F3"/><text x="${X(v)}" y="${H-B+18}" font-size="12" fill="#5B6270" text-anchor="middle">${fmt(v,R.f==="signed"?"f1":R.f)}</text>`;
  for(const v of tick(y0,y1))svg+=`<line x1="${L}" x2="${W-Rm}" y1="${Yp(v)}" y2="${Yp(v)}" stroke="#EEF0F3"/><text x="${L-8}" y="${Yp(v)+4}" font-size="12" fill="#5B6270" text-anchor="end">${fmt(v,Y.f==="signed"?"f1":Y.f)}</text>`;
  if(avg>=x0&&avg<=x1)svg+=`<line x1="${X(avg)}" x2="${X(avg)}" y1="${T}" y2="${H-B}" stroke="#8A919C" stroke-dasharray="4 4"/><text x="${X(avg)+6}" y="${T+12}" font-size="12" fill="#5B6270">League average</text>`;
  const order=[...pts.filter(r=>r.t!=="BUF"),...pts.filter(r=>r.t==="BUF")];
  order.forEach((r,i)=>{const b=r.t==="BUF";svg+=`<circle data-i="${i}" cx="${X(r[S.r]).toFixed(1)}" cy="${Yp(r[S.y]).toFixed(1)}" r="${b?6:4}" fill="${b?"#00338D":"#B7BDC7"}" fill-opacity="${b?1:.8}" stroke="#fff" stroke-width="${b?2:0}"/>`});
  pts.filter(r=>r.t==="BUF").sort((a,b)=>rk.get(a)-rk.get(b)).slice(0,4).forEach(r=>{svg+=`<text x="${X(r[S.r])+9}" y="${Yp(r[S.y])-8}" font-size="13" font-weight="700" fill="#00338D">${esc(r.n.split(" ").slice(-1)[0])}</text>`});
  svg+=`<text x="${(L+W-Rm)/2}" y="${H-10}" font-size="13" fill="#14171F" text-anchor="middle">${esc(R.l)}</text><text transform="translate(16 ${(T+H-B)/2}) rotate(-90)" font-size="13" fill="#14171F" text-anchor="middle">${esc(Y.l)}</text></svg>`;
  $("chart").innerHTML=svg; $("chart").onpointermove=e=>{const c=e.target.closest("circle");const tip=$("tip");if(!c){tip.hidden=true;return}const r=order[+c.dataset.i];
    tip.innerHTML=`<b>${esc(r.n)}</b> · ${r.t} · ${r.pos}<br>${esc(R.l)}: ${fmt(r[S.r],R.f)} (${rkw(r)})<br>${esc(Y.l)}: ${fmt(r[S.y],Y.f)}<br>${r.gp} games`;
    const bx=$("chart").parentElement.getBoundingClientRect();tip.hidden=false;tip.style.left=Math.min(e.clientX-bx.left+12,bx.width-250)+"px";tip.style.top=(e.clientY-bx.top+12)+"px"};
  $("chart").onpointerleave=()=>{$("tip").hidden=true}}
  // table
  const sk=S.sk&&G.cols.some(c=>c.k===S.sk)?S.sk:S.r, sc=col(sk);
  const tv=[...view].sort((a,b)=>{const x=a[sk],y=b[sk];if(x==null)return 1;if(y==null)return -1;return (sc.hi?y-x:x-y)*(S.sd<0?1:-1)||rk.get(a)-rk.get(b)});
  $("ttitle").textContent=`Ranked by ${R.l.toLowerCase()}`;
  const tcols=[col(S.r),...G.cols.filter(c=>c.k!==S.r)];
  const head=`<thead><tr><th data-k="__rk">Rank</th><th data-k="__n">Player</th><th data-k="__t">Team</th><th data-k="__p">Pos.</th>${tcols.map(c=>`<th data-k="${c.k}" class="${c.k===sk?"on":""}">${esc(c.l)}${c.k===sk?(S.sd<0?" ▾":" ▴"):""}</th>`).join("")}</tr></thead>`;
  const row=r=>`<tr class="${r.t==="BUF"?"buf":""}"><td class="rk">${rks(r)}</td><td><a href="${r.u}">${esc(r.n)}</a>${r.o?" *":""}</td><td>${r.t}</td><td>${r.pos}</td>${tcols.map((c,i)=>`<td${i===0?' class="key"':""}>${fmt(r[c.k],c.f)}</td>`).join("")}</tr>`;
  const N=25; let body;
  if(S.all||S.b||tv.length<=N){body=tv.map(row).join("")}else{const top=tv.slice(0,N),rest=tv.slice(N).filter(r=>r.t==="BUF");body=top.map(row).join("")+(rest.length?`<tr class="sep"><td colspan="${G.cols.length+4}">More ${bn}</td></tr>`+rest.map(row).join(""):"")}
  $("table").innerHTML=head+`<tbody>${body}</tbody>`;
  const shown=S.all||S.b||tv.length<=N?tv.length:Math.min(N,tv.length)+tv.slice(N).filter(r=>r.t==="BUF").length;
  $("showing").textContent=`Showing ${shown} of ${tv.length}`; $("more").textContent=S.all?"Show fewer":"Show all"; $("more").hidden=S.b||tv.length<=N;
  $("table").querySelectorAll("th").forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(k.startsWith("__")){S.sk=null;S.sd=-1}else if(S.sk===k)S.sd*=-1;else{S.sk=k;S.sd=-1}render()});
  $("foot").textContent=`${D.meta.label} Ranks are among ${G.label.toLowerCase()} with ${S.m}+ games and a number for that stat; the team and range filters don't change them. Ranks use the rounded numbers shown, so they can differ by a spot from the player cards. A dash means too few attempts to count. * Also played for another team this season. ${S.s==="nhl"?"Chances: what a player's shots were worth in goals, based on where and how each was taken. Goals vs. chances: goals scored minus that total. Goals saved vs. an average goalie: goals an average goalie would have allowed on the same shots, minus goals allowed.":"Points added per dropback: how much each pass play, sack or scramble changed the expected points of the drive, on average."} Every number comes from the same files as our player cards.`;
  writeHash();
}
document.querySelector(".seg").onclick=e=>{const b=e.target.closest("button");if(!b)return;S={...S,s:b.dataset.s,g:null,t:"all",m:null,r:null,y:null,lo:"",hi:"",sk:null,sd:-1,all:0};render()};
$("groups").onclick=e=>{const b=e.target.closest("button");if(!b)return;S.g=b.dataset.g;S.r=null;S.y=null;S.m=null;S.lo="";S.hi="";S.sk=null;S.all=0;render()};
$("team").onchange=e=>{S.t=e.target.value;render()}; $("mingp").onchange=e=>{S.m=e.target.value;render()};
$("rank").onchange=e=>{S.r=e.target.value;S.lo="";S.hi="";S.sk=null;render()}; $("ystat").onchange=e=>{S.y=e.target.value;render()};
$("lo").onchange=e=>{S.lo=e.target.value;render()}; $("hi").onchange=e=>{S.hi=e.target.value;render()};
$("bufonly").onchange=e=>{S.b=e.target.checked?1:0;render()}; $("more").onclick=()=>{S.all=S.all?0:1;render()};
$("share").onclick=async()=>{writeHash();try{await navigator.clipboard.writeText(location.href);$("share").textContent="Link copied"}catch(_){$("share").textContent="Copy the address bar"}setTimeout(()=>$("share").textContent="Copy link to this view",2000)};
readHash(); render();
})();
"""


def build_compare(site, page, slugs, css_v):
    """Write site/compare/. `page` is build.page; `slugs` is build.card_slugs()."""
    out = site / "compare"
    out.mkdir(exist_ok=True)
    nhl, nm = nhl_rows(slugs)
    (out / "nhl.json").write_text(json.dumps(dict(meta=nm, rows=nhl), separators=(",", ":")))
    try:
        nfl, fm = nfl_rows()
    except FileNotFoundError:
        nfl, fm = [], dict(label="")
    (out / "nfl.json").write_text(json.dumps(dict(meta=fm, rows=nfl), separators=(",", ":")))
    js = JS.replace("__CFG__", json.dumps(config())).replace("__V__", css_v)
    body = f"<style>{CSS}</style>{PAGE}<script>{js}</script>"
    (out / "index.html").write_text(page("Compare Buffalo players to the league | Buffalo Quant Desk", body, "Compare", 1,
                                         desc="Filter and rank every Sabre and Bill against the league.", full=True))
    return len(nhl), len(nfl)
