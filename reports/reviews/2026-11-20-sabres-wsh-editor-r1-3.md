# Editor review (stage 3): reports/2026-11-20-sabres-wsh.md

**One sentence a host would say:** "The Sabres snapped their five-game skid with four goals in the first period, but
Washington had about twice the chances. Buffalo's shooters finally had their night."

**Verdict: needs edits.** The lede is right and the story is easy to follow. The fixes are a handful of stiff phrases
Charlie would hear as written, not said, plus the Quant's accuracy fixes (ties in the replay, Benson's goal count, the GM-story
line), which change wording too.

## Edits, most important first

1. **Headline (stacked clause).**
   Replace "Sabres 6, Capitals 3: the skid is over, on a night Washington had the better chances"
   with "Sabres 6, Capitals 3: the skid is over, even though Washington had the better chances".
2. **Lede, replay sentence (Quant item 1).**
   Replace "Play this game over and over with those chances, and Buffalo wins about 14% of the time."
   with "Play this game over and over with those chances, and Buffalo wins it in regulation only about 14% of the time."
   (Add the 13% tie in "Was it luck?" if wanted: "and it's tied after three periods another 13%.")
3. **Lede, finishing sentence (stiff).**
   Replace "This time the puck went in: after a skid of cold shooting, it was Buffalo's second-best finishing night of the season."
   with "This time the puck went in. After five games of cold shooting, it was Buffalo's second-best shooting night of the season."
4. **Receipts (stilted).**
   Replace "They won, so we had the less likely winner, and that counts as a miss."
   with "We gave the Sabres less than an even chance, so this one goes down as a miss."
5. **Benson (Quant item 2; needs the writer to compute "3").**
   Replace "his first goal with a goalie in net since Oct. 29. He now has 2 on chances worth 7.9 this season."
   with "his first goal since Oct. 29. Two of his 3 goals this season came with a goalie in net, on chances worth 7.9."
6. **GM-story line (Quant item 3).**
   Replace "Finishing swings like this are what our [GM story](sabres-if-i-were-gm.html) said to expect: cold streaks tend to even out. What it said to fix was the chances, and those weren't better tonight. Washington had 66% of them."
   with "Our [GM story](sabres-if-i-were-gm.html) said cold shooting tends to even out, and tonight it did. What it said to fix first was the penalty kill, and Washington's power play got 9 shots worth 1.2 goals. Overall, Washington's chances were worth about twice Buffalo's."
7. **Goalie change.**
   Replace "Logan Thompson allowed 3 goals on the first 5 shots that reached him, and Washington switched to Charlie Lindgren after Buffalo's third goal, 10:11 into the game."
   with "Logan Thompson gave up 3 goals on the 5 shots he faced, and Washington pulled him for Charlie Lindgren after Buffalo's third goal, 10:11 in."
8. **Repeat.** "Buffalo scored 4 times in the first period on chances worth 0.9." is the third time (lede, chart note, hero). Cut it from
   "The game" paragraph and start with "Logan Thompson gave up...".
9. **"than an average team would have."**
   Replace "about 3 more than an average team would have" with "about 3 more than chances like that usually produce".
10. **Goal table shot words.** "poke from 8 ft" and "poke from 1 ft" read as typos to a fan. Use "poked in from 8 ft" / "poked in from 1 ft"
    (generator: map shot type `poke` to "poked in").
11. **Table header.** "Sabres chances (worth this many goals)" is clunky. Use "Sabres chances, in goals" and "Capitals chances, in goals".
12. **Penalty-kill decimal.** "more than twice what it averaged coming in (0.52 a game)" — 0.52 of what? Replace with "more than twice
    what its power play usually creates (chances worth 0.52 goals a game coming in)".
13. **Site dek (src/site/build.py).** "Buffalo finished the ones it got: four goals in the first period." Replace with "Buffalo made
    the most of what it got: four goals in the first period."

## Stands alone?

- Chart 1 title "Washington had the better chances. Buffalo scored 5 on chances worth 1.9": a screenshot reader sees 6-3 in the subtitle
  and wonders. Suggest "...Buffalo scored 5 (plus an empty-netter) on chances worth 1.9".
- Chart 2 title "After a skid of cold shooting, the Sabres' second-best finishing night": fine; "shooting night" is plainer than "finishing night".
- Hero note and explainer bars read fine alone.
- Ledger line: "a 42% chance the Sabres win" reads fine alone.

## Fine as is

"Alex Tuch scored against his old team," "The power play wasn't quiet tonight," "Mostly, yes, and that's not a knock,"
the "How we measure chances" paragraph (right size, real examples), and "What's next." No jargon in the body; stat terms stay in
"For the stat-heads." No betting language.

---

# Round 2 (after fixes)

**Verdict: needs one fix (chart).** Every round-1 text edit is in and reads plainly: headline "even though", lede (regulation 14%
plus 13% tie, "second-best shooting night"), "Logan Thompson gave up 3 goals on the 5 shots he faced", repeated first-period line
cut, "usually produce", "poked in", "in goals" headers, power-play wording, receipts line, Benson, GM paragraph. Site-card dek and
hero read fine alone. No betting language. Story text: pass.

**Blocking:** `reports/sabres-wsh-post-flow.png` title is cut off at the right edge: "Washington had the better chances. Buffalo
scored 5 (plus an empty-netter) or..." Shorten it so it fits, e.g. "Buffalo scored 5 (plus an empty-netter) on chances worth 1.9"
(the chart itself shows Washington's line far above). Re-open the PNG after regenerating. The markdown shouldn't change.

**Optional, not blocking** (any text change means a new final check):
- "That's its 2nd-best finishing night of 22 this season." The lede now says "shooting night"; use "That's its second-best
  shooting night in 22 games this season." for consistency.
- The penalty-kill sentence is long: "Washington had 9 power-play shots worth 1.2 goals, more than twice what its power play usually
  creates (chances worth 0.52 goals a game coming in), and scored once." Could split: "Washington had 9 power-play shots worth 1.2
  goals and scored once. Coming in, its power play averaged chances worth 0.52 goals a game."

---

# Round 3

**Verdict: ready (pass).** The flow chart title now fits ("Buffalo scored 5 (plus an empty-netter) on chances worth 1.9"). The
line "2nd-best shooting night in 22 games" matches the lede. The penalty-kill passage is now two short sentences. Compared with
round 2, only those two lines of the markdown changed. Not blocking: the finishing chart's title still says "finishing night"
where the text says "shooting night". Both words work for fans; change it only if the chart is regenerated for another reason.
