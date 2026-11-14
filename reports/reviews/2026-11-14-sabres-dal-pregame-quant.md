# Quant review: 2026-11-14-sabres-dal-pregame (stage 2)

**Verdict: publish with fixes (PASS, conditional on fixes 1-2).** Every number in the body, tables, charts, hero JSON and dek re-derived independently from raw_nhl_games / clean_nhl_shots_xg (own scratch code in /tmp/qdal, own re-implementation of the v0.1 game model; generator not run, Ledger not touched). All numbers match. The problems are wording.

## Required fixes (ranked)

1. **Lead understates the blowout gap and contradicts the body.** Lead: "teams coming off a loss by four or more won 46% of their next game, about the same as everyone else." Evidence: 46.3% (n 697) vs 50.4% after any other result (n 7,665); difference -4.0 pts, SE 2.0, z = -2.0. The body itself says "if anything, they win a little less." Fix: "...won 46% of their next game, a little less often than everyone else (50%)." The headline "forget the bounce-back game" and "there's no such thing" are fine: a positive bounce is ruled out (upper end of the 95% interval on the gap is about 0).
2. **Dangling "(see below)".** In goal section: "they don't carry over well (see below), which is why our prediction doesn't use them." Nothing below shows carry-over; the generator computes the half-season goalie vs team repeatability (rep_g/rep_t) but never prints it. Fix: drop "(see below)", or print the computed half-season numbers in the prediction section as the TBL/CHI pregames did.

## Should fix

3. "Teams that get blown out tend to be a little weaker ... our model already expected them to win less often, as below." Supported but the comparison is not shown: out of sample the model gave blowout-losers 48.7% vs 50.1% for everyone else (2,917 games). That explains about 1.5 of the 4.5-pt out-of-sample gap, so "part of that" is fair. Add the 50% comparison so the reader sees "less often than what."
4. "Small enough to be chance" is fair: model 48.7%, won 46.0%, n 261, SE 3.1 pts, gap 2.7 pts (<1 SE). Note low power (can't rule out a few-point residual effect), but the claim as worded is OK.
5. Buffalo's "6th-most chances allowed" beats NYI by 0.0004 goals/game (3.2453 vs 3.2449). True and pinned, just fragile; no change needed.
6. Cosmetic: chances chart "Create a lot, allow little" label overlaps the top-right team dot. Generator comment line 103 says "pinned to games before Nov 8" (stale; code uses Nov 13 correctly). Not public.

## Verified (my numbers)

- Data: 309 games 2026-27 through 2026-11-12, all regular season (type 02), all final; no Nov 13 games in DB. Rescale factor 2026-27 0.9922.
- Records: BUF 8-7-4 in 19, DAL 10-6-2 in 18. GF/GA per game BUF 2.89/3.58, DAL 2.89/2.72.
- Team table: chances created BUF 3.088 (13th), DAL 3.012 (16th), lg 2.97; allowed BUF 3.245 (27th = 6th-most), DAL 2.627 (4th); share 48.8% (20th) / 53.4% (9th); close shots allowed 12.8 (13th) / 11.1 (2nd, NJD 11.050 1st), lg 13.3; rebounds allowed 2.8 (10th) / 2.1 (1st), lg 3.3; last-5 share 50.2% / 52.1%.
- Explainer: 336,462 prior unblocked non-EN shots; <10 ft 13.75% -> 13.8%; 60+ ft 0.81%.
- Oct 8 in Buffalo: DAL 4-0; chances DAL 2.113, BUF 2.569 (rescaled) -> 2.1 vs 2.6.
- 8-3 games: BUF 3-8 vs TBL at home Wed Nov 11; DAL 3-8 vs WPG at home Thu Nov 12; BUF 2-3 OT at CHI Thu Nov 12.
- Goalies (76 total): Luukkonen 12 GP 86.7% -3.1 (61st); Ellis 8, 87.3%, -0.5 (40th); Lyon 1, 88.0%, -0.7 (43rd); Oettinger 14, 89.5%, +3.6 (17th); DeSmith 5, 89.4%, -0.3 (37th).
- Model (own re-implementation): coef -0.2537 / 1.0316 / 0.2721, OT home 0.5451. Ratings before 2026-11-13: BUF off 3.072, DAL def 2.734, lg 2.994. mu DAL 3.493, BUF 2.788; P(DAL) 0.6158, P(BUF) 0.3842; tie after 60 0.157. Logger uses the same date ("2026-11-13"), same functions, round(p_b,2) = 0.38, version nhl-game-v0.1: matches story.
- Backtest: 2025-26 n 1,312, right 54.65%, home 52.2%, Brier 0.2446; 2026-27 n 309, right 60.5%, home 55.0%, Brier 0.2303. Calibration 60-65% bin: n 231, said 62.1%, won 61.9%. Other bins 528/426/127 match chart. No leakage: ratings use games strictly before each date; training seasons 2023-25 only.
- Bounce-back: L4+ 0.4634 (697), L1-3 0.4928 (3,486), W1-3 0.5135 (3,482), W4+ 0.5079 (697); other 0.5036. First game of each team-season excluded; OT/SO by final score. OOS L4+: n 261, model 0.487, won 0.460, SE 0.031. By season L4+: .449/.482/.481/.377 (2026-27 n 53).
- Goalie-test claim matches prior reviewed stories (VGK, TBL, CHI) and scripts/tune_nhl_game_model_g.py.
- Hero JSON and dek: 62%/38%, 46%, 0.463 vs 0.504, 4th-fewest / 6th-most: all match.
- Brand: no betting language ("likelier team" not "favorite"); body jargon-free; stat terms only in stat-heads; small-sample caveat on early-season ranks and goalies present. Charts viewed: all three have source and sample size.
