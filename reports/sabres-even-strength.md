# At even strength, these Sabres look like last year's Sabres

**Finding: At 5-on-5 the Sabres are taking 52.0% of shot attempts (10th in the NHL) and
50.2% of expected goals, about where they were last season (49.3% and 50.8%).
Last year's difference was the bounces (5-on-5 PDO 1.021); this year's is special teams.**

*2026-27 is 15 games (7-5-3), a small sample.*

![5v5](sabres-5v5.png)

| Season | Shot-attempt share (rank) | Expected-goal share (rank) | 5v5 goals for-against | PDO |
|---|---|---|---|---|
| 2023-24 | 50.7% (16th) | 49.7% (19th) | 174-159 | 1.002 |
| 2024-25 | 49.7% (17th) | 47.3% (27th) | 185-184 | 1.005 |
| 2025-26 | 49.3% (16th) | 50.8% (14th) | 194-156 | 1.021 |
| 2026-27 | 52.0% (10th) | 50.2% (18th) | 30-29 | 0.992 |

## How the pieces fit

Taken together with the companion pieces: the 5-on-5 team hasn't changed much, the goalies have gone from well above
expected to about average, the finishing surplus left with Alex Tuch, and the penalty kill is allowing more. That's
how a 109-point team turns into a 17-point start in 15 games.

## Method and caveats

- Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, rebounds, rush chances and manpower, trained on 336,462 unblocked shots from 2023-24 to 2025-26. Tested on a season it never saw (2025-26), it beat a distance-and-angle model (AUC 0.77 vs 0.71). Empty-net shots are excluded.
- 5-on-5 only, empty nets excluded from goals and expected goals. Shot-attempt share counts blocked shots.
