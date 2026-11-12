# Sabres: who's running hot, and who's due

**Owen Power, Jack Quinn and Zach Benson are the Sabres running furthest ahead of their history, and Tage Thompson's 92-point pace is also ahead of his history, though his rating, 76 points per 82 games, is still the best on the team. At the other end, Ryan McLeod, Josh Doan, Josh Norris and Louis Crevier are furthest behind. Our rating, built from every season since 2023-24, projected last season's players better than going by their pace.**

*Numbers through November 10, the Sabres' first 17 games. Every number here is also on each player's
[card](../cards/).*

![Pace vs. history](sabres-hotcold-pace.png)

## Hot and cold, by the numbers

Seventeen games is about a fifth of a season. Over that stretch, a few lucky bounces can make a player look like a star or a bust. So
for each Sabre we compare two things: his **pace** (his points so far, stretched over 82 games) and his **rating**, our best guess at his
points per 82 games from here on, built from this season and the last three.

| Player | Points so far | Pace (per 82) | Rating (per 82) | If he plays all 65 remaining games |
|---|---|---|---|---|
| [Tage Thompson](../cards/tage-thompson.html) | 19 in 17 | 92 | 76 | 41 goals, 79 points |
| [Rasmus Dahlin](../cards/rasmus-dahlin.html) | 10 in 14 | 59 | 66 | 16 goals, 63 points |
| [Zach Benson](../cards/zach-benson.html) | 15 in 17 | 72 | 53 | 16 goals, 57 points |
| [Jack Quinn](../cards/jack-quinn.html) | 16 in 17 | 77 | 53 | 27 goals, 58 points |
| [Josh Norris](../cards/josh-norris.html) | 5 in 17 | 24 | 45 | 21 goals, 41 points |
| [Ryan McLeod](../cards/ryan-mcleod.html) | 3 in 15 | 16 | 43 | 11 goals, 37 points |
| [Josh Doan](../cards/josh-doan.html) | 4 in 17 | 19 | 42 | 20 goals, 38 points |
| [Noah Ostlund](../cards/noah-ostlund.html) | 10 in 17 | 48 | 39 | 16 goals, 41 points |
| [Owen Power](../cards/owen-power.html) | 14 in 17 | 68 | 39 | 8 goals, 45 points |
| [Peyton Krebs](../cards/peyton-krebs.html) | 9 in 17 | 43 | 35 | 8 goals, 36 points |
| [Jiri Kulich](../cards/jiri-kulich.html) | 3 in 10 | 25 | 34 | 15 goals, 30 points |
| [Mattias Samuelsson](../cards/mattias-samuelsson.html) | 10 in 17 | 48 | 33 | 7 goals, 36 points |
| [Konsta Helenius](../cards/konsta-helenius.html) | 3 in 11 | 22 | 32 | 10 goals, 29 points |
| [Olen Zellweger](../cards/olen-zellweger.html) | 6 in 16 | 31 | 26 | 10 goals, 27 points |
| [Louis Crevier](../cards/louis-crevier.html) | 1 in 15 | 6 | 19 | 3 goals, 16 points |
| [Beck Malenstyn](../cards/beck-malenstyn.html) | 3 in 17 | 14 | 17 | 6 goals, 16 points |
| [Zach Metsa](../cards/zach-metsa.html) | 2 in 15 | 11 | 15 | 2 goals, 14 points |

8 of these 17 Sabres are running ahead of their rating and 9 behind.

**Running hot.**

**Owen Power** is on pace for 68 points per 82 games; his rating says 39. Most of it is assists: 12 so far. Assists swing a lot over a few weeks, because they depend on teammates finishing.

**Jack Quinn** is on pace for 77 points per 82 games; his rating says 53. He has 9 goals on chances worth 6.1, so he's scored 2.9 more than his chances. Finishing like that rarely lasts.

**Zach Benson** is on pace for 72 points per 82 games; his rating says 53. Same story as Power: 13 of his 15 points are assists.

**Tage Thompson** is on pace for 92; his rating says 76. That would still be a big season: about 41 goals and
79 points if he plays every game.

**Due for more:** Ryan McLeod, on pace for 16 with a rating of 43; Josh Doan, on pace for 19 with a rating of 42; Josh Norris, on pace for 24 with a rating of 45; Louis Crevier, on pace for 6 with a rating of 19. Their ratings say more is coming.

## Where the rating comes from

**The source:** the NHL's own play-by-play for every game since the start of 2023-24: every goal, assist and shot, and where each shot came
from. **The math:** for each player we add up his points this season, plus his points from past seasons counted at half weight (and the season
before that at a quarter), plus a few games of an average player at his position, and divide by the games. That way a hot month can't take
over, but a player who's been good for years keeps his history. Goals come from the chances a player creates, adjusted slightly for how well
he's finished his chances over the years, because the chances carry over from season to season much better than the finishing does.

## How we checked it

We set the rating up using 2024-25 only. Then we went back to last season, 2025-26, stopped the clock after 17 games, and had the rating project
every NHL skater's rest of the season using only what was known at that point (632 players). Then we compared with what actually happened.

![The test](sabres-hotcold-test.png)

The rating's projection of a player's rest-of-season points missed by 6.4 on average. Going by his pace missed by 9.5; going by his
last season, 7.3. For goals alone, it missed by 3.3, against 5.3 for pace. It also beat both at the halfway point of the season,
though by less (4.3, against 4.8 for pace and 5.1 for last season), because by then a season's pace means more.

## What it means

- **Expect both groups to drift back toward their ratings.** The players running ahead of their ratings will probably slow down, and the ones behind will probably
  pick up. Not guaranteed: the rating misses by several points a player, and it can't see injuries or a player moving up or down the lineup.
- **Ice time is the missing piece.** We don't have shift data yet, so a player promoted to the top line looks the same to the rating as one
  stuck on the fourth. That's the next thing we're adding.
- **We'll keep score.** These projections are pinned to November 10. We'll check them against the rest of the season,
  the same way we grade every call on the [Ledger](../ledger.html).

## For the stat-heads

- Rating: `src/metrics/nhl_player_ratings.py`. Per-game rate = (current total + W x past totals + K x position mean) / (current GP + W x past GP + K),
  past seasons weighted W x 0.5^(age-1). Chances (xG): W=0.5, K=5; assists W=0.5, K=10.
  Goals = blended xG/game x (career goals + 40) / (career xG + 40). Points = goals + assists. Settings chosen on 2024-25 (history 2023-24).
- Test: checkpoint = date the median team had played 17 (or 41) games; skaters with 5+ games before and 10+ after; errors weighted by games after.
  2025-26 after 17 games, points per game MSE: rating 0.02253, pace 0.05312, last season
  0.02825, position average 0.08317; correlation with rest-of-season rate 0.87 vs.
  0.74 for pace.
- xG: our model, unblocked non-empty-net shots, rescaled per season so league xG = league goals. Shootouts excluded. No TOI (no shift data).
- Projected season totals = points to date + rate x 65 remaining games (82 minus the Sabres' 17 played); they assume he plays every game.
- Players shown: Sabres skaters with 10+ games through 2026-11-10.
