import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from src.ledger import points_model as pm
K,PK=60,0.7
f=pm.build_frame(range(2019,2027),k=K,prior_keep=PK)
# naive baselines, pregame only
sc=f[["game_id","season","week","team","opp","score"]]
def todate(s,w):
    x=sc[(sc.season==s)&(sc.week<w)]
    return x.groupby("team").score.mean(), x.groupby("opp").score.mean(), x.score.mean()
b1=[];b2=[];b3=[]
for (s,w),grp in f.groupby(["season","week"]):
    ppg,allow,lg=todate(s,w)
    if np.isnan(lg): lg=sc[sc.season==s-1].score.mean()
    for r in grp.itertuples():
        b1.append(lg); o=ppg.get(r.team,lg); a=allow.get(r.opp,lg)
        b2.append(o); b3.append(o+a-lg)
f["b_league"]=b1; f["b_team_ppg"]=b2; f["b_simple"]=b3
f.to_parquet("/tmp/pm_frame.parquet")
tr=f[f.season<=2023]; coef,res=pm.fit(tr)
print("coef a,b,home:",coef.round(3)," train MAE",np.abs(res).mean().round(2)," resid sd",res.std().round(2))
for name,te in [("2024",f[f.season==2024]),("2025",f[f.season==2025]),("2026 wk2-8",f[f.season==2026]),
                ("2024-26 weeks 7+",f[(f.season>=2024)&(f.week>=7)])]:
    p=pm.predict(coef,te.raw,te.home); e=lambda v: np.abs(te.score-v).mean()
    print(f"{name:18s} n={len(te):4d} model {e(p):.2f} | league avg {e(te.b_league):.2f} | team ppg {e(te.b_team_ppg):.2f} | ppg+opp allowed {e(te.b_simple):.2f}")
# calibration on test 2024-26
te=f[f.season>=2024]; p=pm.predict(coef,te.raw,te.home).to_numpy()
rows=[]
for th in (14,17,20,21,24,27,28,30):
    for pi,y in zip(p,te.score): rows.append((pm.prob_at_least(pi,th,res), y>=th))
c=pd.DataFrame(rows,columns=["p","y"]); c["bucket"]=pd.cut(c.p,[0,.2,.4,.6,.8,1.0],include_lowest=True)
print(c.groupby("bucket",observed=True).agg(n=("y","size"),said=("p","mean"),happened=("y","mean")).round(3))
brier=((c.p-c.y)**2).mean(); base=((c.y.mean()-c.y)**2).mean()
print("Brier model",round(brier,4)," Brier always-league-rate",round(base,4))
