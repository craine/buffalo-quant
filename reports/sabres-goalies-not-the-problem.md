# The Sabres' goalies aren't the problem. They're just not the bailout anymore.

**Finding: Ukko-Pekka Luukkonen's .874 save percentage looks like a collapse, but the shots in front of him
would beat an average goalie 11.9% of the time. He is -1.9 goals against expectation and
Colten Ellis is +2.2. Last year Sabres goalies were +24.4, and half of that left with Alex Lyon.**

*2026-27 is 15 games (7-5-3), a small sample. 261 shots for Luukkonen, 147 for Ellis.*

![Goalies](sabres-goalies.png)

| Season | Goalie | Shots faced | Save % | Expected save % | Goals saved above expected |
|---|---|---|---|---|---|
| 2023-24 | Ukko-Pekka Luukkonen | 1470 | 0.910 | 0.905 | +7.7 |
| 2023-24 | Devon Levi | 666 | 0.899 | 0.897 | +1.8 |
| 2023-24 | Eric Comrie | 254 | 0.874 | 0.887 | -3.4 |
| 2024-25 | Ukko-Pekka Luukkonen | 1490 | 0.887 | 0.896 | -14.3 |
| 2024-25 | James Reimer | 597 | 0.899 | 0.895 | +2.5 |
| 2024-25 | Devon Levi | 258 | 0.872 | 0.906 | -8.9 |
| 2025-26 | Alex Lyon | 980 | 0.906 | 0.894 | +11.9 |
| 2025-26 | Ukko-Pekka Luukkonen | 931 | 0.909 | 0.896 | +11.9 |
| 2025-26 | Colten Ellis | 455 | 0.903 | 0.902 | +0.7 |
| 2026-27 | Ukko-Pekka Luukkonen | 261 | 0.874 | 0.881 | -1.9 |
| 2026-27 | Colten Ellis | 147 | 0.891 | 0.876 | +2.2 |

League save % on these shots: 0.896 in 2025-26, 0.890 in 2026-27. League expected save %:
0.892 and 0.890.

## What changed

- **Lyon is gone.** He was +11.9 on 980 shots last season and has not played for Buffalo in 2026-27.
- **Luukkonen is facing harder shots.** His expected save % is 0.881, against 0.896 last season;
  among 62 goalies with 100+ shots this season that is 9th-hardest.
- **Combined**, Sabres goalies are +0.3 this season after +24.4 last season.

Save percentage is one of the least stable stats in the sport (see the companion piece on last season). A
261-shot sample says very little about Luukkonen either way.

## Method and caveats

- Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, rebounds, rush chances and manpower, trained on 336,462 unblocked shots from 2023-24 to 2025-26. Tested on a season it never saw (2025-26), it beat a distance-and-angle model (AUC 0.77 vs 0.71). Empty-net shots are excluded.
- Goals saved above expected = expected goals on unblocked shots faced minus goals allowed. Blocked shots and
  empty-net situations are excluded; deflections and screens are only partly captured.
