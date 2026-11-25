# Editor review: 2026-wk12-kc-mahomes (stage 3)

**Verdict: FAIL (needs edits).** The angle is good and a fan would finish it. But the Quant's data refresh changes the Buffalo run
number (20th → 27th), and that changes the lead, "What it means Thursday", the hero, the card and the chart. Several lines also overclaim or use stat words.

**One-sentence version:** "When defenses have slowed Mahomes, they got pressure, took away the deep ball and stopped the run. Buffalo
gets the pressure, but its run defense is near the bottom of the league."

That's a better radio line than the current lead, because 27th is a real story for Thursday. The Bills can't stop the run, and the Chiefs run well.

## Must-fix edits (most important first)

Numbers marked * come from the Quant's re-run on current data. The writer must regenerate them, not type them in.

1. Lead, last sentence.
   - Now: "Buffalo's defense does the first one as well as almost anyone. On the other two, it ranks 20th in both."
   - Replace: "Buffalo's defense gets pressure as well as almost anyone. Against big plays it ranks 20th, and against the run it ranks 27th*."
2. Lead, second sentence (overclaim).
   - Now: "The games where they struggled had three things in common: the defense pressured Mahomes, kept him from hitting big passes, and stopped the Chiefs' running game."
   - Replace: "Defenses that slowed them down tended to do three things: pressure Mahomes, keep him from hitting big passes, and stop the Chiefs' running game."
3. Lead, third sentence (8-game sample needs a plain label; "won 50% of the time" is stiff).
   - Now: "When a defense did all three (8 games), Kansas City scored 16.5 points a game and won 50% of the time."
   - Replace: "In the only 8 games where a defense did all three, Kansas City scored 16.5 points a game and went 4-4."
4. Section 3, first sentence ("running backs" is wrong; "success rate" is jargon).
   - Now: "When a defense held the Chiefs' running backs below their usual success rate, Kansas City scored 22.4 points and won 67%."
   - Replace: "When a defense stopped the Chiefs' runs more often than usual, Kansas City scored 22.4 points and won 67%."
5. Section 3, "It shows most in their worst games: in the 17 where they scored 20 or fewer, their runs succeeded 34% of the time, against 44% in the rest."
   - Replace: "In the 17 games where they scored 20 or fewer, their runs worked 35%* of the time, against 44% in the rest."
6. Section 3, Buffalo line: update to 46%*, 27th*, league average 43%*, Kansas City 48%*, 5th*.
7. "All three at once", the none comparison and the 8-game label.
   - Now: "In the 8 games where a defense did all three, the Chiefs averaged 16.5 points and won 50%. In the 8 where it did none of them, 25.5 points and 75%."
   - Replace: "In the 8 games where a defense did all three, the Chiefs averaged 16.5 points and went 4-4. That's a small sample. In their other 47 games: 25.0* points, and they won 72%*."
   (25.0 and 72% are Quant-computed and need generator code. Or keep the none group as "went 6-2".)
8. "What it means Thursday", wrong after the refresh.
   - Now: "The question is the pass coverage and the run defense, which have been a bit worse than the middle of the league."
   - Replace: "The question is everything else. Buffalo is 20th at stopping big pass plays and 27th* against the run, and Kansas City runs the ball well (5th*)."
9. "How we measured it", running-game bullet (definition wrong: the code uses the scoring-chances rule, not yards).
   - Now: "share of designed runs that were "successful" (gaining at least 40% of the yards needed on first down, 60% on second, all of it on third or fourth). Typical: 41%."
   - Replace: "share of designed runs (not quarterback scrambles) that left the Chiefs more likely to score than before the snap. On first-and-10 that usually takes 5 yards. On third-and-2, it means getting the first down. Typical: 41%."
   (Back "usually takes 5 yards" with a computed figure in the generator: a 5-yard run on first-and-10 counts 70% of the time, 4 yards 9%.)
10. "How we measured it", last sentence.
    - Now: "These are associations from 55 games, not proof that any one tactic causes a loss, and the better defenses tend to do all of them."
    - Replace: "These are patterns from 55 games, not proof that any one tactic causes a loss." (The "better defenses" clause has no code behind it.)
11. Hero `note`: "…20th against big plays and 20th against the run." → "…20th against big plays and 27th* against the run."
12. Site card dek (`src/site/build.py`).
    - Now: "In 55 starts since 2023, three things went with Mahomes' worst games: pressure, no big plays, no run game. Buffalo is 4th in pressure and 20th in the other two."
    - Replace: "In 55 Mahomes starts since 2023, defenses that slowed him got pressure, took away big plays and stopped the run. Buffalo is 4th in pressure, 20th against big plays and 27th* against the run."
13. Chart, panel 3 note: "Bills 2026: 20th against the run" → 27th* (regenerated).

## Polish (optional)

- First "dropbacks" in the body: gloss it once: "dropbacks (every pass play, including sacks and scrambles)".
- "Each of the three mattered on its own, about 2 to 3 points a game apiece" → "Each of the three still mattered with the others
  accounted for. A typical swing in any one was worth 2 to 3 points."
- Hero second line, "in all 55 Mahomes starts", doesn't stand alone. Use "Chiefs points a game in all 55 Mahomes starts since 2023".
- Chart subtitle: "'Yes' = the defense did better than in a typical Mahomes game" is fine. Consider "Bars: Chiefs points per game" in the subtitle for screenshots.

## Checked

- No rejected phrases ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end").
- No betting language. No stat terms in the body except "success rate" (edit 4) and "associations" (edit 10).
- The chart reads on its own: the title is the takeaway, games per bar are shown, and the footer has the source and the 8-game result.
- Headline, lead, hero, card and chart agree with each other but all carry the stale 20th. Fix them together.
- Charlie's angle (the run game) is there and is now the sharper half of the story. Consider leading section 3's Buffalo line with it.
