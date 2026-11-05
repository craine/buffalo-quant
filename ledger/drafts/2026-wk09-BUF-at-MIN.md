# DRAFT Ledger card: Bills at Vikings, MNF, Nov 9 2026, 8:15 PM ET (dome)

Not logged. Charlie approves, edits or kills each call, then run `python3 -m src.ledger.log_card`.
Model: v0.1-locshift (`src/ledger/model_v01.py`). Probabilities are analysis, not wagering advice.

The matchup: Bills offense is #1 in EPA/play (+0.179). Vikings defense is #1 in EPA/play allowed
(-0.167), #1 in dropback EPA allowed, #1 in sack rate, #1 in points per drive. Vikings offense is
28th in EPA/play and 25th in dropback EPA. All through week 8, 7 games each.

| # | Call | Prob | Why it matters |
|---|---|---|---|
| 1 | Vikings post **positive EPA per dropback** vs. the Bills | **58%** | The thesis test. Minnesota's passing game is 25th; if it still finds room, the pass defense problem is real. |
| 2 | Vikings **designed-rush EPA stays below zero** | **81%** | Does the run-defense fix hold? Minnesota's run game is 28th. |
| 3 | Bills **sack rate of 6%+** | **62%** | Bills pass rush is 25th, but Minnesota allows sacks at the 3rd-highest rate. Something gives. |
| 4 | Bills **dropback EPA under +0.15** | **68%** | Best offense vs. best defense. Allen's season average is +0.30; this says Minnesota cuts it roughly in half. |

Model outputs behind each call (expected game value, then P):
1. MIN dropback EPA expected +0.037 -> P(>0) = 0.579
2. MIN rush EPA expected -0.154 -> P(>0) = 0.190, so P(<0) = 0.810
3. BUF sack rate expected 7.4% -> P(>=6%) = 0.620
4. BUF dropback EPA expected +0.031 -> P(>0.15) = 0.318, so P(<0.15) = 0.682

Caveats: 7-game samples on both sides, halfway regression to league average. Call 4's expected
value (+0.031) looks low for a +0.30 offense; it's the model averaging two extremes, and the 68%
leans on that. It's the call I'd trust least.
