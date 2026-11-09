# Quant final check, round 2: Sabres post-game, Vegas 4, Buffalo 1

**Result: PASS.**

All six fixes appear in the regenerated story and the site summary. The extra "In all" edit is correct. Re-running the generator reproduces `reports/2026-11-08-sabres-vgk.md` byte for byte.

## Changed lines checked

1. **Carry-over bullet:** now credits each finding to the test that produced it.
   - Chances allowed carry over from one half of a season to the next (pregame test: 0.75, 0.63, 0.69, against 0.07 to 0.45 for goalies).
   - A team's edge in chances carries over from one season to the next better than finishing or goaltending (50-win story: 0.72, against 0.32 and 0.21).
   - "One night isn't a trend" is included. Supported.
2. **Hot-night line:** now reads "our model doesn't try to predict a goalie's hot night; our tests say it can't be done reliably from a goalie's recent numbers." The claim now covers only our model and our tests. Supported.
3. **Receipts:** "That meant our model leaned slightly toward Vegas" uses the house word, and "favorite" is gone. Nothing in the changed text is betting language.
4. **Vegas defense:** "4th-fewest chances overall coming in" now says it is an all-situations rank (2.60 a game). Correct.
5. **Blocked shots:** "A team has about 15 shots blocked in a typical game, and only 7 times in 556 team games..." Average 15.4; 7 of 556. Correct and no longer ambiguous.
6. **Site summary in `src/site/build.py`:** "Our model leaned slightly to Vegas, a hit, but a near coin flip." Consistent with the story.
7. **Extra edit:** "In all, the Sabres created 3.9 goals' worth, well above their 3.1 average." 3.9 is the all-situations total (3.91) and the average coming in was 3.09. Correct.

No new issues. I edited no files and did not run the Ledger grade script.
