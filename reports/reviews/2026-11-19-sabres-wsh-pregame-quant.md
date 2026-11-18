# Quant review: 2026-11-19-sabres-wsh-pregame (stage 2)

Reviewed the regenerated text (after editor round 1, file time 2026-11-18 13:05 ET), plus hero JSON, site card, three charts and
`src/ledger/log_sabres_wsh.py`. Every number below was re-derived with my own queries on `raw_nhl_games`, `raw_nhl_schedule`,
`raw_nhl_plays`, `raw_nhl_rosters` and `clean_nhl_shots_xg` (the xG column is the one input I did not rebuild), plus my own
re-implementation of the game model's ratings, fit, Poisson and backtests (scripts in /tmp/qa, not committed).

**Verdict: publish with fixes (recorded as fail until fixed).** The numbers are right. Four text and chart issues need fixing first.

## Issues, ranked

1. **Model-test chart title is cut off.** `sabres-wsh-model-test.png` title runs off the right edge: "Teams our model gave a 55-60% chance
   to win, like Washington Thursday, won" and the 54% is lost. That's the chart's whole point, and it travels without the story.
   Fix: shorten it, e.g. "When our model gave a team 55-60%, like Washington Thursday, it won 54%", or wrap it onto two lines.

2. **"Tuch is exactly that profile."** (Tuch section.) The GM story defines the profile as players who beat their chances in all three of
   the last three seasons, and says Tuch "missed by a fraction of a goal" the year before. My numbers: 2023-24 21 goals on 21.14
   (-0.14), 2024-25 34 on 24.28 (+9.7), 2025-26 32 on 23.12 (+8.9). By that story's own test he isn't in the group.
   Fix: "Tuch is the kind of finisher he means: about 10 and 9 goals better than his chances the last two seasons, and ahead again this year."

3. **"why Charlie's shopping list starts with a proven finisher."** The GM story says the reverse order: "I'd go for help a man down
   first, then a proven finisher", and "fix the penalty kill first". Fix: "and why a proven finisher is on Charlie's shopping list,
   after help a man down."

4. **"Both teams have had 2 days off."** Both teams played Tuesday, Nov. 17 (BUF at PHI, WSH at TBL), and play Thursday: one day off.
   The code computes days between games (2) and calls it days off. (The Flyers preview made the same slip; it's published, so
   leave it alone.) Fix: "Both teams played Tuesday and have had a day off."

5. Minor: "yesterday's GM story" and "yesterday's story" are right only if this goes up on Nov. 19 (the card date). If it publishes
   on the 18th, say "Wednesday's" or "today's". The ledger has to be logged before 00:00 UTC Nov. 20 either way.

No betting language. No jargon in the body (xG and the rest are only in "For the stat-heads"). Small samples are labeled (one game,
early-season ranks).

## Verified (my numbers)

- Data: 343 regular-season games through Nov. 17 in games, schedule and shots; all 11 Nov. 17 games present (2026020333-343). 2026-27 rescale factor 0.9916.
- Records: BUF 8-9-4 (20 points, 21 GP), WSH 10-9-0 (20 points, 19 GP). Goals per game BUF 2.76 / 3.52, WSH 3.37 / 3.68.
- Table: created BUF 3.022 (14th), WSH 3.230 (5th), league 2.968; allowed BUF 3.237 (6th-most = 27th best), WSH 3.148 (11th-most = 22nd),
  league 2.965; 5v5 share BUF 50.4% (17th), WSH 52.9% (9th); PP created BUF 0.668 (17th), WSH 0.516 (26th = 7th-fewest; no ties:
  STL 0.505, WSH 0.516, SEA 0.554), league 0.660; PK allowed BUF 0.798 (4th-most = 29th), WSH 0.788 (5th-most = 28th), league 0.662.
  Rank direction in the table matches its note. The old "29th-most of 32" error in the body is now fixed ("4th-most").
- PP goals: BUF allowed 21 in 21 games; WSH scored 10 in 19 (0.53). BUF PP goals 10 (tied 28th) on chances worth 14.0: "hasn't finished them" holds.
- "Both defenses give up more than average": 3.24 and 3.15 vs 2.96. True. "almost as much as Buffalo's": 0.79 vs 0.80. True.
- PK as biggest single reason: BUF allowed vs league per game, 5v5 +0.018, opponent power play +0.136, all other states combined +0.118, out of +0.272. True, about half (matches GM story).
- Skid: VGK L, TBL L, CHI OTL, DAL L, PHI L = 5 (1 OT). xG for 14.35 and against 15.78 (share 48%), goals 9 for and 21 against. Trip CHI-DAL-PHI-WSH-FLA-TBL: game 4 of 6.
- Oct. 24 (2026020173): WSH 4-3 OT; chances WSH 4.054, BUF 2.158; Tuch 2 goals (one at even strength, the OT winner at 3-on-3).
- Tuch: 12 goals (raw play-by-play by scoring player), 1 empty net (Oct. 28, opponent goalie pulled), 11 with a goalie in net on 7.22, 19 games dressed, all for WSH.
  Team leader (next: Leonard 8). Strengths: nine at 5-on-5, one 3-on-3, one shorthanded (4-on-5), one empty net; none on the power play. Last season 32 on 23.12 (+8.9, "about 9").
- Goalies (77 total): Luukkonen 12 GP, .867, -3.1 (59th); Ellis 8, .873, -0.5 (40th); Lyon 3, .898, -0.4 (38th); Thompson 14, .885, -0.7 (41st);
  Lindgren 6, .867, -2.5 (52nd). Every goal is counted as on goal, so save % is consistent.
- Explainer: 336,462 prior shots; 13.8% within 10 ft; 0.8% at 60+ ft.
- Model (own re-implementation): coef -0.2537 / 1.0316 / 0.2721; tied games go to the home team 54.5% of the time; ratings BUF attack 3.03, WSH allowed 3.14, WSH attack 3.18, BUF allowed 3.18;
  expected goals 3.19 / 3.67; tied after 60 minutes 15.3%; **BUF 42.2%**. 2025-26: model said home teams 54.9%, home teams won 52.2% (1,312); picked the winner 54.65% (rounds to 55%); Brier 0.2446.
  2026-27: 54.2% vs 53.1%, 60.1% right in 343 games, Brier 0.2343. 55-60% bin in 2025-26: 426 games, won 54.0%. No leakage: ratings use only games before each date; the fit is on 2023-25.
- Ledger script: same model, same ratings date (before 2026-11-18), rounds to 0.42; puck drop 2026-11-20 00:00 UTC matches `raw_nhl_schedule.start_utc`
  for 2026020351; claim wording, version and notes follow the PHI logger. Not run (as instructed).
- Linked stories: the GM story backs "fix the PK first", PK 4th-most, the PP at a league-average rate but cold, and Tuch's +10/+9 and 11 goals on 7.2. The Flyers
  preview backs "skid of four or more ... as the model expected" (46% vs 46%, 219 games). The playoff story backs "cold shooting and goaltending usually don't last".
  The Vegas preview backs "first half a weak guide to second half".
  The note that numbers differ from yesterday's checks out: `pins.py` dropped 4 late Nov. 17 games from the GM story.
- Reproducibility: two clean copies (before and after the editor round) regenerate the story, hero JSON and all three PNGs byte-for-byte.
- Hero/card: 42% / 58%, "4th-most", 0.66 vs 0.80, Tuch 12 goals. All match.
- Charts: chances scatter (title "WSH 5th-most created; BUF 6th-most allowed" correct), PK/PP bars (0.52 7th-fewest, 0.80 4th-most, averages 0.66) fine; model-test title clipped (issue 1).

## Round 2 re-check (after fixes)

**Verdict: pass.** All four issues are fixed, and the fixes added no new problems.

1. Model-test title is now "When our model gave a team 55-60%, like Washington Thursday, it won 54%". It fits; I opened the image. 54% from 426 games, checked again.
2. Tuch: "a proven finisher is on Charlie's shopping list, after help a man down. Tuch is the kind of finisher he means: about 10 and 9 goals better
   than his chances the last two seasons, and ahead again this year." Matches the GM story's order and my numbers (+9.7, +8.9; 11 on 7.2 this year).
3. "Both teams played Tuesday and have had a day off." Correct: BUF at PHI and WSH at TBL on Nov. 17.
4. No "yesterday" left. The GM story is now "his GM story" or "the GM story". The site card date is 2026-11-18, the day it publishes.
   "Thursday night" and "Thursday, Nov. 19" still read correctly published a day early.

Everything after the Tuch section is the same as in round 1. A clean copy regenerates the story, hero JSON and all three charts byte-for-byte.
The ledger script is unchanged: 0.42, puck drop 2026-11-20 00:00 UTC.
