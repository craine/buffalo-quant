# Editor review: 2026-11-19-nfl-mismatches.md

Reviewer: Editor (stage 3), independent. Read as a Bills fan and a WGR host. Story body, both charts, hero JSON and the
`nfl-mismatches` site card in `src/site/build.py`. No numbers changed; where a fix needs a new number, it says so.

**One-sentence version (radio):** "Over 27 years, even when one team had been about 17-plus points a game better than the
other, the worse team still won about 1 time in 5. By that history and by our own model, the Bills win Sunday about 4 times in 5."

**Verdict: needs edits (fail).** The idea is strong and the method is honest, but the hero card contradicts its own
bars, "Bills by about 11" reads like a point spread, and the lead and model chart set the 87% next to the Bills' 81% so a fan
hears "the Bills really have 87%". Fix the top five and it is ready.

## Must fix

### 1. Hero explainer kicker contradicts its own chart
- Exact text (hero JSON `explainer.kicker`): `Bigger gaps don't help`
- Problem: The bars directly under it climb 67% -> 71% -> 74% -> 79% -> 80%. Seen alone, the card says the opposite of what it shows.
  Only the step from 17-20 to 20+ is flat.
- Rewrite: `Past 17 points, a bigger gap barely helps`

### 2. "Bills by about 11" is point-spread language (brand rule 1)
- Exact text (lead): `Our own model has the Bills by about 11 over Miami on Sunday, with an 81% chance to win.`
- Also in the model chart title (`Our model has Bills by about 11.`) and the site card (`Our model has the Bills by about 11 over Miami.`).
- Problem: "Team by N" is how a betting line is spoken on radio. It's the one phrase in the piece a listener would
  take as a spread.
- Rewrite (lead): `Our own model projects Bills 30, Dolphins 20 on Sunday, and gives Buffalo an 81% chance to win.`
  Site card: `...still lost about 1 in 5. Our model gives the Bills an 81% chance against Miami on Sunday.`
  Chart title: see item 4.

### 3. The 87% next to the 81% overclaims for the Bills
- Exact text (lead): `When it has expected a team to win by 10 or more, that team has won 87% of the time.`
- Problem: Right after "Bills ... 81%", a fan hears "so the Bills' real chance is 87%." It's 61 games, the model said 82% for
  that group, and the story's own point is that the model's chances match results. The 87% is a small-sample edge, not the headline.
- Rewrite: `Two different ways of measuring land in the same place: teams in Buffalo's spot have won about 4 times in 5.`
  Keep the 87% (with "61 games") in "How we checked it" only.

### 4. Model chart title doesn't stand alone and repeats the overclaim
- Exact text: `Our model has Bills by about 11. Teams it expected to win by 10+ won 87%`
- Problem: Spread phrasing plus the 87% beside the Bills (items 2, 3). A screenshot of this chart tells a fan the Bills are 87%.
  The chart's real message is that the grey and blue bars match.
- Rewrite: `When our model gives a team a chance, that team wins about that often`
  Subtitle: replace `2024-26 are blind tests` with `2024-26 are games it never saw while being built`.
  Legend: `What our model said` -> `Our model's chance for the team it expected to win`.

### 5. The Bills' list: "games like this" is undefined, and the 2024 loss needs context
- Exact text: `The Bills have been the better team and lost 5 games like this since 1999: at Titans in 2021, at Jaguars in 2021, vs. Jaguars in 2023, at Patriots in 2023, at Patriots in 2024.`
- Problems:
  (a) "Like this" is unclear: a 17+ point gap? Say so, and give the record ("5 losses in N such games"). That needs a
      new number. The writer must compute N.
  (b) The 2024 Patriots game is Week 18 (`2024_18_BUF_NE`, 16-23). Every Bills fan will say "that's the game they rested
      everybody." The writer should verify who played and add a note. If the starters sat, say so plainly; it's an asterisk,
      not an upset.
  (c) `vs. Jaguars in 2023` was the London game (Week 5). Add "in London" or a fan will look for a home loss that isn't there.
- Rewrite: `Since 1999 the Bills have been on the good side of a gap like this (17+ points a game) N times and lost 5: at Tennessee
  and at Jacksonville in 2021, vs. Jacksonville in London and at New England in 2023, and at New England in Week 18 of 2024
  [note on starters, once verified].`
- Hero `note` has the same problem: `The Bills have lost 5 of them since 1999` -> `The Bills have been the much better team and lost 5 times since 1999, including at Jacksonville in 2021 and at New England in 2023.`

## Should fix

### 6. Lead sentence is hard to say out loud
- Exact text: `when one NFL team had been outscoring its opponents by 17 or more points a game more than the other`
- Problem: "outscoring ... by 17 more ... than the other" doubles back on itself. A host would stumble on it.
- Rewrite: `when one NFL team's scoring margin was 17 or more points a game better than its opponent's, the better team won 79% of the time.`
  Site card same fix: `NFL teams whose scoring margin was 17+ points a game better than their opponent's still lost about 1 in 5.`

### 7. "Why the biggest gaps stop helping" is too certain and the 77% sentence is hard to follow
- Exact text: `The reason is that a few weeks of scores exaggerate...`. Should be `One big reason is that a few weeks of scores exaggerate...`
  Football is also just random. Don't claim a single cause.
- Exact text: `the same two teams' margins over their whole seasons were only about 77% as far apart as they looked going in.`
- Rewrite: `by the end of those seasons, the gap between the same two teams had shrunk by about a quarter.`
  (0.77 means about 23% less, so "about a quarter" fits. Quant to confirm the wording.)
- Add one real example (needs a computed number): one team from the upset table whose margin going in and full-season
  margin show the shrink, e.g. "The 2011 Saints were +X a game going into Week 8 and finished +Y." This is the
  behind-the-scenes example CLAUDE.md requires. Right now the section has none.

### 8. Upset table doesn't stand alone
- Exact text (header): `| Season | Final | Gap going in |` with rows like `Rams 31, Saints 21 | 30.7`
- Problem: A screenshot doesn't say which team was the "better" one or what 30.7 measures. You have to work out that the
  loser was the better team.
- Rewrite header: `| Season | Final | Better team going in | Gap (points per game) |`. Fill with e.g. `Saints`.
  Bold or flag the `Jaguars 9, Bills 6` row: it's the Bills row and the best hook in the table.
- Bonus hook for Sunday: `Dolphins 31, Bears 13` (2006) is Miami pulling off one of these. One line would do: "Miami has done this before."

### 9. "15 for 15" and "band" are unclear
- Exact text: `In the seasons it never saw while being built (2024 to this year), it was 15 for 15.`
- Problem: 15 for 15 of what? A reader can't tell this is only the 10+ group.
- Rewrite: `In games from 2024 on, which it never saw while being built, teams it expected to win by 10 or more went 15-0.`
- Exact text: `in every band` -> `at every level`.

### 10. Model paragraph should tie back to the history number
- Add after the model description: `That lines up with history: in games with a gap like Sunday's, the better team won 79%.`
  This makes the two halves of the story one story (and is the radio line).

## Polish

### 11. History chart labels
- Red annotation `Bills vs. Dolphins Sunday: 18.2` -> `Bills vs. Dolphins Sunday: 18.2-point gap`.
- Y-axis `How often the better team won` -> `How often the team with the better scoring margin won` (the screenshot shows "better" undefined).
- Label the dashed 50% line `coin flip`.

### 12. Sunday numbers wording
- Exact text: `the Bills have outscored opponents by +9.8 points a game this season (2nd of 32 teams) and Miami by -8.4 (3rd-lowest)`
- Problem: "Miami has outscored opponents by -8.4" is backwards English.
- Rewrite: `the Bills have outscored opponents by 9.8 points a game this season (2nd of 32 teams), and Miami has been outscored by 8.4 (30th).`
  (If "30th" is used, confirm rank = 3rd-lowest of 32.)

### 13. Ledger line is vague
- Exact text: `This is our model's number. It counts once it's logged on the Ledger before kickoff`
- `ledger/*.csv` has no BUF-MIA row yet. Say what will happen: `We'll log Bills 81% on the [Ledger](../ledger.html) before kickoff and grade it after the game, hit or miss.`

### 14. "86 of 420" vs 79%
- 0.794 x 420 = 333.5 wins, so one tie is counted as half. "86 of 420 games" lost is right, but Quant should confirm that
  a tie isn't also in the 86. If there's a tie, "about 1 in 5" is still fine.

## Betting-language sweep
No "favorite", "underdog", "cover", "lock", "odds", "line" (apart from the disclaimer "We don't use betting lines"), "pick" or
"spread". "Upset" and "lopsided" are ordinary sports words and fine. The one problem is "Bills by about 11" (item 2), in three places.

## Jargon sweep (story body)
Mostly clean. Flagged: "blind tests" (chart subtitle), "band", "pulled toward the league average" (OK as written; it's
explained). "Points per drive" is fine for a football fan. The stat-heads section is where the terms belong and it is fine.

## Where the key numbers come from
79%: explained well ("How we measured a mismatch" plus the table). 81%: explained in plain English, and checked against results in
the second chart. Missing: one worked real example for the shrink (item 7) and one worked gap example. A single line like "Going
into Week 9 of 2021 the Bills were +X a game and Jacksonville -Y, a 28.6-point gap; Jacksonville won 9-6" would make the method
click. Needs computed X and Y.

---

# Round 2 (re-read of regenerated story, both charts, hero JSON, site card)

**One-sentence version:** "Over 27 years, when one team's scoring margin was 17-plus points a game better, the worse team
still won about 1 in 5. History and our model both put the Bills around 4 in 5 on Sunday." That's now the lead.

**Verdict: pass (ready, minor polish only).** All round 1 items were applied and read correctly. The hook is clear and true.
"Scoring margin gap" is explained, with a worked real example. The "why" section is right-sized. The upset table and the
Bills' 11-5 list land. No spread phrasing remains, and the 87% sits only in "How we checked it". I accept keeping the Ledger
line conditional, since the call isn't approved for logging yet.

## Remaining polish (fix before stage 4, none blocking)

1. **Model chart subtitle is cut off.** The right edge reads `...2024-26 are games it never saw while b`. Wrap it onto two lines:
   `Our points model's pregame projections, 2018 to Week 10 of 2026 (2,133 games).` /
   `Built on 2019-23 games; 2024-26 are games it never saw while being built.`
2. **"coin flip" label runs into the 20+ bar** on the history chart. Move it to the left end of the dashed line, or above the
   line in the gap between the 0-3 bar and the y-axis.
3. **The 79% is repeated two paragraphs apart.** The Sunday section says `the better team won 79% of games with a gap that size (220 games)`,
   then the model paragraph says `That lines up with history: in games with a gap like Sunday's, the better team won 79%.` The second one also
   splits the model description from "The model's pull toward the middle...". Delete the inserted sentence and change the bold line to:
   `**Our model's number: Bills 81%, right next to the 79% history gives.**`
4. **The worked example doesn't add up as printed.** `outscored opponents by 17.1 ... outscored by 11.4, a 28.6-point gap`: 17.1 + 11.4 = 28.5.
   A listener doing the math will catch it. The writer or Quant should check the rounding and print the parts so they sum, or write "about 28.6"
   (the 28.6 also appears in the upset table). The end-of-season numbers (11.4 + 12.0 = 23.4) are fine.
5. `the Bills have outscored opponents by +9.8 points a game`: drop the "+" (`by 9.8 points a game`). "Outscored by +" doubles the sign.

## For the Quant (new facts in round 2, not checked by the Editor)
Bills 16 games with a 17+ gap, 11-5. 2024 Week 18: Trubisky started and the starters rested. 2006 Dolphins-Bears was in Chicago.
2021 example margins: 17.1 / -11.4 going in, +11.4 / -12.0 at season's end. Also "86 of 420, plus 1 tie".

## Plain-language round (2026-11-20, after Charlie's "just say it plain" note)

**One-sentence version:** Teams that are much better than their opponent still lose about 1 game in 5, and our model gives the Bills an 81% chance against Miami on Sunday.

**Verdict: needs edits (FAIL).** The new lead is much better, but the phrase Charlie named, "go the other way", is still on the main chart title and in the hero note. "Lopsided" is still in the headline and hero label. The rename to "point differential" stopped partway: the method paragraph still says "margins" and "better margin".

Edits, most important first (exact text, then the plain version). No numbers change.

1. Chart title (nfl-mismatch-history.png, `finish(...)` in nfl_mismatches.py): "Even the most lopsided NFL games go the other way about 1 in 5 times"
   -> "Even a much better NFL team loses about 1 game in 5"
2. Hero note: "About 1 in 5 lopsided games still go the other way. The Bills have been the much better team and lost 5 times since 1999, including at Jacksonville in 2021."
   -> "A much better team still loses about 1 game in 5. Since 1999 the Bills have been the much better team 16 times and lost 5, including at Jacksonville in 2021." (16 is already in the story; otherwise keep "and lost 5 times")
3. Headline: "How often do big NFL mismatches go wrong? 27 seasons of lopsided games, and where Bills-Dolphins fits"
   -> "How often does the much better NFL team lose? 27 seasons of answers, and what it means for Bills-Dolphins"
4. Hero label (both hero JSONs): "Lopsided NFL games, 1999-2025" -> "Big NFL mismatches, 1999-2025"
5. Lead, second sentence: "The Bills and Dolphins are that far apart this season: Buffalo has outscored its opponents by 9.8 points a game, and Miami has been outscored by 8.4."
   "That far apart" points back to a definition the reader hasn't seen yet, and leaves them to add 9.8 and 8.4.
   -> "Sunday's game is one of those: the Bills have outscored opponents by 9.8 points a game, Miami has been outscored by 8.4, so the Bills are 18.2 points a game better."
6. Definition line: "\"Much better\" here means the gap between the two teams' point differentials (points scored minus points allowed, per game) was 17 or more going in. That happened 420 times; the better team lost 86 and tied 1."
   "the gap between the two teams' point differentials" is a stacked phrase.
   -> "\"Much better\" means 17 or more points a game better by point differential (points scored minus points allowed, per game) going into the game. That happened 420 times. The better team lost 86 and tied 1."
7. Method paragraph, leftover from the rename: "The gap between the two teams' margins is the size of the mismatch." -> "The difference between the two teams' point differentials is the size of the mismatch."
   and "how often the team with the better margin won" -> "how often the team with the better point differential won"
8. Hero big-number label: "How often the much better team won (17+ point gap in point differential)" ("point gap in point differential" repeats "point" and reads as math)
   -> "How often the much better team won (17+ points a game better by point differential)"
9. Hero explainer text: "By gap in point differential going in:" -> "By how much better the team was going in (points a game):"
10. Chart x-axis label (history and home charts): "Gap between the two teams' point differentials going in (points per game)"
    -> "How much better the better team was going in (point differential, points a game)"
11. Section header "Why the biggest gaps stop helping" -> "Why a bigger gap stops mattering past 17 points"
12. "A team that has been crushing people is usually good, but not as good as its early scores say, and the same goes in reverse."
    -> "A team that has been crushing people is usually good, just not as good as its early scores say. A team getting crushed is usually not quite that bad."
13. "Early in the season the effect is stronger: with a 17-point gap or more, the better team won 75% through Week 8 (164 games) and 82% after (256 games)."
    -> "This matters most early in the season. Much better teams won 75% of the time through Week 8 (164 games) and 82% after that (256 games)."
14. Upsets paragraph: "The Bills have been the much better team (a gap of 17 or more) 16 times since 1999: they went 11-5."
    -> "The Bills have been the much better team 16 times since 1999. They went 11-5."
15. Model paragraph, stacked clauses: "It's built from each offense's points per drive and each defense's points allowed per drive this season, blended with last season's numbers and pulled toward the league average while the season is young, plus how many drives each team usually gets and home field."
    -> "It starts with how many points each offense scores per drive and each defense gives up per drive. Early in the season it leans on last year's numbers and on the league average. Then it adds how many drives each team usually gets, and home field."
16. "The model's pull toward the middle is why it rarely expects a blowout: ..." -> "Because it leans toward average, it rarely expects a blowout: ..."
17. "Our model's number: Bills 81%, right next to the 79% history gives." -> "Our model: Bills 81%. History says 79%."

Blurb (build.py "nfl-mismatches"): reads plainly. OK as is.
Charts: model chart reads fine.

## Plain-language round 2 (re-read after rewrites applied)

**Verdict: ready (PASS).** All 17 edits are in. "Lopsided", "go the other way" and "scoring margin" are gone, and the method paragraph says "point differential" throughout. Lead, headline, chart titles and axes, hero labels and note, and the site blurb all read as a fan or host would say them. Charts re-viewed: the history chart's title and x-axis are plain, and the model chart is unchanged.
