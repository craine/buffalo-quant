# Final check (stage 4): reports/2026-wk10-postgame.md, sha256 fc556fa23216...

**Verdict: PASS (publish).**

## What changed since my stage-2 pass
I compared the current text with the text I passed and found exactly the three edits the coordinator listed. Nothing else changed. The hero JSON and site dek are the same as at my pass.

1. **Lead:** "counting every run, Buffalo's designed runs had the best game of any team's this season".
   - Correct: Buffalo ranks 1st of 296, at +0.477 a run and +13.84 in total.
   - Counting every run is the measure the rank uses. The body gives the 12th-place rank without the 74-yard TD.
2. **Cut:** "Last week, our call on the Bills' passing game hit by an even smaller margin." Removing it leaves no dangling reference, and no other claim depended on it.
3. **Defense bullet:** "It was 16th before Sunday and 30th after week 7."
   - I computed the ranks independently from clean_drives (regular season, SNF/MNF excluded). Buffalo's points allowed per drive and rank:

     | Through week | Points allowed per drive | Rank |
     |---|---|---|
     | 7 | 2.672 | 30th |
     | 8 | 2.351 | 25th |
     | 9 | 2.101 | 16th |
     | 10 | 1.990 | 14th |

   - League average is 2.05. "Keeps climbing" holds.

## Everything else
The rest of the text is unchanged from what I verified at stage 2: the score, projections, passing and running totals, QB splits and drive-by-drive sequence, the Cook and Allen runs, the rank with and without the 74-yard TD, drives, and the Ledger record (10 of 16, 0.24; 0.28 this week). No betting language and no jargon in the body.
