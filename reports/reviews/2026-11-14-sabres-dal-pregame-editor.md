# Editor review: 2026-11-14 Sabres at Stars pregame

**Verdict: needs edits (FAIL until the required fixes below are applied).** Good story underneath. The bounce-back angle is new and a good partner to Thursday's back-to-back story: that one said the model misses something, this one says it doesn't. Charts are readable. The problems are a confusing lead, one paragraph that works against its own section, and the "how we measure" box missing the math step the earlier pregames had.

**My one-sentence version (radio line):** "Our model has Dallas winning about 62 times in 100 because the Stars keep teams away from their net and the Sabres don't. And forget the bounce-back talk after Dallas got hammered 8-3 Thursday: teams coming off a blowout actually win a little less often than usual."

The lead has the right pieces, but it buries the 62% and puts three ideas into one bold block. "Both teams lost 8-3 this week" also trips up a fan, because the very next line says Buffalo's last game was a 3-2 overtime loss in Chicago.

## Required fixes (most important first)

All line references are to the .md; the same text is in `src/reports/sabres_pregame_dal.py` (lines noted).

1. **Lead: say plainly which 8-3 loss matters, and make the bounce-back claim match the body** (gen 258-259).
   - Replace `Both teams lost 8-3 this week, and Dallas's came Thursday, so you'll hear about a bounce-back game. The`
     with `Dallas got blown out 8-3 at home Thursday, so you'll hear about a bounce-back game. The`
   - Replace `won 46% of their next game, about the same as everyone else.**`
     with `won 46% of their next game, a little less often than everyone else (50%).**`
   - Why: Buffalo's 8-3 came two games ago, so it isn't the bounce-back question. The body says "if anything, they win a little less"; the lead says "about the same". Make them agree. The Buffalo 8-3 still gets its mention in the bounce-back section.

2. **The Oct. 8 sentence argues against its own header** (gen 292). "What makes Dallas hard to play" ends with Buffalo getting the better chances (2.6 vs 2.1) and losing 4-0. A fan reads that and thinks "so Dallas isn't that hard to play, it's their goalie." Don't present it as evidence for the section. Replace
   `When the teams met in Buffalo on Oct. 8, Dallas won 4-0, with chances worth 2.1 goals to Buffalo's 2.6.`
   with
   `One caution: when the teams met in Buffalo on Oct. 8, the Sabres actually got the better chances (worth 2.6 goals to Dallas's 2.1) and still lost 4-0. One game is a small sample, and our prediction goes by the full season.`
   Optional, needs a new number from the writer: who was in goal for Dallas that night and his saves. If it was Oettinger, that's a natural lead-in to the goalie table.

3. **Restore "The math" to the "How we measure chances" box and tie it to a headline number** (gen ~284-286). CLAUDE.md requires the source, a real example, the math, and how we checked it. The CHI and TBL pregames had "The math"; this one dropped it, and "How we checked it" is now only a link. Replace
   `**How we checked it:** the full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).`
   with
   `**The math:** each shot's chance comes from our model, built on past seasons and tested on a season it hadn't seen; we nudge each season's totals so the league's chances add up to the league's real goals. **How we checked it:** the full explanation, with the chart, is in our story on [last year's 50-win season](sabres-50-win-mirage.html). For Saturday: the chances Buffalo has allowed were worth 3.25 goals a game, and it has actually allowed 3.58. That gap is the goaltending, below.`
   (Every number is already in the table. The Quant should confirm the "goaltending" attribution holds before final.)

4. **The "Part of that... as below" sentence is clumsy and repeats the next paragraph** (gen 300-301). Replace
   `Part of that is that teams that get blown out tend to be a little weaker to begin with: our model, which ignores the last score, already expected them to win less often, as below.`
   with
   `Part of the reason is simple: teams that get blown out tend to be a little weaker to begin with.`
   Then in the next paragraph, replace `It doesn't look at the last score at all, only at the chances teams create and allow. On games` with `Our model never looks at the last score, only at the chances teams create and allow. On games`. That way the point is made once.

5. **Jargon and a second "league average" in the prediction paragraph** (gen 326). "On the model's own scale" means nothing to a fan, and 2.99 next to the table's 2.97 reads like a mistake. Replace
   `2.73, against a league average of 2.99 on the model's own scale.`
   with
   `2.73. (After that blending, an average team comes out at 2.99, slightly different from the 2.97 in the table above.)`

6. **Repeated angle from Nov. 11** (gen 338). "Getting to the net" was the TBL pregame's matchup to watch, and "Sabres allow the 6th-most" was its lead. Keep the facts but tie them to what's new tonight. Replace
   `- **Getting to the net.** Dallas allows the 2nd-fewest shots from close in.`
   with
   `- **Second chances.** Dallas allows the fewest rebound shots in the NHL and the 2nd-fewest from close in.`
   The rest of the bullet can stay.

## Suggested (not blocking)

7. **Link the two "does the model miss it?" stories.** This is the series' best idea. After `So for Saturday, Dallas's 8-3 loss counts for exactly what its chances were worth, and nothing more.`, add: `That's the opposite of Thursday in Chicago, where tired legs were something our model missed ([our pregame](sabres-chi-pregame.html)).` (Use the correct slug/link.)
8. **"(see below)" in the goalie note points to the wrong idea** (gen 316). Below says adding the goalie made predictions no better; it says nothing about carrying over. Replace `and they don't carry over well (see below), which is why` with `and when we tested adding the starting goalie, the predictions got no better (see below), which is why`.
9. **Ledger line** (gen 128): when the call is logged, the text should switch to the logged timestamp, as the CHI pregame did. That changes the markdown, so it needs the final check afterward.
10. **Table:** fans will notice that Buffalo is 13th in close shots allowed but 27th in chances allowed. One clause would help, but it needs the writer to say what drives the gap (shot type? rebounds?). Leave it alone unless it's computed.

## Charts

- `sabres-dal-chances.png`: fine. The title is the takeaway and the flipped axis is labeled. Minor: the "Create a lot, allow little" label overlaps the top-right dot.
- `sabres-dal-bounce.png`: excellent. Readable in five seconds, the title is the finding, and sample sizes are on the bars.
- `sabres-dal-model-test.png`: good. "Likelier team" is a bit clunky; "Favored team" is plain English but could read as betting, so keep "likelier".

## Hero card and dek

Both are fine. They match the story and use no betting language. If fix 1 lands, consider "teams coming off a blowout won 46% of their next game, a little less than usual" in the dek for consistency.

## Brand / betting check

No betting language. "Favorite", "odds" and "pick" don't appear. Stat terms (xG, GSAx, Brier, Poisson) appear only in "For the stat-heads". Length is right for a pregame.
