# The Sabres' 50-win season was built on goals that weren't supposed to happen

**Finding: By the quality of chances they created and allowed, the 2025-26 Sabres played like a 91-point
team. They finished with 109: +18 points over expectation, the 2nd-largest gap in the NHL.
The extra came from goaltending and finishing, the two least repeatable of the stats we tested.**

*2026-27 is 15 games (7-5-3), a small sample.*

![Mirage](sabres-mirage.png)

## Where the extra points came from

| | Goals | Expected | Difference |
|---|---|---|---|
| Goals scored | 256 | 237.2 | +18.8 (finishing) |
| Goals allowed | 221 | 238.4 | +17.4 (goaltending) |

That is +36 goals better than their chances, all situations, empty nets excluded. Their expected-goal share
was 49.9% (17th in the NHL):
a league-average team by process.

## Why that was unlikely to repeat

Year-to-year correlation for all 32 teams, 2023-24 to 2025-26 (63 team pairs):

| Stat | What it measures | Correlation with next season |
|---|---|---|
| Expected-goal share | Chances created vs. allowed | 0.72 |
| PDO | Shooting % + save % | 0.31 |
| Shooting % | Finishing | 0.32 |
| Save % | Goaltending | 0.21 |

Shot quality carries over. Shooting and save percentages mostly don't. The Sabres' PDO was
1.019 (2nd in the NHL).
This season it is 0.983 (26th).

## What it says about this season

Through 15 games their expected-goal share is 47.8% (22nd) and they are -1.8
goals against their chances. In other words, the 2026-27 record looks a lot like what last year's underlying numbers
suggested, without the luck.

## Method and caveats

- Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, rebounds, rush chances and manpower, trained on 336,462 unblocked shots from 2023-24 to 2025-26. Tested on a season it never saw (2025-26), it beat a distance-and-angle model (AUC 0.77 vs 0.71). Empty-net shots are excluded. Values for 2023-24 to 2025-26 come from a model fit on those seasons; 2026-27 is out of sample. Each season is rescaled so league expected goals equal league goals (the raw model ran +3.0% hot in 2025-26), so above-expected numbers are relative to that season's league average.
- Expected points: a straight-line fit of points on xG differential per game across all 96 team-seasons, 2023-24 to
  2025-26 (correlation 0.77; typical miss 9.7 points). "Expected" is a model estimate, not a guarantee. Points also
  depend on overtime and shootout results and on empty-net goals, which this fit doesn't model.
- Goaltending here = expected goals against minus goals against on unblocked shots, empty nets excluded.
