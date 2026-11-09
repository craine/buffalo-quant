"""Out-of-sample test of Ledger model v0.1 on the week-9 call types. Logic lives in src/ledger/model_v01_backtest.py."""
import sys
sys.path.insert(0, ".")
from src.ledger.model_v01_backtest import CALLS, run, summary

if __name__ == "__main__":
    for metric, t in CALLS:
        s, cal = summary(run(metric, t))
        print(f"{metric} > {t}: n={s['n']} Brier model {s['brier']:.4f} vs base rate {s['brier_base']:.4f} | happened {s['rate']:.3f}")
        print(cal.round(3).to_string())
