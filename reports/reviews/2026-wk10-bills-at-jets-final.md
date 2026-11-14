# Final check (stage 4): reports/2026-wk10-bills-at-jets.md

Text checked: sha256 a9078ec040c014ccbf25bc868fafb9137a3414b8b8d29ca692681c82f2bdcbf5 (matches current file).
I did not run the generator or the logger. My own scratch code is /tmp/fc10/check.py. It opens data/buffalo.db read-only and uses only points_model, model_v01 and model_v01_backtest.

**Verdict: PASS. Publish as is.** The edits since the round-2 Quant pass are: the opening rewording, "Ty Johnson", the game-by-game sentence, the ladder note, the cut duplicate disclaimer, the Ledger line and the removed tie footnote. None of them broke a number or a claim.

## Re-derived numbers
- **Projections:** coef 7.068 + 0.6785 x raw + 1.453 x home. Bills raw 33.59 (3.074 per drive x 10.92 drives), which gives 29.86 or **29.9**. Jets get **22.08 or 22.1**. Blends: Bills offense 2.729, Jets defense 2.400, Jets offense 1.805, Bills defense 2.078, league 2.055.
- **Win chance:** 1,247 pairs, Buffalo 0.7466, so **75%**. The ladder reproduces in all 16 cells: 99/90, 95/80, 92/69, 85/58, 72/41, 61/30, 48/20, 29/9. 18-42 is the 10th-90th range. 2,494 training misses: median miss 6.3, 80th percentile 12.1. Test misses averaged 7.47 over 1,264 games.
- **Raw per drive, through week 9:** Bills offense 2.889 (1st), Jets defense 2.368 (6th-most), Jets offense 1.916 (19th), Bills defense 2.101 (17th-most, so 16th-best). The story's "16th" matches the week 9 postgame's "16 of 32".
- **Pass, two-point tries excluded:** Bills 0.2633 over 273 (4th). Jets defense 0.1608 over 312 (7th-most of 32). League 0.0466. With two-point tries included, the Bills would be 0.253 over 277, so the exclusion is applied.
- **Game-by-game:** offense 0.2705, Jets defense 0.1950, league 0.0486. 0.0486 + 0.5 x (0.2219 + 0.1464) = 0.2327, so **0.23**. P = 0.798, so **80%**.
- **Example plays (2026_09_BUF_MIN):** play 2588, Q3 3rd-and-8, passer 00-0034857 (Josh Allen) to 00-0035537 (Ty Johnson in raw_players), 36 yards, EPA +3.775. Play 132, Q1 3rd-and-14, Allen sacked for -7, EPA -1.755.
- **The 80% check:** dropback backtest n=990. The 0.7-1.0 bucket has n=134, said 0.754, happened 0.776, so 75 and 78. Brier 0.2296 vs 0.2452 (pass), 0.2263 vs 0.2312 (run). Runs lost points in 63.9% of games, so 64%. The stat-heads calibration buckets all reproduce.
- **Other calls:** Jets pass 0.5515, so 55%. Bills runs lose 1 - 0.338 = 66%. Jets runs lose 1 - 0.25 = 75%. Expected values 0.028, -0.067 and -0.113 match the Ledger notes.
- **Win test:** n=632. The better-chance team was right 63.3% with ties as misses (2 ties). Home team won 51.9%. The 70%+ bucket: n=102, said 75.0%, won 74.0% with ties counted as half. Brier 0.2248 vs 0.2492 / 0.2490.
- **Ladder caveat:** pooled 0.4-0.6, n=1,744, said 0.499, happened 0.548, so "50% / 55%".
- **"Most confident pass call":** earlier pass calls were 0.57 (P0005) and 0.65 (P0006). P0008 at 0.81 is a run call, so the qualifier is right.
- **5 of 7:** P0002-P0008 graded 1,1,0,1,0,1,1.
- **20-point note:** the week 9 preview said the 20-point chances were "probably a few points low ... will fix this before using these lines again". This week has no 20+ calls on the Ledger and says the fix isn't done. Consistent.

## The Ledger
- P0012-P0016 hold 0.75 / 0.80 / 0.55 / 0.66 / 0.75, which match the table, the chart and the model output.
- Version is points-win-v0.1 for P0012 and v0.1-locshift for the other four. Game is 2026_10_BUF_NYJ, resolving 2026-11-15T18:00Z (1 p.m. EST).
- created_at_utc is 2026-11-14T00:54:53Z, which is 7:54 p.m. EST on Nov 13, about 41 hours before kickoff. The story's Ledger line is correct, including "All 5 calls".
- **Wording:** the story paraphrases the Ledger claim text, the same way week 9 did. For P0012 the story says "overtime counts; a tie counts as a miss" and the Ledger says "any result; a tie counts as a miss". These grade identically. Not a blocker, and the Ledger can't be edited anyway.

## Ties
The 63% counts ties as misses. Counting them as half gives 63.4%, and the home-team baseline moves from 51.9% to 52.1%. Both still round to 63% and 52%, so the sentence is true under either rule. The 74% sentence and the win chart footer both state the half-win rule. Dropping the footnote loses nothing a reader needs.

## Hero, dek, charts
- **Hero:** 30 / 22, 75%, 4th, 7th-worst, 134 games, 0.754 / 0.776. All correct.
- **Dek:** 29.9 / 22.1 / 75% and "one of the NFL's leakiest pass defenses" (7th-most). Correct.
- **Ladder PNG:** all 16 labels match and the footer reads 1,264 test games.
- **Calls PNG:** labels and values match and the footer is correct.
- **Win-test PNG:** buckets 315 + 215 + 102 = 632, and 75/74 matches the text.

## Brand
- Scanning the body above "For the stat-heads" found no betting words: odds, spread, line, pick, lock, favorite, bet, wager.
- No jargon in the body (no EPA, dropback or correlation).
- Every number traces to the model code I re-ran.

## Optional (non-blocking)
- Lines 14-15 have a cosmetic markdown line wrap. It renders as one paragraph.
