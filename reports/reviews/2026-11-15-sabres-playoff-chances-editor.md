# Editor review (stage 3): 2026-11-15-sabres-playoff-chances

Reviewed: story body (not "For the stat-heads"), the three charts, the hero JSON, the site dek in `src/site/build.py`, and Ledger P0017.
Note: the review record shows only the self-check so far. No Quant (stage 2) record exists yet.

## One-sentence version

"The Sabres aren't done, but they're long shots at about 1 in 6. Their cold shooting and goaltending should even out on their own. The scoring chances they give up, especially when they're shorthanded, won't. Cut those to league average and their playoff chance doubles."

That is the lead, almost. The lead's last line ("Fix it, and their chances roughly double") doesn't say which fix. Cutting only the shorthanded chances gets them to 25%, not double.

## Verdict: needs edits (recorded as FAIL for this round)

The structure is right and it answers all four of Charlie's questions in order. What has to change before it passes:
- One claim goes further than the table supports (edit 3).
- Two numbers a fan will check don't add up (edits 4 and 5).
- The word "chances" means two different things all the way through (edit 2).
- The first chart's title has betting flavor (edit 6).
- The worked example that shows what a chance is worth is missing (edit 8).

## Edits, most important first

### 1. Lead: say which fix doubles it
Replace:
`The real problem is how many chances they give up, especially when they're
shorthanded, and that kind of problem tends to stick. Fix it, and their chances roughly double.`
With:
`The real problem is how many scoring chances they give up, especially when they're
shorthanded, and that kind of problem tends to stick. Cut those chances to league average and their playoff chance doubles, to 32%.`

### 2. "Chances" means two things. Keep them apart everywhere
Today "chances" means scoring chances, and also the playoff probability ("their chances roughly double", "Playoff chance"). A fan
reading "Fix it, and their chances roughly double" can't tell which one. Rule for the whole piece: say **"scoring chances"** on first
use in each section and in every standalone line (headline, dek, hero, chart titles). Always say **"playoff chance"** for the probability.
- Headline: replace `Not yet, but they need to stop giving up so many chances` with `Not yet, but they need to stop giving up so many scoring chances`
- Dek (`src/site/build.py`): replace `the chances they give up, especially shorthanded, won't on their own.` with `the scoring chances they give up, especially when they're shorthanded, won't fix themselves.`
- Hero: replace `"If they allowed league-average chances"` with `"If they allowed a league-average number of scoring chances"`
- Hero explainer bar: replace `"Chances allowed"` with `"Scoring chances allowed"`

### 3. Overclaim: not all the extra chances against come shorthanded (writer must compute)
The story says: "At full strength, Buffalo is about even (50% of the chances). The extra chances against come while a man down." By the
story's own table, Buffalo allows 3.25 a game against a league average of 2.96, which is about 0.29 extra. Shorthanded accounts for 0.79 vs 0.67,
about 0.12 extra. The what-ifs agree: the shorthanded fix alone gets them to 25%, the full-defense fix to 32%. The stat-heads note also has
five-on-five chances allowed slightly above average (2.08 vs 2.03). So the shorthanded piece is the biggest single piece, but not all of it.
Replace:
`The extra chances against come
   while a man down: the 5th-most in the league, and 21 goals allowed.`
With (writer computes the bracketed numbers; Quant checks "biggest single piece"):
`The biggest single piece of the extra scoring chances against comes
   while a man down: [0.12] of the [0.29] extra a game. Buffalo allows the 5th-most chances in the league when shorthanded, and has given up 21 goals that way.`
Also give the numbered item a header that states the finding: replace `They give up too much when they're shorthanded.` with
`They give up too much with a man in the penalty box.` (optional; "shorthanded" is fine hockey language. Keep it if you prefer.)

### 4. Benson's numbers don't add up for a fan (writer must reconcile)
`2 goals on chances worth 7.3. That's about 6 of the team's 7 missing goals.` A fan does 7.3 - 2 = 5.3 and gets "about 5", not 6.
The generator prints `abs(fin_low.fin)` from the card data, which isn't the same as `g - ixg` as displayed (likely a different
xG rescale or definition between the card's `ixg` and `fin`). Use one consistent pair so the subtraction works on the page, then reword. Example
if the card's finishing figure is the right one: `2 goals on chances worth [X]` with X = 2 + that gap. Don't publish until they match.

### 5. "Per 82" in an 84-game season
The story says this season is 84 games, and the player table uses "per 82". A fan will notice. Either restate the pace and rating per 84
(writer recomputes), or say why 82: `points per 82 games (the length of every season before this one)`. Also rename the vague column:
replace `| Points pace (per 82) | Rating (per 82) |` with `| On pace for (per 82 games) | Track record says (per 82 games) |`
and replace `Each Sabre's points pace this season against his rating, our best guess at his points per 82 games from here, built from this season and the last
three.` with `Each Sabre's scoring pace this season against what his track record says he should score, our best guess built from this season and
the last three.`

### 6. Points chart title: drop "the line"
"Ahead of the line" sounds like betting talk, and it doesn't say what the 16% is. (16% is the playoff chance. That isn't the same as the share of seasons above 94.)
Replace `The Sabres finish ahead of the line in about 16% of seasons` with `The Sabres make the playoffs in about 16% of our simulated seasons`.
Keep the subtitle and the "Points it usually takes to get in: about 94" note. Both read well on their own.

### 7. What-if chart title: name the "it"
Replace `Fewer chances against or more chances for: either one about doubles it` with
`Allow fewer scoring chances or create more: either one about doubles the Sabres' playoff chance`.
Bar labels stand alone. Fine.

### 8. Missing worked example of what a "chance" is worth (writer must compute)
CLAUDE.md asks for a real example ("shots from within 10 feet go in 13.8% of the time"). The story never says how a shot becomes "goals'
worth". The only definition is in the what-if chart's footer. Add one sentence to "How we got the 16%", after **The reasoning:** ...:
`**What a scoring chance is worth:** every shot gets a chance of going in, based on where and how it was taken. Shots from within [X] feet go in
[Y]% of the time; shots from the blue line, about [Z]%. Add those up over a game and you get how many goals a team's chances were worth.`
(X, Y, Z from the xG model, this season or the training seasons. The writer computes them.)

### 9. "Expected goals" is jargon in the body
Replace `turns two teams' ratings into expected goals for each game, and plays the game out` with
`turns two teams' ratings into how many goals each should score in that game, and plays the game out`.

### 10. The scorecard and the caution are hard to follow
Replace:
`On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored 0.15. Going by who's in a playoff spot
after 20 games scored 0.20. One honest caution: of the 23 teams we gave between 5% and 30%, the model said 16% on average and
3 made it.`
With:
`We graded it the way we grade the Ledger, where lower is better: 0 is perfect and calling every team 50-50 scores 0.25. The model scored 0.15.
Simply picking whoever held a playoff spot after 20 games scored 0.20. Teams in Buffalo's spot do sometimes get in: of the 23 teams the
model gave between 5% and 30%, 3 made it (it gave them 16% on average).`
Keep the next sentence about last year's Sabres. It's the best line in the section.

### 11. Units on the points-a-game numbers
Replace `1.16 a game. So far it's earned 1.00 a game. Last season's 50-win team earned 1.33.` with
`1.16 points a game. So far it's earned 1.00 a game. Last season's 50-win team earned 1.33 a game.`

### 12. "Their record is about what they've earned": plainer replay sentence
Replace `Replay each of Buffalo's games from its shots, with every shot going in or missing at its own chance, and the Sabres' chances were worth about
**20.7 points**.` with `Replay each of Buffalo's games shot by shot, with every shot going in about as often as shots like it usually do, and the Sabres'
play was worth about **20.7 points** in the standings.`

### 13. "What's going wrong" table: formatting a fan trips on
- Replace both `| -0.00 |` cells with `| 0 |`. "-0.00" reads as a typo. It's `{L.fin:+.2f}` and the goaltending equivalent in the generator.
- Replace `3.06 (10th of 32)` with `3.06 (10th-most of 32)` so it matches the other rank wording.

### 14. Goalie table needs a so-what line
After the goalie table, add: `Luukkonen has faced the most shots, and he's allowed about 3.2 more goals than an average goalie would have on them.
Like the shooting, that rarely carries over.`

### 15. Shorthanded bullet: "about half of a problem like this tends to last" is muddled
Replace `It's the most specific fix on the list, and about half of a problem like this tends to
  last if nothing changes.` with `It's the most specific fix on the list, and it's the kind of problem that tends to stick around if nothing changes.`

### 16. Standings table: cells that don't stand alone
`34 in 21` under "Points now" is odd on a screenshot. Replace the header `| Eastern team | Points now | Projected finish | Playoff chance |` with
`| Eastern team | Points (games played) | Projected points | Playoff chance |`, and in the generator format cells as `34 (21)`. Optional:
use city names (Carolina, New Jersey...) instead of abbreviations. Most fans know them, but not CBJ or NJD at a glance.

### 17. Nice to have: make "0.2 more goals' worth of chances" concrete (writer computes)
A fan can't picture 0.2 goals' worth. One clause would do it, something like `(about one more shot from in close every [N] games)`. Skip it if no clean figure exists.

## What works (keep)
- The headline question and the "Not yet, but" answer. The four sections follow Charlie's four questions in order.
- The Ledger call reads on its own: "Sabres make the 2026-27 playoffs (top 3 in their division or one of the East's 2 wild cards)," 16%.
- Last year's Sabres at 13% making it with 109 points is a great honest detail, and fans will repeat it.
- The carry-over chart reads in five seconds. Its title is the takeaway and the gray bars do the work.
- "Wait for the shooting and the saves to come around. Our projection already counts on that." That's exactly the right note.

## Charts
- Points chart: readable, the annotation is good, and the title needs fixing (edit 6).
- Carry-over chart: ready.
- What-if chart: readable, and the title needs naming what "it" is (edit 7).
