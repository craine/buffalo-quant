# Editor report: 2026-wk09-postgame.md (Bills 23, Vikings 6)

## One-sentence version

"We said the Bills would score 23 and they scored 23. We said the Vikings would score about 23 and they scored 6, because Carson Wentz had one of the worst passing nights of the season. We went 5 for 7, and here are the two we missed."

It's the headline, and the lead gets there, so the test passes. The lead paragraph is too crowded to read aloud, though. The model-testing aside sits in the middle of the key sentence.

## Verdict: needs edits

The bones are good. The headline, the first chart, the "coin landing on its edge" honesty and the decision to stop using the Wentz swap are exactly the receipts brand. There are three real problems:

1. **The story's main measure is never explained.** "Pass plays gain points," "cost it about 26 points," "short throws cost it 16 points": a fan reads "points" as points on the scoreboard. Then the story says Minnesota scored 6 but "lost 26 points" passing, and to that fan it makes no sense. This breaks the "show where the key number comes from, with a real example" rule, and it's the biggest fix. It needs a new number (see edit 1).
2. **The order buries the interesting part.** Minnesota's collapse and our miss are the story. Right now the reader gets a table, a second chart, a grading-method box and the Bills' half before reaching it.
3. **The two charts repeat each other alongside the table.** The scorecard chart and the scorecard table carry the same seven rows.

## Suggested structure (bold, but uses only existing text and numbers)

1. Headline (keep)
2. Short lead (edit 2)
3. Intro italic line (keep, with edit 9)
4. Chart: projected vs. final (keep, it's the story's chart)
5. **New short box: "What 'gaining points' means"** (edit 1, needs a new number)
6. **Minnesota: what we missed** (moved up), including "Why our Vikings calls missed"
7. **Buffalo: right on the number**
8. **The scorecard** table, then "How we grade" and "One hit we're not bragging about"
9. The weak spot / defense section, folded into "What it means"
10. What it means (edit 12)
11. For the stat-heads (untouched)

Cut the scorecard PNG from the body, or move it to the stat-heads section. The table already has the "what happened" column, which the chart lacks. If Charlie wants a second chart for social, keep it but apply edit 14.

## Specific edits, most important first

**1. Explain "gaining points" with one real play (NEW NUMBER NEEDED).** Insert right after the first chart:

> **What "gaining points" means.** Every snap starts from a spot on the field where an average NFL offense can expect a certain number of points from the drive. A good play raises that number and a bad one lowers it. [Writer: one real play from this game, e.g. one of Wentz's interceptions: "Before Williams' interception, Minnesota could expect about X points from that drive. After it, Buffalo could expect Y. That one throw cost the Vikings about Z."] Add up every pass play and you get whether a team's passing helped or hurt it. Minnesota's cost it about 26 points. That doesn't mean they lost 26 points off the scoreboard. It means their passing game turned drives that should have produced points into drives that produced almost nothing.

The writer needs to compute X, Y and Z (expected points before and after one specific play, from the play-by-play). Without a real example, this rule isn't met.

**2. Replace the bold Finding paragraph** with:

> **We projected the Bills to score 23.4. They scored 23. We projected the Vikings to score 22.8. They scored 6, a miss that big happened only about 3 times in 100 when we checked the model against past games. Of the seven calls we logged before kickoff, five hit, including the one that matters most: the Bills win. Both misses came from Minnesota's passing game, which had one of the worst nights of any team this season.**

**3. Add one line explaining the run calls (NEEDS A CHECK).** A fan sees "Bills' runs lose points overall" marked as a *hit* and thinks we predicted the run game would be bad. In the scorecard section, add:

> Why would "runs lose points" be the expected outcome? Because across the league, the average run [writer: league-average value per run this season, e.g. "costs about 0.0X points"]. Losing a little on the ground is normal. Running well is the exception.

The writer must compute the league average before this line goes in. Don't state it qualitatively without the number.

**4. Replace** "Gained 0.003 points over 36 pass plays" (table) **with** "Gained 0.003 points over 36 pass plays: basically zero". The cell has to warn the reader before they reach the "not bragging" box.

**5. Replace** "By the rule we set before kickoff, that's a hit, the same way we'd have counted a miss by that margin." **with** "By the rule we set before kickoff, that's a hit. If it had landed 0.003 the other way, we'd have logged a miss."

**6. Replace** "Over 36 dropbacks they gained" **with** "Over 36 pass plays they gained". Use one term throughout. The story switches between "pass plays" and "dropbacks" for the same thing (also in "about 26 points over 33 dropbacks": change to "33 pass plays"). Add once, in the Minnesota section: "(pass plays include sacks and quarterback scrambles)."

**7. Replace** "Our model had Minnesota around 23 points, mostly from Kyler Murray's games and last season, with a typical range of 11 to 35. Six was below that range: in testing, only about 3 in 100 teams fell that far short of their projection." **with** "Our model had Minnesota around 23 points, built mostly on Kyler Murray's games and last season. We expected their score to land between 11 and 35 eight times in 10. Six was below that. When we ran the model back over past games, only about 3 teams in 100 fell that far short."

"Typical range" doesn't match the chart's "8 games in 10," and "in testing" means nothing to a fan.

**8. Say why Wentz started (NEEDS A FACT CHECK).** The story mentions Murray and Wentz but never says Wentz was the starter in place of Murray, or why. Add one clause in the Minnesota section, e.g. "With Kyler Murray out, Carson Wentz started and went 8 of 24..." The writer and QA need to confirm the reason before any reason is stated.

**9. Replace** "([part 3](bills-vikings-prediction.html))" **with** "([our preview](bills-vikings-prediction.html))". Also replace "Part 3 said" with "Our preview said" and "Part 1 said" with "Earlier this season we said". A new reader doesn't know what the parts are.

**10. Replace** "per play, the 3rd-worst passing game by any team in 272 games this season" **with** "play for play, the 3rd-worst passing night of any team this season (out of 272 team performances)".

**11. Replace** "Monday, Minnesota's 25 short throws cost it 16 points." **with** "Monday, Minnesota's 25 throws of under 20 yards downfield cost it 16 points." To a fan, "short" means a dump-off. The stat-heads definition is under 20 air yards, which also covers intermediate throws.

**12. Rename and fold "The weak spot that wasn't."** The header says the weak spot went away, but the body says it didn't ("it doesn't make that weak spot go away"). Change the header to **"A known weak spot, closed for a night"** and fold the section into "What it means" as the defense bullet. Replace "(2.35 to 2.10; league 2.05)" with "(about 2.1 points a drive now, right around the league average of 2.05)". Fewer decimals, same numbers.

**13. Make "What it means" look forward.** Brand rule 3 is predictive over descriptive, and the current bullets mostly repeat the story. Move the strongest forward-looking line in the piece here: "We won't use the Wentz swap on the Ledger again until we've tested it." Final bullets:
   - Defense: two strong games in a row (the folded weak-spot material, plus the "small sample, Minnesota's quarterback situation helped" caveat).
   - What we're changing: no more untested quarterback swaps on the Ledger.
   - Next: at the Jets, Sunday, Nov. 15, with predictions logged before kickoff.
   - Cut "The record is the point. 6 of 8 so far." It repeats "How we grade."

**14. Charts.**
   - *Projected vs. final:* it passes the five-second test, and the title is the takeaway. Optional tightening: "Bills: right on the number. Vikings: 17 points short of our call." (The 17 comes from the 16.8 already in stat-heads.) The subtitle's "open dot / solid dot" key works, but the Bills' dots overlap. Fine as is, since the labels carry it.
   - *Scorecard:* cut it from the body (it repeats the table). If it's kept, add "(by 0.003)" to the "Bills' pass plays gain points overall" label so the chart doesn't oversell that hit, and match colors: the subtitle says gray means a miss, but the MISS labels are red. Pick one.

**15. Small fixes.**
   - "was sacked 1 time" -> "was sacked once"
   - "39 designed runs for 132 yards" -> "39 runs (not counting Allen scrambles) for 132 yards"
   - "Small numbers, but that's the point of keeping the record: it adds up." -> "Eight calls is a small record. That's why we keep it: it grows every week."
   - In "How we grade," "Lower is better" should come right after the two scores so a fan can compare them: "This week our calls scored 0.22. Guessing 50/50 on every call would score 0.25. Lower is better."

## Needs from the writer/Quant before publishing

- Edit 1: expected points before and after one real play from this game (e.g. a Wentz interception).
- Edit 3: league-average points gained or lost per run, 2026 regular season.
- Edit 8: confirmed reason Wentz started over Murray (or drop the reason and just say Wentz started).
