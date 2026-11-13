# Quant re-check: reports/2026-11-13-sabres-chi.md (sha256 a9ede8f1580a...)

**Verdict: FAIL. Two small fixes are needed, then it passes.** All five stage-2 fixes landed correctly. The rewrite introduced one factual error, in the headline.

## Required fixes

1. **The headline is false for the full game.** It reads "Buffalo had more of the chances and still lost", but over the full game Chicago had more: 2.26 to 2.11, counting overtime.
   The story itself says so in three places:
   - the flow chart subtitle ("Final chances 2.1 to 2.3")
   - "How we measure" ("all 31 of Chicago's shots were worth 2.3")
   - the stat-heads section (CHI 2.26)

   The hero and dek both say "over 60 minutes" and are fine.
   Fix: "Buffalo had more of the chances in regulation and still lost" (or "over 60 minutes").

2. **"(2,319 games)" in the third-period section.** 2,319 is the number of times a team led by one in that window. Those come from **2,250 games**; a game can count twice when each team leads at different points. The stat-heads label ("2,319 game-leaders") is correct.
   Fix the body: "(2,250 games)", or "2,319 teams in that spot".

## Stage-2 fixes: all landed

- **League comparison.** Leader's share in the first 8:22 of the third, pulled-goalie strengths excluded: 0.4670, which matches "about 47%". Per leader: 2,319, with 31.52% at 25% or less, which matches "about 32%".
- **Power play and 4-on-4.** 0.264 of Chicago's 0.693 is 38%. Buffalo's 3 shots were all 5-on-5, so its 5-on-5 share is 0.35. Matches.
- **"Sat on" and "sat back further" are gone.** "One to watch, not a trend yet" is appropriately hedged.
- **Tired-legs section.** "A little behind all game, not more in the third" matches 0.457/0.470/0.482 vs 0.478/0.485/0.488.
  - The resampling ranges match mine within resampling noise (mine: P2 -3.0 to -0.1, P3 -2.0 to +0.9).
  - The score-adjustment caveat is present.
  - The chart title now reads "a little behind all game. They don't fade late". I looked at it and it's correct.
- **The model comparison is now 60 minutes to 60 minutes.**
  - The model's 3.45 and 2.97 vs regulation chances of 2.115 and 1.886, with a 2-2 score.
  - "The edge went the way it expected" checks out (Buffalo ahead in both).
  - The stat-heads section labels 3.45/2.97 as expected goals.
- **Dallas is cut.**

## New content checked

- **Regulation chances** 2.11 to 1.89. Through two periods 1.53 to 0.84.
- **Period table** (rounded): 0.8/0.4, 0.8/0.5, 0.6/1.0, 0.0/0.4. Correct.
- **Buffalo's first and second periods:** 67% and 62%. Correct.
- **"Tired road teams usually start a little behind"** matches 0.457 in the first period. "Overtime 3 shots to none" is correct.
- **Hero bars 0.383 / 0.468.**
  - Through Nov 12, Thursday excluded: 644 games, 0.3835; 3,107 games, 0.4680.
  - The pregame's numbers (through Nov 11): 643 games, 0.3826; 3,099 games, 0.4676.
  - Both render as 38.3% and 46.8% (the build uses one decimal for pct), so they are consistent with the pregame story.
- **Goalie paragraph.** The 37% usual-starter and 0.06-goal figures match the pregame text (lines 57-58; its notes give GSAx per game -0.059).
  "Third goalie" is correct: Buffalo's 2026-27 starts are Luukkonen 12, Ellis 8, Lyon 1.
- **"Lose more often than their chances say."** This is a fair paraphrase of the pregame finding.
  - Tired road teams still get 47.0% of the chances (rested 48.4%), and their goal share is close to that (46.3%, rested 48.6%).
  - But they win 38% vs 47%.
  - The story hedges it ("One game can't prove it").
- **Unchanged items still correct:** the goal table, 11:38, the 44/21/35 replays, Lyon -0.74 and Knight +0.11, Brier 0.32, 7 of 10.
- **Brand rules:** no betting language. Stat terms appear only in the stat-heads section.
- **Charts:** both looked at. The flow chart's goal dots are now Bills blue, and the footers are intact.
