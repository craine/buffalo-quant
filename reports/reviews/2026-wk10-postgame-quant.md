# Quant re-check (stage 2, revised text): reports/2026-wk10-postgame.md

**Verdict: PASS (publish).** All 7 required fixes from the first review are applied and correct. The new numbers and claims re-derive from the database (checks below). There are no new issues.

## The 7 fixes
1. **Lead:** names two run-call misses plus the Jets passing-game near coin flip. This matches the ledger: P0014, P0015 and P0016 missed.
2. **Hero note and site dek:** both say "Two of the three misses were run calls." The dek adds "counting every run" and "running game".
3. **Heading:** "The passing games and the win".
4. **QB sequence:** verified from raw_pbp, by drive, using the passer or the rusher on scrambles.
   - Smith ran NYJ drives 2, 4, 6 and 8. Klubnik ran drive 10. Smith ran drive 12. Klubnik ran drives 14 through 21.
   - Play 2022 is the Jets' last dropback of the first half, and its description says Smith was injured.
   - Play 2656 says he returned.
   - So "hurt on his last throw before halftime", "Smith came back for one drive" and "Klubnik played the rest" are all correct. The stat-heads note cites both plays and says the play-by-play doesn't explain the second switch.
5. **Rank without the 74-yard TD:** I get 12th of 296 independently (+0.267 vs the other 295 team games). It's stated in the body, the chart footer and the stat-heads. The small-sample line ("One game and 29 runs") is present.
6. **Scramble note:** now sits directly under the calls table.
7. **Bullet:** reads "Our Bills score was close; the Jets' wasn't." Numbers: 29.9 vs 31, 22.1 vs 12, range 10 to 34.

## New wording checked
- **"Buffalo was a little more likely to give up the next score than to get it (about -0.5 points)"** (play 129). nflverse's next-score chances agree: Jets 0.542, Bills 0.452, no score 0.006. EP is -0.52.
- **"The defense keeps climbing ... up from 16th."** Buffalo's points-allowed-per-drive rank by week:

  | Through week | Rank |
  |---|---|
  | 7 | 30th |
  | 8 | 25th |
  | 9 | 16th |
  | 10 | 14th (1.990; league average 2.05) |

  Three straight weekly gains, so "keeps climbing" is supported. The note that four teams hadn't played is correct (PIT, CIN, LAC, BAL).
- **"all but decided (Buffalo had a 98% chance to win)":** win probability before the snap on play 3897 is 0.982.
- **"night" -> "game":** changed in the body, the chart title and the image alt text. **"most confident in"** is present.
- **Run chart:** opened. The title reads on its own. The label says "+0.48 a run (about 14 over 29 runs)", which matches +13.84 over 29. The footer gives the source, 296 team games, the scramble note and the 12th-without-the-run note. No overlaps.

## Unchanged numbers, re-confirmed against the current text
- Score 31-12. Projections 29.86 / 22.08, P(BUF win) 0.7466.
- Bills passing: 22 pass plays, Allen 11/21, 196 yards, 1 INT, +4.63. Jets passing: 48 pass plays, -8.95.
- Smith: 13/21, 148 yards, -3.44. Klubnik: 11/20, 137 yards, 1 INT, 3 sacks, -5.51.
- Bills runs: 29 for 204 yards, +13.84 (+0.477 a run). Without the 74-yard run: 28 runs, +7.48. Close-game runs: 24, +0.325 a run.
- Cook: 18 carries, 157 yards. The 74-yard run was worth +6.36. Allen: 4 runs, 6 yards, +5.98.
- Jets runs: 20, +1.125.
- League: 67% of 296 team games had runs below zero. Best Bills game by year: 0.269 / 0.333 / 0.432.
- Drives: 11 and 11. Jets: 4 field goals, 2 turnovers, 1 turnover on downs. Bills: 4 TDs.
- Ledger: Brier 0.2806 this week. Overall 10 of 16, 0.2384.
- No betting language. No jargon in the body.

I did not re-run the generator, because it writes to reports/. The self-check stage covers whether it reproduces the committed files.
