# Editor report: 2026-11-08-sabres-vgk.md (Vegas 4, Buffalo 1)

## One-sentence version

"The Sabres outchanced Vegas, by a lot at full strength, but Adin Hill had one of the best goalie nights in the league this season and that's the whole 4-1."

That point is in the lead, but it's buried under the replay percentages and the Ledger hit/miss explanation. Fans have to get through three different "46%"-type numbers before reaching Hill.

## Verdict: needs edits

The reporting is strong. The radio lines are good ("Only 12 of the 586 goalie games... have been better," "the Sabres score one goal or fewer only 8% of the time," "Vegas's shorthanded shots were worth more than Buffalo's power play"). The problems:
- The lead is overloaded.
- The 46% coincidence and the "Sabres win at 46% = a hit" framing confuse a fan.
- Signed decimals (+2.9, -1.9) read like stat lines.
- The same point ("chances said Buffalo, the goalie said Vegas") gets made four times.
- The ending looks back at the game but never says what comes next.

## Edits, most important first

### 1. Lead: cut it down to the story, and move the replay and Ledger material to their own sections

Replace:
> **Finding: The Sabres lost 4-1 Sunday, but they had the better chances: their shots were worth 3.9 goals to Vegas's 3.6.
> Replay those same shots thousands of times and Buffalo wins about 46%, Vegas about 38%, and 16% end tied. The difference was
> in goal. Adin Hill stopped 28 of 29 shots, about 2.9 goals better than an average goalie, one of the best goalie
> nights in the league this season. Our pregame model gave Buffalo a 46% chance, a slight lean to Vegas, so it goes on the Ledger as a hit,
> but not for the reason it expected: Vegas didn't win on chances, it won in goal.**

With:
> **Finding: The Sabres lost 4-1 Sunday, but they had the better chances: their shots were worth 3.9 goals to Vegas's 3.6, and 3.2 to 1.8 at full strength. The difference was in goal. Adin Hill stopped 28 of 29 shots, about 2.9 goals better than an average goalie, one of the best goalie nights in the league this season. On shots like Buffalo's, the Sabres score one goal or fewer only 8% of the time.**

Why: one idea per sentence, and it ends on the most repeatable number. The replay split (46/38/16) moves to edit 3. The Ledger moves to Receipts (edit 6). Every number is already in the story.

### 2. Headline: the second half doesn't parse

Replace:
> Golden Knights 4, Sabres 1: Buffalo earned more than one goal. Adin Hill didn't allow it

With:
> Golden Knights 4, Sabres 1: Buffalo had the better chances. Adin Hill had the better night

### 3. Replay explanation: say how it works, put the 46/38/16 here, and make the coincidence note plain

Replace:
> In our replays, the Sabres score one goal or fewer only 8% of the time on shots like these. (The replay's 46% for Buffalo
> happens to match our pregame 46%; they're different numbers. One is before the game from season form, the other is after it from Sunday's shots.)

With:
> To see how unusual that is, we replayed Sunday's game 20,000 times, letting each shot go in or miss at its own chance. Buffalo won 46% of the replays, Vegas 38%, and 16% ended tied. The Sabres scored one goal or fewer in only 8% of them. (That 46% happens to match our pregame number. It's a coincidence: the pregame number came from each team's form before the game; this one comes only from Sunday's shots.)

### 4. Remove the repeated point; keep it in one place (the goalie section)

"Vegas didn't win on chances, it won in goal" appears in the lead, the goalie section, Receipts (line 81-82) and Takeaways. With edit 1, the lead says it once. Then:

Replace:
> We're not taking a victory lap. The model expected a close game with Vegas slightly ahead. On chances it was close, but Buffalo was the one slightly ahead.
> Vegas won because the goals didn't follow the chances, and the model can't see a goalie's hot night coming.

With:
> We're not taking a victory lap. The model expected a close game with Vegas slightly ahead. It was close, but Buffalo was the one slightly ahead, and no model sees a goalie's hot night coming.

### 5. Goalie numbers: words, not signed decimals

Replace:
> Hill faced Buffalo shots worth 3.9 goals and allowed 1: **+2.9**.

With:
> Hill faced Buffalo shots worth 3.9 goals and allowed 1: **2.9 goals better than an average goalie.**

Replace:
> Ellis faced Vegas shots worth 3.6 goals and allowed 4: **-0.4**, a little below average, not a bad night.

With:
> Ellis faced Vegas shots worth 3.6 goals and allowed 4: **0.4 worse than average**, a little below, not a bad night.

Replace:
> [Adin Hill](../cards/adin-hill.html) was 1.9 worse than average (8 games). Small samples, both.

With:
> [Adin Hill](../cards/adin-hill.html) had allowed 1.9 more than an average goalie would have (8 games). Both numbers come from fewer than 10 games, so they swing fast.

Replace:
> (Our pregame story had Hill at -1.8; shot values are re-tuned slightly as each night's games come in.)

With:
> (Our pregame story said 1.8; the number shifts a little as each night's games are added.)

### 6. Receipts: "we logged the Sabres to win, and it's a hit because they lost" will confuse every fan

Replace:
> Before the game we logged one call on the [Ledger](../ledger.html): **the Sabres win, at 46%.** Giving Buffalo less than half means our model
> leaned Vegas, and Vegas won, so by our rule (the side we gave more than 50% wins) it's a hit. It was a near coin flip either way: our pregame story noted
> that the model's slight leans, 50-55%, had won about half the time in testing. It stays up regardless.

With:
> Before the game we logged one call on the [Ledger](../ledger.html): **a 46% chance the Sabres win.** That made Vegas a slight favorite, and Vegas won, so it counts as a hit. Don't read much into it: our pregame story noted that leans this slight (50-55%) had come in only about half the time in testing. Hit or miss, it stays up.

Replace:
> We also grade every call with a simple score: the gap between the chance we gave and what happened, squared. Lower is better. Saying 46% on a
> game Buffalo lost scores 0.21. A pure 50/50 guess would have scored 0.25. So slightly better than a coin flip, on this one game.

With:
> We also score every call: take the gap between the chance we gave and what happened, and square it. Lower is better. Our 46% on a Buffalo loss scores 0.21; a straight 50/50 guess would have scored 0.25. So a bit better than a coin flip, on one game.

### 7. Period section: promote the best line in the story, and stop repeating Marner's 47%

The 47% for Marner appears three times (explainer, this paragraph, goals table). The power-play point, that Vegas got more out of Buffalo's power plays than Buffalo did, is the sharpest radio line in the story, and right now it's the last clause of a paragraph.

Replace:
> The first period was the Sabres' game to take: their chances were worth 1.8 goals to 0.5, and it stayed 0-0. The turn came in the second,
> when Mitch Marner scored from 3 feet while Vegas was killing a penalty, a shot that goes in about 47% of the time from there.
> Buffalo's power-play shots on the night were worth 0.5 goals, and it didn't score with the extra man. Vegas's shorthanded shots were
> worth 0.8, more than that.

With:
> The first period was the Sabres' game to take: their chances were worth 1.8 goals to 0.5, and it stayed 0-0. The turn came in the second, when Mitch Marner scored from 3 feet while Vegas was killing a penalty.
>
> That sums up Buffalo's power play Sunday: **Vegas got more out of it than Buffalo did.** Vegas's shorthanded shots were worth 0.8 goals; Buffalo's power-play shots were worth 0.5, and it didn't score with the extra man.

Header: replace `## Period by period` with `## A big first period, then a shorthanded goal turned it`.

Table header: replace `| Period | Sabres chances, in goals | Golden Knights | What happened |` with `| Period | Sabres chances, in goals | Golden Knights chances, in goals | What happened |`.

### 8. Takeaways: fix the even-strength bullet, untangle the number collision, add a look ahead

The first bullet is headed "even-strength" but leads with the all-situations 3.9. It also cites Vegas allowing 2.6 per game, which clashes with the "Vegas's chances were worth about 2.6" in the explainer: two different 2.6s, four paragraphs apart.

Replace:
> - **Buffalo won the even-strength game.** Against a Vegas team that had allowed the 4th-fewest chances per game in the league before Sunday (2.6),
>   the Sabres created 3.9 goals' worth (their average coming in was 3.1), 3.2 of it at five on five.

With:
> - **Buffalo won at full strength, 3.2 to 1.8 in chances.** And it did that against a defense that had given up the 4th-fewest chances in the league coming in. Overall the Sabres created 3.9 goals' worth, well above their 3.1 average.

Writer's call: if the 2.6 per-game figure is needed, give it in a different spot from the "about 2.6" final-two-minutes number.

**Needs writer (new content):** the story never says what comes next (brand rule 3: predictive over descriptive). Add one closing bullet, e.g. what Sunday's full-strength edge, or Hill's night, means going forward, using the goalie split-half test the story already describes ("a hot goalie night doesn't carry over; a chance edge does"). If that needs a carry-over number for team chances, the writer computes it. Then rename `## What to take from it` to `## What it means for Buffalo`.

### 9. Move the season-update sentence to where it belongs

Line 62-63 ("In one afternoon, Hill went from -1.9 ... Ellis went from +2.2 to +1.8 (7 games).") is about the goalies' season numbers, not about why goalies aren't in the model. Move it to the end of the paragraph that ends "...not a bad night." Reword it in words:
> In one afternoon, Hill went from 1.9 below average for the season to 1.0 above (9 games now); Ellis went from 2.2 above to 1.8 (7 games).

In the model paragraph, replace:
> It barely did, much less than a team's chances allowed did.

With:
> It barely did, far less than how many chances a team gives up carries over.

### 10. Blocked shots: too many numbers, and no "so what"

Eleven numbers in four lines. Replace:
> Buffalo tried 78 shots; Vegas blocked 28 of them. Only 7 of 556 team-games this season have had
> 28 or more blocked (the average is 15). Buffalo's 78 tries were 20 more than its average coming in
> (58); 36% were blocked, against 27% league-wide. Blocked shots aren't in the 3.9. Vegas tried 51 shots and had 10 blocked.

With:
> Buffalo tried 78 shots and Vegas blocked 28 of them. The league average is 15, and only 7 times in 556 team games this season has a team had 28 or more blocked. Buffalo blocked 10 of Vegas's 51. Blocked shots don't count toward Buffalo's 3.9.

**Needs writer:** say why this matters. Is it a Vegas habit that will show up again, or a one-night thing? If you can't support either, cut the section to two sentences.

### 11. Plain-English sweep (remaining)

- "Buffalo's 50 unblocked shots" -> "Buffalo's 50 shots that weren't blocked" (same in "Vegas's 41").
- "1.0 of Vegas's 3.6 came in the final two minutes" -> "a full goal's worth of Vegas's 3.6 came in the final two minutes".
- "five on five" and "even-strength" are both used. Use "full strength" throughout the body (edit 8 does this for the bullet).
- "team-games" -> "team games" (edit 10).

### 12. Explaining the data: nearly right-sized; add one line on source and checking

"How we measure chances" has good real examples (Marner 47% from 3 feet, Hertl 9% from 34 feet) and links to the full method. It never says in the body where the shots come from or how we know the model works. After "...Hertl's second goal, from 34 feet, about 9%." add:
> The shot locations come from the NHL's own play-by-play for every game, and we tested the model on a full season of games it hadn't seen.

**Writer to confirm** that this wording matches what was actually validated (CLAUDE.md says out-of-sample on 2025-26).

## Charts

**Flow chart (sabres-vgk-post-flow.png):** readable in five seconds, and the title is the takeaway. Suggestions:
- Label the period lines "1st / 2nd / 3rd". The dashed lines at 20 and 40 aren't explained.
- Annotate the late gold spike at about 58-60: "Vegas up 4-1, last 2 min". The story makes this point and the chart shows it, but nothing ties them together.
- Optional: label the score at each goal dot (e.g. "0-1", "0-2") so a fan can follow the game.

**Goalie chart (sabres-vgk-post-goalies.png):** good. The title is the takeaway and matches the body (12 of 586 better). Minor: make the labels parallel, "Colten Ellis, Sunday: -0.4" to match "Adin Hill, Sunday: +2.9". The signed numbers are fine on the chart because the axis explains them.
