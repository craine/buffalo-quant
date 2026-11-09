# Editor report: Bills at Vikings, part 3 (2026-wk09-prediction.md)

## One-sentence version

"Pick almost any score and the Bills are a little more likely to get there than the Vikings: a few percentage points, almost every time. That thin edge makes Buffalo a 53% pick on Monday night."

That is not the current lead. The current lead opens with "23 apiece" and then walks it back, which is exactly what confused Charlie.

## Verdict: needs edits (big structural ones, no rewrite)

The numbers and the reasoning are solid. Three things hold the story back:

1. **The lead leads with the confusing part.** "Rounded, 23 apiece, with the edge to Buffalo" tells the reader it's a tie and then says it isn't. Lead with the ladder, which is the strong part.
2. **The bridge from "23 points" to "53%" comes too late and is missing its key idea.** It sits in section 3, after a four-step drives explanation. The one idea a fan needs is never said outright: *the projection is the middle of a wide range, and next to a typical 6-point miss, a 0.6-point edge is only a nudge. That's why the win chance is only 53%.* Say it, and say it right after the ladder.
3. **"Did we check it?" reads like a methods paper.** It has four sub-parts, a table of grades like 0.230 and two calibration paragraphs. Cut it to about a third and move the rest to "For the stat-heads."

## Recommended structure

| # | Section | Change |
|---|---|---|
| 1 | Lead | Rewrite around the ladder (edit 1) |
| 2 | Ladder chart + "The scoreboard ladder" | Keep. Tighten the reading paragraph (edit 2). Add a projection marker to the chart (chart note A) |
| 3 | **"How a 23-point game becomes 53%"** | Move "From 23 points to those percentages" up to here, ahead of the drives section. Add the "nudge" idea (edits 3-5) |
| 4 | "Why not just call it a tie?" | **Delete as a section.** Fold one sentence into section 3 (edit 6) |
| 5 | "The calls going on the Ledger" | Keep. Clear up the two meanings of "points" (edit 7). New chart title (chart note B) |
| 6 | "Where the 23 comes from" | Move after the calls. Put the "best offense vs. best defense cancels out" hook first (edits 8-10) |
| 7 | "Did we check it?" | Cut hard. Move the grade table and the run-model caution to stat-heads (edits 11-14) |
| 8 | "What the model doesn't know" | Keep as is. It's good |
| 9 | For the stat-heads | Takes the moved table and caution |

Why this order: ladder, then "why only 53%," then the calls is the story a fan follows. The drives math answers "where does 23 come from," a second question most readers only ask once they care. It still gets full treatment, so the "show the reasoning" rule is met.

## Specific edits, most important first

**Edit 1: Lead (top issue).**
Replace:
> **Finding: This one is about as close as games get. Our model projects Bills 23.4, Vikings 22.8: rounded, 23 apiece, with the edge to Buffalo. That small edge shows up at nearly every scoreline, and it gives the Bills a 53% chance to win.**

With:
> **Finding: Pick almost any score, and the Bills are a little more likely than the Vikings to get there: 75% to 72% to reach 17 points, 47% to 44% to reach 24. It's never a big edge, but it's there nearly everywhere, and it adds up to a 53% chance the Bills win. It all traces to one small gap: we project Buffalo 23.4 points, Minnesota 22.8.**

(The word "rounded" and the phrase "23 apiece" should not appear anywhere in the body. That rounding is what made the 53% look contradictory.)

**Edit 2: Ladder reading paragraph.**
Replace:
> The gaps are small, a couple of points of probability, and they all come from the same thing: our Bills projection is 0.6 points higher. That small gap is also why, when we replay past games with both teams at once (more on that below), the Bills finish ahead 53% of the time.

With:
> The Bills are ahead on every rung except the bottom one (at 10 points it's even, 92% each), by 1 to 3 percentage points. That's this game in one table: no big edge anywhere, a small one almost everywhere.

(Reason: "points of probability" collides with football points. Writer: confirm the "1 to 3" from the unrounded values, since I took it from the rounded table. If unrounded gaps fall outside that, use "a few percentage points.")

**Edit 3: Move and rename the bridge section.**
Move the whole "From 23 points to those percentages" section (through the "Who wins?" paragraph) to sit right after the ladder paragraph, ahead of "Where the 23 comes from." Replace its header:
> ## From 23 points to those percentages

With:
> ## How a 23-point game becomes 53%

**Edit 4: Add the "nudge" idea. This answers Charlie's confusion directly.**
Replace:
> Count 24 or more and it's 47%, just under half, because 23.4 is right in the middle. That's the whole ladder.

With:
> Count 24 or more and it's 47%, just under half, because 23.4 is right in the middle. That's what our 23.4 really is: the middle of a wide range, not a guess at the final score. And it's why a 0.6-point edge only gets the Bills to 53%. When a typical miss is 6 points either way, 0.6 is a nudge, not a shove.

**Edit 5: "Who wins?" is cryptic ("each team's miss side by side").**
Replace:
> **Who wins?** Same idea, both teams at once. We replay 1,247 real past games, each team's miss side by side, on top of Monday's projections.
> Buffalo finishes ahead in 53% of them.

With:
> **Who wins?** Same idea, both teams at once. We took 1,247 real past games and noted how far off we were for each team in that same game. Then we applied each pair of misses to Monday's projections and checked who came out ahead. Buffalo did in 53% of them.

**Edit 6: Delete the "Why not just call it a tie?" section.**
Replace the whole section (header through "...written into our Ledger entries before kickoff.") with one line at the end of the "How a 23-point game becomes 53%" section:
> So why not call it a tie? Because the model doesn't: 23.4 beats 22.8, and that's what tips it to 53%. Both numbers go on our Ledger before kickoff.

(The "made-up final like 23-20 or 24-21" material is inside baseball for a fan. It invites the question it answers.)

**Edit 7: "Gain/lose points" uses a second meaning of "points."**
Replace:
> What "gain points" and "lose points" mean: every play moves a drive closer to scoring or further away, and we add it up over the night.

With:
> What "gain points" and "lose points" mean: these aren't scoreboard points. Every play moves a drive closer to scoring or further away, and we add that up over the night.

**Edit 8: Lead "Where the 23 comes from" with its hook.**
Replace the header:
> ## Where the 23 comes from

With:
> ## Where the 23 comes from: the NFL's best offense meets its best defense, and they cancel out

Then move the paragraph "So the most interesting matchup of the night... close to adding the two together." to directly under the header, changing its opening "So the most interesting matchup" to "The most interesting matchup". Follow it with "Points come from drives, so that's where we start. Four steps:".

**Edit 9: Step 4 is vague.**
Replace:
> A last adjustment,
>    learned from past games, trims projections that history says run too high or too low and gives the home team about 1.5 points.

With:
> A final check against past games
>    pulls extreme projections back toward normal and gives the home team about 1.5 points.

**Edit 10: Step 2, smaller fix.**
Replace:
> **Don't overreact to seven games.** A hot start isn't a guarantee, so we blend this season with last season and the league average.

With:
> **Don't overreact to seven games.** A hot start isn't a guarantee, so we mix in last season and an average team.

**Edit 11: Cut the scoreline-check paragraph.**
Replace the full "**The scoreline chances.**" paragraph (from "We ran the model on 1,234 team-games..." through "...will fix this before using these lines again.") with:
> **The scoreline chances.** We ran the model on 1,234 team-games from 2024-2026 that it had never seen. At the extremes it was right on: when it gave a team a 20% chance or less, it said 12% on average and it happened 12%; at 80% or more, it said 89% and it happened 89%. In the middle it ran a few points low, including right at the 20-point line (it said 60%, teams got there 65%). Real scores bunch up on 17, 20 and 24, and our model smooths that out. So both teams' 20-or-more chances are probably a few points low. We're logging them as they are and will fix this before using these lines again.

**Edit 12: Replace the grade table with plain sentences.**
Replace from "**The pass and run calls.** These come from a simpler model..." through the end of the three-row table with:
> **The pass and run calls.** These come from a simpler model, tested on 990 past team-games (2023-2025) against just guessing the league's usual rate. It beat the guess on pass calls and edged it on run calls. On one kind of call it lost, so we threw that call out:

Move the table (with its "Lower grade is better" line) to "For the stat-heads." Decimal grades like 0.230 and 0.245 are exactly the stat-looking numbers fans skip.

**Edit 13: Move the run-model caution.**
Move the whole "**One caution on the run calls.**" paragraph to "For the stat-heads." Neither Monday call falls in the range it warns about. In the body it raises a worry and then cancels it.

**Edit 14: Sack paragraph, light trim.**
Replace:
> But this kind of call did worse than simply guessing the usual rate. When it was confident (above 55%), it said 64% and was right
> 54% of the time. Sacks in one game swing too much to call, so we're not.

With:
> But when this kind of call was confident, it said 64% and was right 54% of the time: worse than just guessing the usual rate. Sacks in one game swing too much to call, so we're not.

## Charts

**A. Ladder chart (wk09c-ladder.png).** A fan reads it in five seconds and the title is the takeaway. Keep it. Two changes:
- Add a vertical dashed line between the 20+ and 24+ groups labeled "Our projection: Bills 23.4, Vikings 22.8." That puts the "23" on the same picture as the percentages, which is Charlie's exact confusion. Then drop the projection from the subtitle so the subtitle reads: "Our chance each team scores at least this many points. Bills win 53% of the time."
- Optional: small "+1", "+3" gap labels above each Bills bar would make "a few points ahead at every scoreline" visible at a glance. Those are new numbers, so the writer must compute them from unrounded values.

**B. Calls chart (wk09c-calls.png).** Readable. The title "Seven calls for Monday night" is a label, not a takeaway. Suggested: "Our seven calls: the closest is who wins, the most confident is Minnesota's run game." The subtitle line "comes from a kind of model we tested" is fine.

**C. Win-test chart (wk09c-win-test.png).** Readable, but the title highlights the 60-70% group and Monday is a 53% game. Retitle to the group that matters: "In close calls like Monday's, the team we leaned to won 56% of the time (we said 55%)." All of those numbers are already on the chart. Also note: the chart counts ties as half a win, while the body says "the team our model favored won 63%" with ties as misses. Add a short caption under the chart so a careful reader doesn't think they conflict: "Chart counts ties as half a win."

## Plain-English flags not covered above

- "points of probability": replaced in edit 2. Use "percentage points" throughout.
- "team-scores" ("2,494 past team-scores"): use "2,494 times a team scored in a past game" or "2,494 past team scores." Minor.
- "Those are the games the model was built on; on games it had never seen, its average miss was 7.5 points": fine. Keep it.
- "a below-average Bills defense (2.23 allowed)": accurate, but readers may stop at "below-average Bills defense." Fine to keep, since part 1 covers it.

## What's working (don't touch)

- The ladder table and "Read it like this" line.
- The four-step drives explanation. It's right-sized once moved.
- The sack call we threw out. It's honest and interesting, and it's the kind of receipt that builds trust.
- "What the model doesn't know." It's short, plain and specific.
