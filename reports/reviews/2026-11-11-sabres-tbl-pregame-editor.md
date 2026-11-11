# Editor review: 2026-11-11-sabres-tbl-pregame.md

**Verdict: needs edits (light).** No betting language, no "special teams," and the body has almost no jargon. Three problems: the lead tries to do three things in one breath, the model section is too long for a same-day preview, and a few sentences can't be read aloud.

**One-sentence version (radio):** Our model calls it close, Lightning 54%, Sabres 46%: Buffalo's second-chance game runs into a team that keeps shots away from its net, and the Sabres give up the 3rd-most chances in the league.

The lead's facts are right, but the prediction comes last and the "2nd-fewest (tied)" parenthetical trips the reader.

## Edits, most important first

1. **Lead (rewrite, same numbers).**
   OLD: `**Finding: Tampa Bay allows the 2nd-fewest shots from close to its net (tied) (10.6 a game from within 20 feet), and Buffalo's best weapon this season has been second chances: the Sabres are 3rd in the NHL at creating rebound shots. The bigger worry is at Buffalo's end: the Sabres allow chances worth 3.30 goals a game, 30th of 32. Our model gives Tampa Bay a 54% chance to win and Buffalo 46%.**`
   NEW: `**Finding: Our model calls it close, Lightning 54%, Sabres 46%. Buffalo's best weapon has been second chances (3rd in the NHL at rebound shots), but Tampa Bay is tied for 2nd-fewest shots allowed from close to its net. The bigger worry is Buffalo's own end: the Sabres give up the 3rd-most chances in the league.**`

2. **Cut the goalie-test sentence from the body (too long to read aloud, and it's correlation in disguise).** In "What it doesn't count: goalies":
   OLD: `tells you little about his second half (on a scale where 1 means one half perfectly predicts the next, goalies came in between 0.07 and 0.45 over the last three seasons; a team's chances allowed, between 0.63 and 0.75).`
   NEW: `tells you little about his second half. A team's chances allowed carry over much better.`
   (The 0.07-0.45 / 0.63-0.75 figures are already in "For the stat-heads.")

3. **Trim "Where the number comes from" (same-day length; 3 long sentences).**
   OLD: `Seventeen games is a small sample, so we blend each team's numbers with last season's, pulled halfway toward the league average; Buffalo's attack counts as 3.04 and Tampa Bay's defense as 2.66. Start from the league's 2.86 per game, adjust for Buffalo's attack and Tampa Bay's defense, and you get Buffalo's expected chances; do the same the other way for Tampa Bay.`
   NEW: `Seventeen games is a small sample, so we blend in last season, with both pulled toward the league average. That makes Buffalo's attack 3.04 and Tampa Bay's defense 2.66. Put those against the league average of 2.86 and you get Buffalo's expected chances. Then do the same for Tampa Bay.`
   OLD: `A final step, fit on past seasons, turns chances into goals and adds about 0.27 of a goal for playing at home. Then we play the game out on paper: with those scoring rates, how often does each team end up ahead? Ties after 60 minutes are split the way they went for home teams in past overtimes and shootouts (55% home wins).`
   NEW: `We turn chances into goals, add about 0.27 of a goal for home ice, and play the game out on paper. Ties after 60 minutes go the way past overtimes and shootouts went: home team 55%.`

4. **Goalie table: save rate looks like a stat line.** Show `.878` etc. as percentages (`87.8%`, `88.4%`, `88.7%`, `88.0%`) and rename the column `Saves`. Change Vasilevskiy's `-0.0` to `0.0 (about average)`; "minus zero" reads like a typo on air. (Format only, no new numbers.)

5. **Model-test chart title says the opposite of what the story uses it for.** "Mostly held up" while the text says the 50-55% bucket is a coin flip. Suggest title: `Slight favorites won about half the time; bigger favorites won as often as predicted`, or highlight the 50-55% pair as "Tonight's range". Numbers already on the chart.

6. **"How we measure chances" sits between the chart and the table.** For a preview, move it below "The two teams, side by side" so the fan sees the matchup first. In it:
   OLD: `(336,462 unblocked shots)` -> NEW: `(336,462 shots that reached the net or missed it)`. "Unblocked" isn't a fan word.

7. **Chances chart (five-second test: passes, barely).** The y-axis label `(lower is better, so it's flipped)` is clunky. Suggest `Chances allowed per game (better defense is higher)`. The title is the takeaway. Good.

8. **Dek (build.py).** It leaves out Buffalo's defense, the bigger worry, and drops the "tied." Suggest:
   `Our model: Lightning 54%, Sabres 46%. Buffalo's second-chance game meets a defense tied for 2nd-fewest close shots allowed, and the Sabres give up the 3rd-most chances in the league.`

9. **Lead-line consistency.** The body says "chances worth 3.30 goals a game, 30th of 32" in some places and "3rd-most" in others. Use "3rd-most" in the body text and keep 30th in the table.

## Other notes
- Rebounds chart: passes the five-second test. Title is the takeaway.
- No betting language. "Favorite" in the chart is ordinary sports language, fine.
- For the Quant (not my lane): Luukkonen 11 + Ellis 7 = 18 appearances in 17 games. Probably one relief appearance; confirm "Games" means appearances.
- NEEDS A NUMBER: none required by these edits.
