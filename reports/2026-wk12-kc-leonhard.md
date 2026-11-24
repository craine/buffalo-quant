# Greg Rousseau leads the NFL in pressures. The Bills still have fewer sacks than a year ago

**If it feels like Buffalo's pass rush is having a monster year, the pressure part is true. Through nine games under new coordinator Jim Leonhard, the Bills
have 107 quarterback pressures, tied for 3rd in the NFL, and Greg Rousseau has 37, the most of any player through Week 10. The sacks are another story: Buffalo has
21, four fewer than at the same point last season, and ranks 20th in sacks per dropback. Buffalo is getting to the quarterback. It just isn't bringing him down as often.
On Thursday it faces Patrick Mahomes, who has been good this season whether teams send extra rushers or not.**

*Part 1 of our Bills-Chiefs series. Data: the Bills' first nine games of each season (Weeks 1-10; Week 11 isn't fully charted yet), plus all of Denver's 2025 season.
A "dropback" is any pass play: completions, incompletions, sacks and scrambles.*

![Buffalo's pass rush gets pressure like a top-five defense. The sacks haven't kept up](bills-kc-wk12-leonhard.png)

## The pressure is real

A pressure is any play where a defender hurries, hits or sacks the quarterback, as charted by Pro Football Reference. Buffalo has 107 pressures on
375 opponent dropbacks, about 29 for every 100. That ranks 4th in the NFL (league average: about 25).
It's about where Buffalo was at this point last year (29 for every 100, also 4th), but on more plays: 107 pressures now against 84 then.

The biggest share is Rousseau's: 37 of the 107, about 35%. His 37 lead the league (Maxx Crosby is next with 35, in one more game). His best through nine games in any
earlier season was 23. He has 8 sacks in those nine games and added 2 more against Miami, for 10.

## The sacks aren't

Through nine games last season, Buffalo had 25 sacks, 5th in the league per dropback. This season it has 21, 20th.

The gap is in how often pressure becomes a sack. Last year at this point, 30% of Buffalo's pressures ended in a sack. This year it's 20%
(28th in the league; the league average is 26%). And outside of Rousseau, the sacks are spread thin: the rest of the defense has 13
in nine games, and nobody else has more than 3.5 (TJ Parker).

Last year is a warning about fast starts. Through nine games, Buffalo was 4th in pressure rate and 5th in sacks per dropback. Over the
last eight games it fell to 28th in pressure and 27th in sacks, with 11 sacks. It finished with 36, 14th in the league per dropback.

## Where Leonhard comes in

Before Buffalo, Leonhard was Denver's defensive backs coach and pass game coordinator, and in 2025 its assistant head coach. Vance Joseph was the coordinator.
Denver's pass defense had a clear style:

- **Man coverage.** Denver played man on 44% of dropbacks, the most in the NFL. The league average was 31%. Its most common
  look was one deep safety with everyone else in man (31% of dropbacks).
- **Extra rushers.** Denver sent five or more on 32% of dropbacks, 6th in the league.
- **Sacks.** Denver got a sack on 9.8% of dropbacks, 1st in the NFL.

This season, Buffalo sends five or more rushers on 35% of dropbacks (8th in the league), up from 24%
(22nd) at this point last season. Teams across the league are sending more this year (27% at this point last season, 31% now), but Buffalo's jump is more than twice as big.
Denver also got pressure on about 33 of every 100 dropbacks last year, more than Buffalo does now.
We can't tell yet whether Buffalo plays as much man coverage as Denver did. That data for 2026 isn't out.

## The one time Denver faced Mahomes

Denver and Kansas City met twice in 2025, and Denver won both. But Mahomes played in only one of them: Week 11, a 22-19 Denver win.
He didn't play after Week 15, so the Week 17 game (20-13 Denver) was against a backup, and we leave it out.

Against Mahomes, Denver played man on 33% of his 49 dropbacks. That's below its 44% for the season, but it's about what Denver was doing
by then: after playing man on 56% of dropbacks through Week 8, it dropped to 35% from Week 9 on. It sent five or more rushers 27% of the time.
Mahomes was held to +0.02 points per dropback, below his 2025 average of +0.17.
(Points per dropback is how much each pass play helped the offense, on average, measured in points.)
One game is a small sample, and it can't tell us which part of Denver's plan worked.

## Why it matters Thursday

Kansas City's passing game ranks 6th this season at +0.17 points per dropback. Against five or more rushers, Mahomes has averaged
+0.14 points per dropback; against four or fewer, +0.18. That's a small sample (93 and 234 dropbacks). Extra rushers cost him about what they
cost every offense (league-wide: +0.06 against four or fewer, +0.01 against five or more). The difference is that even against extra rushers, he's
far above the league. When Buffalo does send five or more, it gets a sack on 6.8% of those dropbacks, 25th in the league
(league average: 8.6%).

Tomorrow: what has slowed Mahomes down over the last four seasons.

## How we measured it

Pressures and sacks credited to players come from Pro Football Reference's charting, which marks every hurry, quarterback hit and sack. We add them up by
team and divide by the opponents' dropbacks. Team sack totals come from the official play-by-play.
FTN, a charting service, records how many players rushed the passer on every NFL play. For example, on a Week 2 sack of Jared Goff
(by Greg Rousseau), FTN counted 5 Bills rushers. We count every dropback (passes, sacks and scrambles) and divide.
Man or zone coverage comes from charting published by nflverse; it's out through 2025 only. "Points per dropback" measures how much each pass play moved
the offense closer to or further from scoring, in points. Above zero helps the offense; below zero hurts it. It's the same measure we use in every Bills story.
Plays wiped out by penalties are left out.

## For the stat-heads

- Dropbacks: `pass == 1`, EPA not null, no two-point tries, spikes or no-plays; regular season. 2025 full season; 2026 weeks 1-10 (all final, FTN coverage 100%).
- FTN's 2026 blitzer count equals rushers minus four (zero when four or fewer rush) on all but 1 of 11,091 dropbacks (89% in 2025), so we use rushers only. Two FTN rows with impossible rusher counts are dropped.
- DEN 2025: 693 dropbacks; 5+ rushers 0.322 (6); man wk 1-8 0.557, wk 9+ 0.355; 5+ wk 9+ 0.306; sack rate 0.098 (1); EPA/db -0.078 (5).
  Participation: man 0.444 (1st), pressure 0.345 (2).
- BUF 2025: 530; 5+ 0.251 (21); sack 0.068 (14); EPA/db -0.067 (8);
  man 0.313 (14; first nine games 0.298); 5+ first nine games 0.239 (22; league 0.268); pressure 0.338 (5).
- Pressures: PFR `def_pressures` summed by team, weeks 1-10 (every game charted). BUF 2026 107 (3), 0.285/db (4);
  BUF 2025 same weeks 84 (10), 0.295 (4); 2025 full 132, 0.249 (11). League 0.245 (2026), 0.222 (2025 same weeks), 0.233 (2025 full). DEN 2025 0.329.
- Sacks per pressure (PFR sacks / PFR pressures): BUF 2026 0.196 (28); 2025 same weeks 0.298; league 2026 0.262.
- Sacks (play-by-play): BUF 2026 wk 1-10 21 (20 per dropback); 2025 same weeks 25 (5); 2025 full 36 (20 in total, 14 per dropback); 2025 weeks 11-18 pressure 0.196 (28), sacks 0.045 (27). Through Week 11 (Miami): 23.
- Rousseau: 37 pressures wk 1-10 in 9 games (1st; Maxx Crosby 35 in 10); PFR pressures count each credited player, so a shared sack is a pressure for both; previous best through Week 10 23; sacks 8 (wk 1-10), 10 through Week 11.
- BUF 2026 on 5+ rusher dropbacks: sack rate 0.068 on 133 (25); league 0.086.
- BUF 2026 wk 1-10: 375; 5+ 0.355 (8); change vs. first nine games of 2025 +0.116 vs league +0.045; full-season basis +0.104 vs +0.046 (24 of 32 teams up); sack 0.056 (20); EPA/db +0.012 (11).
- League 2026 wk 1-10: 5+ 0.313; sack 0.065; EPA/db vs 4 or fewer +0.065, vs 5+ +0.010.
- League 2025: 5+ 0.267; sack 0.065; man 0.308; pressure 0.298.
- DEN vs. KC, 2025_11_KC_DEN: 49 Mahomes dropbacks, EPA/db +0.017; man 0.327, pressure 0.306, 5+ 0.265. Mahomes 2025 EPA/db +0.165 (587, all of his 2025 dropbacks including his partial Week 15).
- KC 2026 offense EPA/db +0.167 (6). Mahomes vs 5+ rushers +0.137 (n 93); vs 4 or fewer +0.179 (n 234). Small samples.
- Leonhard's Denver titles: defensive backs coach and pass game coordinator (2024); assistant head coach and pass game coordinator (2025). Coordinator: Vance Joseph.
