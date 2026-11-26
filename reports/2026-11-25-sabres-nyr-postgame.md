# Sabres 5, Rangers 1: a hot week cancels out a cold start

**Through 21 games the Sabres had scored 57 goals on chances worth 64, and allowed 72 on chances worth 69. Four games later,
both running totals are back near zero. Wednesday was the latest: even chances, 2.5 to 2.3, and a 5-1 win. A hot four games has
cancelled out the cold start, and the hot streak is no more likely to last than the cold start was. Underneath, the Sabres get 48% of the chances
in their games, 22nd in the NHL.**

![The Sabres' early bad luck has evened out](sabres-nyr-nov25-postgame.png)

## The game

Both teams had 30 shots on goal. Buffalo's goals came from Rasmus Dahlin, Josh Norris, Zach Benson, Jack Quinn and Jiri Kulich. New York's lone goal was Vladislav Gavrikov's shot from 56 feet,
a chance worth about 2% of a goal. Ukko-Pekka Luukkonen stopped everything else, about 1.3 goals better than the chances he faced.

At the other end, the Rangers started Joonas Korpisalo, who has been taking turns with Dylan Garand since early November. Korpisalo had saved about
2.8 more goals than an average goalie would have in his first 3 games.
On Wednesday he allowed 5 on chances worth 2.5.

## How we count chances

Every shot that isn't blocked gets a value: the share of similar shots that go in, based on distance, angle, shot type and whether it's a rebound or rush.
Buffalo's closest goal came from 13 feet, a chance worth about 12%. Add up a team's shots and you get what its chances
were worth in goals. Score more than that and you finished well; allow fewer and your goalie saved some.

**How we checked it.** The model's values are set so that, across the league, chances add up to goals: this season its raw values came to
2,367 goals and teams scored 2,370 on those shots, so we scaled them by 1.001. And in the [Tampa recap](sabres-lightning-postgame-nov-22.html)
we checked what carries over: a team's share of chances in the first half of a season predicts the second half far better than its finishing or goaltending.

## The season, evened out

| | Games | Goals | Chances worth | Goals allowed | Chances against worth |
|---|---|---|---|---|---|
| First 21 games | 21 | 57 | 64.1 | 72 | 68.6 |
| Last 4 games | 4 | 18 | 10.4 | 10 | 12.3 |

*Goals in the table leave out empty-net and shootout goals.*

Over the whole season, the Sabres have now scored 0.5 more goals than their chances were worth, and their goalies
have allowed 1.0 more than expected. Both are close to zero.
Not counting empty-net or shootout goals, they've been outscored 75-82, almost exactly what their chances say (74.5 to 81.0).

## What to expect

Finishing and goaltending streaks come and go; a team's chances carry over far better than either. The Sabres get 48% of the chances,
22nd in the league. Expect them to look like that team, a little below average, rather than the one that
scored 20 in four games.

## Receipts

- **Our preview** said the Rangers' poor finishing (30th in the NHL) probably wouldn't last and their goaltending would probably cool off.
  It also said one game wouldn't settle either. On Wednesday New York scored 1 goal on chances worth 2.3, and Korpisalo allowed
  5 on chances worth 2.5. Both are season-long calls, and we'll keep tracking them.
- **The Ledger** gave the Sabres 49%. They won, so the call leaned the wrong way and counts as a miss, though the chances themselves came out
  close to even. On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored 0.26. Our record is 13 of 22.

## For the stat-heads

- Rangers starters since Nov. 7 (first goalie faced each game): Korpisalo, Garand, Korpisalo, Garand, Korpisalo, Garand, Korpisalo.
- xG model: unblocked non-empty-net shots, rescaled so 2026-27 league xG equals league goals through 2026-11-25 (factor 1.001).
- Game: xGF 2.47, xGA 2.35; all situations. Korpisalo GSAx -2.53 on the night, +2.79 in 3 games before it.
- Season (25 games): xGF% 0.479 (22nd); finishing (G - xG) +0.02 per game (15th); GSAx -0.04 per game (18th).
- Ledger P0023: p = 0.49, outcome 1, Brier 0.2601. "Right" = the side above 50% won.
