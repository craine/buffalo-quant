# Golden Knights 4, Sabres 1: Buffalo earned more than one goal. Adin Hill didn't allow it

**Finding: The Sabres lost 4-1 Sunday, but they had the better chances: their shots were worth 3.9 goals to Vegas's 3.6.
Replay those same shots thousands of times and Buffalo wins about 46%, Vegas about 38%, and 16% end tied. The difference was
in goal. Adin Hill stopped 28 of 29 shots, about 2.9 goals better than an average goalie, one of the best goalie
nights in the league this season. Our pregame model gave Buffalo a 46% chance, a slight lean to Vegas, so it goes on the Ledger as a hit,
but not for the reason it expected: Vegas didn't win on chances, it won in goal.**

*One game, 2026-11-08, in Buffalo. Before the game, our model gave Vegas a 54% chance. [Our pregame story](sabres-vegas-pregame-nov-8.html).*

![Game flow](sabres-vgk-post-flow.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Add those up and you get what a team's
chances were worth in goals. Sunday's goals show the range: Marner's shot from 3 feet had a 47% chance of going in;
Hertl's second goal, from 34 feet, about 9%.
(The full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

Sunday, Buffalo's 50 unblocked shots were worth **3.9 goals**. Vegas's 41 were worth **3.6**. Buffalo scored once.
In our replays, the Sabres score one goal or fewer only 8% of the time on shots like these. (The replay's 46% for Buffalo
happens to match our pregame 46%; they're different numbers. One is before the game from season form, the other is after it from Sunday's shots.)

Two splits tell the rest of it. **At full strength, five on five, Buffalo won clearly: 3.2 to 1.8 in chances.** On special teams, Vegas won
1.8 to 0.7. And 1.0 of Vegas's 3.6 came in the final two minutes (7 shots), after it led 4-1 and the game was decided.
Leave those out and Vegas's chances were worth about 2.6.

## Period by period

| Period | Sabres chances, in goals | Golden Knights | What happened |
|---|---|---|---|
| 1st | 1.8 | 0.5 | Buffalo's best period. No goals. |
| 2nd | 0.7 | 1.4 | Vegas scores twice, the first one shorthanded. |
| 3rd | 1.4 | 1.7 | Beck Malenstyn makes it 2-1; Tomas Hertl answers twice. |

The first period was the Sabres' game to take: their chances were worth 1.8 goals to 0.5, and it stayed 0-0. The turn came in the second,
when Mitch Marner scored from 3 feet while Vegas was killing a penalty, a shot that goes in about 47% of the time from there.
Buffalo's power-play shots on the night were worth 0.5 goals, and it didn't score with the extra man. Vegas's shorthanded shots were
worth 0.8, more than that.

| Period | Time | Team | Scorer | Shot | Chance it went in |
|---|---|---|---|---|---|
| 2 | 12:17 | Golden Knights | Mitch Marner | wrist from 3 ft, shorthanded | 47% |
| 2 | 13:43 | Golden Knights | Jack Eichel | wrist from 16 ft | 15% |
| 3 | 4:26 | Sabres | Beck Malenstyn | wrist from 4 ft | 44% |
| 3 | 5:43 | Golden Knights | Tomas Hertl | wrist from 10 ft | 20% |
| 3 | 10:00 | Golden Knights | Tomas Hertl | wrist from 34 ft | 9% |

## The goalie duel went the other way

Coming in, these two were at opposite ends. [Colten Ellis](../cards/colten-ellis.html) had saved 2.2 more goals than an average goalie
would have on the same shots this season (6 games). [Adin Hill](../cards/adin-hill.html) was 1.9 worse than average (8 games). Small samples, both.
(Our pregame story had Hill at -1.8; shot values are re-tuned slightly as each night's games come in.)

Sunday flipped it. Hill faced Buffalo shots worth 3.9 goals and allowed 1: **+2.9**. Only 12 of the 586 goalie games in the NHL this
season have been better. Ellis faced Vegas shots worth 3.6 goals and allowed 4: **-0.4**, a little below average, not a bad night.

![Goalie nights](sabres-vgk-post-goalies.png)

**Why goalies aren't in our prediction model.** Before Sunday's game we tested it: we split past seasons in half and checked whether a goalie's
first half told us about his second half. It barely did, much less than a team's chances allowed did. And adding the starting goalie didn't make our
game predictions any better. Sunday is an example: the goalie with the worse numbers coming in had one of the best nights in the league. In one afternoon,
Hill went from -1.9 for the season to +1.0 (9 games now); Ellis went from +2.2 to +1.8 (7 games).

## Vegas got in the way

Buffalo tried 78 shots; Vegas blocked 28 of them. Only 7 of 556 team-games this season have had
28 or more blocked (the average is 15). Buffalo's 78 tries were 20 more than its average coming in
(58); 36% were blocked, against 27% league-wide. Blocked shots aren't in the 3.9. Vegas tried 51 shots and had 10 blocked.

## Receipts: our pregame call

Before the game we logged one call on the [Ledger](../ledger.html): **the Sabres win, at 46%.** Giving Buffalo less than half means our model
leaned Vegas, and Vegas won, so by our rule (the side we gave more than 50% wins) it's a hit. It was a near coin flip either way: our pregame story noted
that the model's slight leans, 50-55%, had won about half the time in testing. It stays up regardless.

We also grade every call with a simple score: the gap between the chance we gave and what happened, squared. Lower is better. Saying 46% on a
game Buffalo lost scores 0.21. A pure 50/50 guess would have scored 0.25. So slightly better than a coin flip, on this one game.
One game proves nothing either way; the point is the season-long record.

We're not taking a victory lap. The model expected a close game with Vegas slightly ahead. On chances it was close, but Buffalo was the one slightly ahead.
Vegas won because the goals didn't follow the chances, and the model can't see a goalie's hot night coming.

## What to take from it

- **Buffalo won the even-strength game.** Against a Vegas team that had allowed the 4th-fewest chances per game in the league before Sunday (2.6),
  the Sabres created 3.9 goals' worth (their average coming in was 3.1), 3.2 of it at five on five.
- **Special teams lost it.** The power play came up empty Sunday: 0.5 goals' worth of chances, and more than that given up the other way, including Marner's goal.
- **Ellis was a little below average, not bad.** He's still at +1.8 for the season (7 games).

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals.
  BUF 3.91 xG on 50 unblocked shots (29 on goal); VGK 3.65 on 41 (26 on goal).
- Replays: 20,000 simulations, each shot an independent coin flip with p = xG. BUF win 0.459, tie 0.159, loss 0.382.
- GSAx = xG on unblocked shots faced minus goals allowed. Hill +2.91 (29 shots on goal), Ellis -0.35. Hill's game ranks
  13th of 586 2026-27 goalie games. Season GSAx before/after: Hill -1.86/+1.05, Ellis +2.18/+1.83
  (this season only; shot values rescaled with games through Nov. 8, so Hill's pregame -1.8 reads -1.9 here).
- Strength: five on five BUF 3.19, VGK 1.84; all other situations BUF 0.72, VGK 1.81. Final two minutes (58:00 on): VGK 1.04 on 7 shots.
- Blocked attempts: attributed to the shooting team. Power play = 5v4, 5v3, 4v3 from the shooter's side.
- Ledger P0001: p = 0.46, outcome 0, Brier 0.2116; scored a hit because p < 0.5 and the event didn't happen. Model nhl-game-v0.1.
