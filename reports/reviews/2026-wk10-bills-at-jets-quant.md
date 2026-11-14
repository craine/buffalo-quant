# Quant review (stage 2): reports/2026-wk10-bills-at-jets.md

**Verdict: FAIL (publish with fixes).** The projections, win chance, ladder, all five calls, the logger, both backtests, the ranks and the week-9 receipts all reproduce from my own scratch code. There is one real data error: the pass-play numbers count two-point tries. There are also three wording fixes.

## Required fixes (most important first)

1. **Bills dropback number includes two-point tries. It doesn't match the model or CLAUDE.md.**
   - Text: "the Bills' pass plays have gained +0.25 points each on average, 4th in the NFL, over 277 dropbacks". Stat-heads: "Bills offense +0.253 (rank 4)".
   - Evidence: `pass_ranks()` filters on `qb_dropback=1 AND epa IS NOT NULL` with no two-point filter. CLAUDE.md excludes two-point tries, and the model's `clean_team_week.dropbacks` excludes them too (273).
   - Recomputed from raw_pbp, 2026 weeks 1-9, regular season, without two-point tries: Bills **+0.263 over 273 dropbacks, still 4th**. Jets defense is unchanged at +0.161 over 312, 7th-most (no two-point dropbacks against them). League +0.047, which still rounds to +0.05.
   - Fix: add `AND COALESCE(two_point_attempt,0)=0` to `pass_ranks`. Body becomes "+0.26 ... over 273 dropbacks"; stat-heads becomes +0.263. Every other line is unchanged.

2. **The +0.23 can't be rebuilt from the numbers in the body.**
   - The body gives +0.25 (fixed: +0.26), +0.16 and +0.05. The formula in the stat-heads section, applied to those, gives about +0.21, not +0.23.
   - Why: the model averages each team's game-by-game values. Bills offense +0.270, Jets defense +0.195, league +0.049, so 0.049 + 0.5 x (0.221 + 0.146) = +0.233.
   - That breaks the "show the math" rule. Fix: add one plain clause, e.g. "the model averages game by game, which counts the Jets' worst games a bit more: Bills +0.27, Jets defense +0.19". Or use the model's per-game inputs in the paragraph.

3. **"lines" in a no-betting story.**
   - Text: "before using those lines again" (body) and "all 8 lines pooled" (stat-heads).
   - Next to "20-point calls" and a scoreline table, "lines" reads like betting lines. Fix: say "scorelines" or "the 20-point chances".

4. **The calls chart says something that isn't true yet.**
   - wk10-calls.png footer: "Logged on the Ledger before kickoff." Nothing is logged; log_wk10.py hasn't run. The story body correctly says the calls "count once they're logged".
   - This chart is also the site card image for the dek. Fix: "Logged on the Ledger before kickoff" only after the logger runs, or say "Goes on the Ledger before kickoff". Otherwise log before publishing.

## Should fix / editorial calls

- **The week-9 promise on 20-point chances.** Week 9 said "We're logging them as they are and will fix this before using these lines again." Week 10 doesn't log them, which is right and matches log_wk10.py. But the ladder table and chart still show the uncorrected 20+ chances, with a disclosure. That's defensible and honest. I'd make it explicit: "We still show them in the ladder, flagged, but we're not putting them on the Ledger until they're fixed." Charlie's call.
- **"The NFL's best offense" (headline).** It's 1st in points per drive, 2.889, just ahead of SF at 2.872. By pass plays the Bills are 4th. It's supported, and "best" refers to scoring per drive. Fine as is, but don't push it on radio as clear-cut.
- **Bills defense "16th".** It's 2.101, essentially tied with NE (also 2.101 to three decimals; NE is fractionally lower). Fine.

## Verified (my numbers, from data/buffalo.db read-only, data through 2026 week 9)

- **Game:** 2026_10_BUF_NYJ, NYJ home, 2026-11-15 13:00 ET, MetLife. Home field goes to NYJ (home=1). Correct.
- **Points per drive, 2026 weeks 1-9:**
  - League 2.055 (2,992 drives).
  - Bills offense 2.889 (260/90), 1st.
  - Jets defense 2.368, 6th-most.
  - Jets offense 1.916, 19th.
  - Bills defense 2.101, 16th.
- **Ratings, blended with last season (K=60, keep 0.7):** Bills offense 2.729, Jets defense 2.400, Jets offense 1.805, Bills defense 2.078.
- **Projection math:** points per drive 3.074 (Bills) and 1.829 (Jets). Drives 10.92. Raw 33.6 and 20.0. Calibration coefficients 7.068 / 0.6785 / 1.453, fit on 2019-23 (2,494 misses). **Bills 29.86, Jets 22.08.**
- **Ladder:** all 16 cells match (99/90, 95/80, 92/69, 85/58, 72/41, 61/30, 48/20, 29/9).
- **Misses:** half within 6.3, 80% within 12.1. Bills 80% range 18.0-42.2. Average miss on unseen games 7.47 (n=1,264).
- **Win chance:** 1,247 pairs. Jets win 25.3% (ties after regulation split half), so **Bills 74.7%, shown as 75%**. A strict Buffalo win is 73.4%; the tie zone is 2.6%.
- **Win test:** 632 games (2024: 256, 2025: 256, 2026 weeks 2-9: 120).
  - The team it leaned to won 63.3% (ties count as misses). Home team won 51.9%.
  - By bucket: 50-60% said 55, won 57 (315 games); 60-70% said 65, won 68 (215); 70%+ said 75.0, won 74.0 (102).
  - Brier 0.2248 vs 0.2492 (50/50) and 0.2490 (home-win rate).
  - Out of sample: fit on 2019-23 only, ratings use only earlier weeks.
- **Ladder caveat:** said 0.499, happened 0.548, n=1,744 (2024-26, pregame, trained on 2019-23). Matches "said 50%, happened 55%".
- **Matchup model (clean_team_week, 272 team-games in the spread), Bills pass plays:** expected +0.233, chance of gaining points **79.8%, shown as 80%**.
- **The other matchup calls:**
  - Jets pass plays: expected +0.028, 55.1% (55%).
  - Bills runs: expected -0.067, chance of gaining points 33.8%, so **lose points 66.2% (66%)**.
  - Jets runs: expected -0.113, chance of gaining points 25.0%, so **lose points 75.0% (75%)**.
  - The run calls are correctly 1 - p.
- **Matchup backtest:** 990 team-games, 2023-25, week 8 on. Each call uses only earlier weeks of that season (league mean, team means and spread all use weeks before the game), so there's no leakage. The model has no fitted parameters except shrink 0.5, which was set by hand.
  - Pass calls at 70%+: n=134, said 75.4%, happened 77.6%. Matches the story and the hero bars (0.754 / 0.776).
  - Brier: pass 0.2296 vs 0.2452; runs 0.2263 vs 0.2312. "Beat the guess / edged it" is fair.
  - Runs lost points in 63.9% of team-games, shown as 64%.
- **Logger:** log_wk10.py calls the same `points_block()` and `matchup_calls()` and rounds to 0.75, 0.80, 0.55, 0.66, 0.75. That's the same five numbers, same model versions (points-win-v0.1, v0.1-locshift), and matching claim meaning. Its wording ("add points") follows week 9's Ledger rows. Not run.
- **"Our most confident pass call yet":** true. The only earlier pass calls on the Ledger are P0005 (0.57) and P0006 (0.65).
- **"5 of 7 calls hit":** true.
  - Hits: P0002, P0003, P0005, P0007, P0008. Misses: P0004, P0006.
  - P0005 is a hairline hit: Bills week-9 dropback EPA was +0.0029 over 36 plays, so +0.00008, which is above zero.
- **Hero JSON and dek:** 30 and 22 (rounded from 29.9 and 22.1), 75%, 4th, 7th-worst, 134 games, 0.754 / 0.776. All consistent.
- **Charts:** I looked at all three. Labels match the computed values, with no overlaps; the footers have source and sample (1,264; 632; data through week 9). The only problem is the "Logged" footer (fix 4).
- **Brand:** no odds, spreads, picks or favorites anywhere. EPA and Brier appear only in the stat-heads section. Samples are shown (134, 102, 990, 632).
