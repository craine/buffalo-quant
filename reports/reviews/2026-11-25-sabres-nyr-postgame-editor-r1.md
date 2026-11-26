# Editor review: Sabres 5, Rangers 1 (2026-11-25-sabres-nyr-postgame)

Reviewer: independent Editor (stage 3). Story sha d6824a2d.

## One sentence a host would say

"The Sabres beat the Rangers 5-1 on even chances, and a hot four games has cancelled out their cold start. Underneath, they're the same
team: they get a little less than half the chances, 22nd in the league."

That point is the lead, which is good. But it's buried in an eight-sentence bold block with about a dozen numbers.

## Verdict: needs edits (fail this round)

The story is solid and much less dry than the earlier recap. The idea is fan-friendly: the chart, a running total climbing back to zero,
reads in five seconds. Four things hold it back: the lead is a wall of numbers; the Receipts and "usual starter" lines need the Quant's fixes;
a few phrases slip into stat-speak; and the "how we checked it" step that Charlie requires is missing.

## Edits, most important first

1. **Lead: open with the hook, then fewer numbers.** The chart already has the best line: five games ago Buffalo had scored 7.9 fewer goals
   than its chances were worth, and now it's +0.5. Both numbers are on the generated chart. Replace the bold lead with something like:
   "**Five games ago, the Sabres had scored about 8 fewer goals than their chances were worth. After Wednesday's 5-1 win over the Rangers,
   they're even. The chances on Wednesday were close: Buffalo's shots were worth 2.5 goals and New York's 2.3. Over the last four games
   the Sabres scored 18 goals, not counting empty nets, on chances worth about 10. That hot run cancelled out a cold start, and it's no
   more likely to last than the cold start was. What lasts is chances, and the Sabres get 48% of them, 22nd in the NHL.**"
   (The first-21-game details can stay in the table below, so they don't need to be in the lead.) Note: "five games ago" is the chart's low
   point after game 20. If the writer would rather keep the 21/4 split everywhere, use "Four games ago... about 7 fewer" from the table
   (57 on 64.1) instead. Keep one framing throughout.
2. **Receipts, preview bullet** (also Quant must-fix 2): replace with "**Our preview** said the Rangers' poor finishing (30th in the NHL)
   probably wouldn't last and their goaltending would probably cool off. It also said one game wouldn't settle either. On Wednesday
   New York scored 1 goal on chances worth 2.3, and Korpisalo allowed 5 on chances worth 2.5. Both are season-long calls, and we'll keep tracking them."
3. **Goalie line** (also Quant must-fix 1): replace "the Rangers started Joonas Korpisalo instead of their usual starter, Dylan Garand (16 games)."
   with "the Rangers started Joonas Korpisalo, who has been taking turns with Dylan Garand since early November."
4. **"paid most of that back"** (also Quant must-fix 3): replace "The last four games paid most of that back." with "A hot four games has
   cancelled most of that out." In the site dek, replace "paying back an unlucky first 21 games" with "cancelling out an unlucky first 21 games".
5. **Plain English:**
   - "had saved about 2.8 goals more than expected in his first 3 games" -> "had saved about 2.8 more goals than an average goalie would have in his first 3 games"
   - "The Sabres' chance share, 48%, is 22nd in the league." -> "The Sabres get 48% of the chances, 22nd in the league."
   - "Every unblocked shot gets a value" -> "Every shot that isn't blocked gets a value"
   - "Its score was 0.26, about what a coin flip earns." -> "On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored 0.26."
     "Its score" means nothing to a reader who sees only this line.
6. **Add "how we checked it" to "How we count chances"** (standing rule). Example: "We check the values against the whole league: this
   season NHL teams' chances added up to almost exactly the goals they scored." If a number is used, the generator must compute it
   (2,367 vs. 2,370 before scaling, per the Quant). The Tampa recap's "the team with more of the chances won 57%" also works if it's linked.
7. **"That's the fourth game of a run in which the Sabres have gone 3-1"** reads clunkily. Edit 1 removes it. If it stays, use "Buffalo has won 3 of its last 4."
8. **"That's why the record, 11-10-4, looks like..."**: see Quant should-fix 4. Goal difference is clearer for fans than W-L-OTL.

## Checks

- **Headline/hook:** "20 goals in four games" is a good scoreboard hook and true. Don't sell it as rare: 19 teams have had an 18-goal four-game
  span this season (Quant). This is not "boring as hell". The running total crawling back to zero is a story fans get. Optional sharper headline:
  "Sabres 5, Rangers 1: a hot week cancels out a cold start."
- **Jargon in body:** none of xG, GSAx, PDO, Corsi or correlation in the body. The small slips are listed in edit 5.
- **Betting framing:** none.
- **Charlie's rejected phrases** ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end"): none found (grep of story and dek).
- **Typed numbers:** body numbers are generated. Literals are guarded by asserts (see Quant should-fix 8).
- **Chart:** reads on its own. The title is the takeaway; the subtitle defines zero; the legend says what each line is; the shaded "Last 4 games"
  box names the run; the footer has the source and date. The y-axis label is long but clear. No change needed.
- **Hero/dek stand alone:** the hero's "18 / Sabres goals in the last 4 games, not counting empty-net goals" and "10.4 / what those chances were worth" work.
  The dek works once "paying back" is fixed.
