# Editor review, round 3: 2026-wk12-kc-postgame (stage 3)

**One sentence:** "Cook carried the Bills 32 times in the rain, and Tyler Bass tied it from 54 and won it from 57 with 4 seconds left. The kicks and returns did more for Buffalo's chances than the passing game took away."

**Verdict: needs edits (FAIL).** The new angle is better radio than the Allen yards angle, and the headline is a good three-beat hook.
No betting language. None of the rejected phrases. The part 3 and part 4 links are valid. Numbers are generator variables. "Since 1999"
must change to "since 2018" (Quant must-fixes 2-3), and nothing in the text is worded as an all-time record.

## Edits, most important first
1. Apply Quant must-fixes 1-4 (2018 window for the Cook and kick claims, "won" not "tied or won", new chart file name).
2. **Explain the key number (standing rule).** The story never shows where +64 comes from. After "Every play changes a team's chance to win."
   add, with numbers the writer computes: `Buffalo started at 55% and finished at 100%. The 57-yarder alone took it from about 76% to 100%, and the punt return just before it was worth about 22 points.`
   That gives a fan the "how we got it" in one real example.
3. **"points" reads as scoreboard points.** In the body replace `about **+64 points** of win chance` with `about **+64 percentage points** of win chance`.
   In the hero note replace `added about 64 points to Buffalo's chance to win; the passing game took away 36` with
   `added about 64 percentage points to Buffalo's chance to win; the passing game took away 36`.
4. **Whose kicking game?** The +64 includes Kansas City's miss and fumble. In the lead replace `the kicking game and returns added about` with
   `the kicks, punts and returns, by both teams, added about`. Then the chart title "The kicking game won it" still works.
5. **Punt unit:** replace `**Kansas City's punt unit** had a bad day: punter Matt Araiza fumbled in the second quarter and got off only a 13-yard punt, and with 15 seconds left
   Greg Dortch returned a punt 17 yards to the Kansas City 39.` with
   `**Kansas City's punting:** Matt Araiza fumbled a snap in the second quarter, and the punt netted only 13 yards. With 15 seconds left, Greg Dortch returned a punt 17 yards to the Kansas City 39 and put Bass in range.`
6. **Chart:**
   - The Butker and Dortch leader lines cross. Move the Butker label above the line.
   - Subtitle `Blue dots: Bills kicking plays.` -> `Blue dots: Bills kicks and returns.`
   - Start the line at the pregame chance, not a flat 50%.
   - Title and labels otherwise read on their own.
7. **Site dek** (src/site/build.py) still leads with Allen's 81 yards. Rewrite it for the new angle, e.g.
   `James Cook carried 32 times, Tyler Bass hit from 54 and 57, and the kicks and returns swung Buffalo's chances more than anything else. Both Ledger calls hit.`
8. The "Allen's quiet day" section is the right length for a secondary note. Optional: cut "He did run 7 times."; Receipts already says it.
9. Remove the orphan Mahomes stat-heads line (Quant should-fix 9).
