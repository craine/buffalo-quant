import sys, time; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from src.ledger import points_model as pm
t=time.time()
grid={}
for k in (30,60,120):
    for pk in (0.3,0.5,0.7):
        f=pm.build_frame(range(2019,2023),k=k,prior_keep=pk)
        coef,res=pm.fit(f); grid[(k,pk)]=np.abs(res).mean()
        print(k,pk,round(grid[(k,pk)],3), round(time.time()-t))
