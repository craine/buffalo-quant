# The Sabres' penalty kill is where this season is leaking

**Finding: Shorthanded, the Sabres are allowing 0.80 expected goals per game, up from
0.59 last season (25th of 32, where 1st is best). They've allowed 16 power-play
goals in 15 games, 30th in the league. Last season's kill ranked 4th in goals allowed.**

*2026-27 is 15 games (7-5-3), a small sample.*

![Penalty kill](sabres-pk.png)

| Season | PP goals allowed | Expected | Goals allowed/game (rank) | Expected/game (rank) | League expected/game |
|---|---|---|---|---|---|
| 2023-24 | 49 | 49.3 | 0.60 (16th) | 0.60 (22nd) | 0.60 |
| 2024-25 | 57 | 46.6 | 0.70 (30th) | 0.57 (24th) | 0.53 |
| 2025-26 | 39 | 48.1 | 0.48 (4th) | 0.59 (11th) | 0.62 |
| 2026-27 | 16 | 12.1 | 1.07 (30th) | 0.80 (25th) | 0.68 |

Ranks: 1 = fewest allowed. The league as a whole is allowing more shorthanded chances this season
(0.68 per game, up from 0.62), so not all of the rise is Buffalo's, but the Sabres are
+0.13 per game worse than average. It isn't unprecedented, either: in 2024-25 the kill ranked
30th in goals allowed. Part of this season's damage is bad luck (16 goals on 12.1 expected),
but the chances allowed are also up, and that part is less likely to fix itself.

## Method and caveats

- Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, rebounds, rush chances and manpower, trained on 336,462 unblocked shots from 2023-24 to 2025-26. Tested on a season it never saw (2025-26), it beat a distance-and-angle model (AUC 0.77 vs 0.71). Empty-net shots are excluded.
- Shorthanded situations are 4-on-5, 3-on-5 and 3-on-4. Per-game rates do not adjust for how often the team is
  shorthanded; time-on-ice data is not in our dataset yet.
