# As many chances, fewer goals: too early to call it a slump

**Finding: The Sabres are generating 3.00 expected goals per game, at least as many as last season's 2.89,
but scoring 2.87 a game, down from 3.12. Last season's finishing surplus came from players who are
still here: they scored +17.4 goals above expected then and are -3.8 this season. That
dip is within normal game-to-game variation.**

*2026-27 is 15 games (7-5-3), a small sample. League average: 2.99 expected goals per team per game this season.*

![Finishing](sabres-finishing.png)

## It isn't Alex Tuch

Tuch was last season's best finisher relative to his chances (32 goals on 23.1 expected, +8.9),
and he now plays for Washington. But the 13 skaters not on a Buffalo roster this season who shot for Buffalo last season combined for
49 goals on 47.5 expected (+1.5). Tuch's surplus was largely cancelled out by others who left.

2025-26 leaders, all situations, empty nets excluded:

| Player | Goals | Expected | Above expected | Gone? |
|---|---|---|---|---|
| Alex Tuch | 32 | 23.1 | +8.9 | Yes |
| Tage Thompson | 37 | 30.2 | +6.8 |  |
| Mattias Samuelsson | 12 | 5.9 | +6.1 |  |
| Noah Ostlund | 11 | 6.9 | +4.1 |  |
| Jason Zucker | 24 | 20.7 | +3.3 |  |

## This season's leading scorers

| Player | Goals | Expected | Above expected |
|---|---|---|---|
| Tage Thompson | 10 | 6.8 | +3.2 |
| Jack Quinn | 8 | 5.7 | +2.3 |
| Noah Ostlund | 4 | 4.5 | -0.5 |
| Olen Zellweger | 3 | 1.6 | +1.4 |
| Josh Norris | 2 | 2.8 | -0.8 |

The top of the lineup is still finishing (Tage Thompson and Jack Quinn are above expected), so the shortfall is
spread through the rest of the roster.

## How much of this is noise?

Returning players have taken 552 unblocked shots worth 42.8 expected goals this season. Random
variation alone on that many shots is about 6.1 goals either way, so
-3.8 is well within normal. It's the right thing to watch, not yet a slump.

## Why it matters going forward

Finishing above or below expected moves a lot from year to year (team shooting % has a year-to-year correlation
of about 0.3). The chances are still there. If finishing returns to normal, goals would likely follow, though
probably not to last season's level, which was itself above normal.

## Method and caveats

- Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, rebounds, rush chances and manpower, trained on 336,462 unblocked shots from 2023-24 to 2025-26. Tested on a season it never saw (2025-26), it beat a distance-and-angle model (AUC 0.77 vs 0.71). Empty-net shots are excluded. Values for 2023-24 to 2025-26 come from a model fit on those seasons; 2026-27 is out of sample. Each season is rescaled so league expected goals equal league goals (the raw model ran +3.0% hot in 2025-26), so above-expected numbers are relative to that season's league average.
- Individual expected goals count a player's own unblocked shots. "Not on a Buffalo roster" = dressed for Buffalo in 2025-26 and
  not yet in 2026-27, from game rosters; some may be injured or in the minors rather than gone. Per-game rates use all 15 games.
