# Editor review: 2026-11-22-sabres-tbl-swing (stage 3)

**One-sentence version:** "The Sabres turned an 8-3 loss into a 6-2 win against the same team without getting better chances. Saves and finishing flipped it, and that rarely lasts. Buffalo still loses the chances battle most nights."

**Verdict: FAIL (needs edits).** The angle is good and much better than the template: same teams, a 9-goal swing, and the chances didn't move it. The chart works. The lead is too long and has one stilted line, the "doesn't carry over" lines overclaim (see Quant), and three hero/card/key lines don't stand alone.

## Must-fix (replace X with Y)

1. Lead. X: "That's a 9-goal swing. The chances moved 0.5 of a goal Tampa Bay's way. The rest came from who finished and who made saves. Over the last three
seasons, that part hasn't carried over from one stretch of games to the next. The chances have."
   Y: "That's a 9-goal swing, and the chances didn't cause it: Tampa Bay's edge there grew by only half a goal. Finishing and saves did the rest. Over the last three
seasons, finishing has barely carried over from one stretch of games to the next, and goaltending only a little. The chances have."
2. X: "A hot stretch told you nothing about the next one."
   Y: "A hot stretch told you very little about the next one. Goaltending is the part that sticks a bit: the quarter of teams with the best saves in their odd games were 14 goals better than average, then 4 in their even games." (Needs generator numbers; Quant computed 14.3 and 4.3.)
3. X: "Add up how many more goals a team scored than its chances were worth, plus how many fewer its goalies allowed."
   Y: "Take how many more goals a team scored than its chances were worth. Add how many fewer its goalies allowed than the other team's chances were worth."
4. Keys. X: "Buffalo scored first but Tampa Bay tied it (half)"
   Y: "Buffalo scored first but Tampa Bay tied it (missed)". Optionally add after the sentence: "One of three, and a four-goal win."
5. X: "Only 6 NHL teams have done it less often."  Y: "Only 8 NHL teams have done it in a smaller share of their games." (Quant item 2.)
6. Card dek (build.py). X: "Finishing and saves swung it, and that part doesn't carry over. Chances do."
   Y: "Finishing and saves swung it, and those rarely last. Chances do."
7. Hero note. X: "Finishing and saves swung it. That part doesn't carry over; chances do. Buffalo has had more of the chances in 9 of 24 games."
   Y: "Finishing and saves swung it, and those rarely last. Chances do, and Buffalo has had more of them in only 9 of 24 games." Also change the hero second "big" (Quant item 4). Two 9s side by side read like a typo.
8. Hero explainer title. X: "Top quarter of teams in odd games, then even games"
   Y: "The best finishing and saving teams in half their games were average in the other half". The text line can stay.
9. Chart, right panel title. X: "Finishing plus saves: it doesn't"  Y: "Finishing plus saves: it barely does". (PNG regenerates; freeze at publish.)

## Polish

- Headline: "almost the same game as the 8-3 loss" is soft, because Buffalo's own chances dropped. Stronger and accurate: "Sabres 6, Lightning 2: a 9-goal swing from the 8-3 loss, and the chances didn't cause it".
- X: "won 57% of games (3,936)"  Y: "won 57% of 3,936 games".
- X: "What would change the outlook is more games like Oct. 6 against Minnesota and Oct. 3 against Chicago, Buffalo's two best nights for chances this season."
  Y: "What would change the outlook is more nights like Oct. 6 against Minnesota and Oct. 3 against Chicago, when Buffalo's chances were worth about two goals more than the other team's." (Needs the generator; Quant has +1.99 and +1.97.)
- Goalie row: split Nov. 11 into "Luukkonen 2.2 worse, Ellis 2.2 worse". It's fairer to Ellis and reads cleaner.
- "They've cost a little." Fine. The 10-vs-7 caveat is in the Quant report.

## Checks

- Headline, lead, hero, card and body agree on the facts. They also share the overclaim, which fixes 1, 2, 6, 7 and 9 resolve together.
- Chart: readable in five seconds. The left panel's bars and dots are labeled, and the footer has the source and sample. The middle "line" vs right "cloud" contrast is clear.
- No jargon in the body. No rejected phrasing ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end"). No "luck" in the body; the framing is fair once "barely" and the goalie caveat go in.
- Ledger paragraph is clear and stands alone.
