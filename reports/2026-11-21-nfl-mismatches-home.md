# Much better NFL teams win 9 in 10 at home, 7 in 10 on the road. Rivalry games are no closer.

**Since 1999, NFL teams that were much better than their opponent won 88% of the time at home and 73% on the road.
Division games were no different. When the better team lost, it was usually close. Sunday's Bills-Dolphins game is in Buffalo.**

*This follows our story on [how often the much better NFL team loses](nfl-mismatches.html), using the same 5,205 regular-season games from 1999 to 2025. 
"Much better" means 17 or more points a game better by point differential (points scored minus points allowed, per game) going into the game. We don't use betting lines.*

![Home vs road](nfl-mismatch-home.png)

## Home field

Home teams won 56% of all these games, and the home edge shows up at every size of mismatch: in every group on the chart, the better team won 10 to
18 more games out of every 100 at home than on the road. Even in the biggest mismatches, home field still matters. Of the 86 times a much better team lost, 64
were on the road.

## Sunday

The Bills have outscored opponents by 9.8 points a game this season, and Miami has been outscored by 8.4, so the Bills are 18.2 points a game better, and they're at home.
Much better teams at home have won 88% of the time. That's history, not a forecast: our model's chance for the Bills on Sunday, from the first story, is 81%.

## Rivalry games aren't closer

"Throw out the records" is a common line for division games. The numbers don't back it up. Much better teams won 80% of division
games (171 games) and 79% of other games (249). Teams 10 or more points a game better won 75% of division games and 73% of other games. When the Bills were
10 or more points a game better than Miami going in, they went 4-2 from 1999 to 2025. That's too few games to read much into.

## When the upset comes, it's usually close

![How the games ended](nfl-mismatch-endings.png)

In the 86 games the much better team lost, the typical upset was decided by 5 points, and 65% were one-score games
(8 points or fewer). When the much better team won, it won by 17 or more 42% of the time and by one score 36% of the time. Its typical win was
by 13.

## One smaller note

**Cold weather.** When a much better team played at home outdoors at 40°F or colder, it won 28 of 29. That's a small group, and the schedule
data has no temperature for 4% of these outdoor home games, so take it as a note, not a finding.

## For the stat-heads

- Same sample as the first story: nflverse schedules, regular season 1999-2025, both teams with 4+ prior games (5,205). Ties = 0.5.
- Gap 17+: home 0.880 (n=183), road 0.728 (n=237); division 0.801 (n=171), other 0.789 (n=249).
  Gap 10+: division 0.748 (n=660), other 0.735 (n=927). All games: home team 0.561.
- Upsets (gap 17+): n=86, median margin 5.0, share decided by 8 or fewer 0.651. Better-team wins: n=333, 17+ 0.420, 8 or fewer 0.357.
- Cold: gap 17+, better team at home, roof = outdoors, temp <= 40: 29 games (28 wins); temp missing for 3.7% of 135 outdoor home games.
- Gap 17+: 1999-2019 0.797 (n=347), 2020-2025 0.781 (n=73). Home-minus-road edge by gap group: 0-3: +0.132, 3-7: +0.147, 7-10: +0.095, 10-14: +0.129, 14-17: +0.125, 17-20: +0.175, 20+: +0.127.
- No market data read: the schedule query selects only game, team, score, division, roof and temperature columns.
