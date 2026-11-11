# Quant review (stage 2): Sabres vs. Lightning pregame, Nov 11, 2026

Reviewed: reports/2026-11-11-sabres-tbl-pregame.md as of 17:03:26 ET (it was regenerated during the review; numbers did not change), hero JSON, build.py dek, 3 PNGs, src/ledger/log_sabres_tbl.py.

## VERDICT: FAIL. Do not publish as is. The fix is mechanical: rebuild the clean tables, regenerate, and re-review the changed numbers.

## 1. BLOCKER: clean_nhl_shots_xg is missing the last 14 games, including Tampa Bay's Nov. 8 game at Winnipeg

- raw_nhl_games has 292 games for 2026-27 through Nov. 10. clean_nhl_shots and clean_nhl_shots_xg have only 278. The clean step (src/clean/nhl.py, then src/metrics/nhl_xg.py) was not re-run after the last raw ingest.
- The 14 missing games are 2026020279 to 2026020292 (Nov. 8 to 10). raw_nhl_plays has them (game 2026020280, WPG 4 TBL 3, has 286 plays).
- The generator divides shot totals from 16 games by 17 games played (from raw_nhl_games). That understates Tampa Bay's per-game numbers by about 1/17. The same goes for every other team with a missing game: NJD, PHI, WPG and TOR are missing two each. It also lowers the league average and adds 14 zero-chance team-games to the model's ratings (team_games fills them with 0). This makes Tampa Bay's defense look better than it is.
- **How I checked it:** I copied the DB to /tmp, rebuilt clean_nhl_shots and clean_nhl_shots_xg in the copy with the repo's own build() and fit_and_score(), and recomputed everything independently. Prior-season xG did not change: the refit is deterministic (random_state=7) and the explainer numbers matched exactly.

Published value, then the value after the rebuild:

| Item | Published | Rebuilt |
|---|---|---|
| 2026-27 xG scale factor | 0.998 | 0.989 |
| League chances/game | 2.86 | 2.97 |
| BUF chances created | 3.14 (6th) | 3.11 (9th) |
| TBL chances created | 3.17 (4th) | 3.25 (5th, 0.0001 ahead of NJD) |
| BUF chances allowed | 3.30 (30th) | 3.27 (27th) |
| TBL chances allowed | 2.59 (7th) | 2.80 (13th) |
| BUF share | 48.7% (20th) | 48.7% (20th) |
| TBL share | 55.0% (4th) | 53.8% (7th) |
| BUF close shots | 13.5 (9th) | 13.5 (14th) |
| TBL close shots | 13.1 (13th) | 13.8 (11th) |
| League close shots | 12.7 | 13.3 |
| BUF close shots allowed | 13.1 (22nd) | 13.1 (16th) |
| TBL close shots allowed | 10.6 (T-2nd) | **11.5 (3rd, untied; FLA 11.474 vs TBL 11.471)** |
| BUF rebound shots | 4.0 (3rd) | 4.0 (3rd) |
| TBL rebound shots | 3.1 (16th) | 3.2 (19th) |
| League rebound shots | 3.2 | 3.3 |
| TBL rebound shots allowed | 2.6 (7th) | 2.8 (8th) |
| BUF rebound chances/game | 0.38 | 0.37 |
| TBL last-5 share | 53.9% | **49.9%** |
| Vasilevskiy | 12 GP, 0.0 (30th) | **13 GP**, 88.3%, -0.5 (37th) |
| Luukkonen | -0.6 (40th) | 87.8%, -1.0 (44th) |
| Ellis | +1.8 (20th) | 88.4%, +1.6 (21st) |
| Hildeby | -0.8 (42nd) | 88.0%, -1.0 (42nd) |
| Model: TBL / BUF | 54% / 46% | **53% / 47%** (BUF 47.1%) |
| Expected goals TBL / BUF | 3.4 / 3.1 | 3.4 / 3.2 (3.439 / 3.201) |
| Tie after 60 | 16% | 16% (15.7%) |
| BUF attack / TBL defense / league | 3.04 / 2.66 / 2.86 | 3.09 / 2.86 / 3.00 |

**Text this breaks:**
- "Tampa Bay is tied for 2nd at keeping shots away from its net" (finding and dek): should be 3rd.
- "the Sabres allow the 3rd-most chances in the league" (finding, What to watch, dek, chances chart title): should be 6th-most.
- "Tampa Bay creates the 4th-most": should be 5th-most.
- "Lightning 54%, Sabres 46%" (headline section, finding, dek, hero): should be 53% / 47%.
- "Tampa Bay ... 2.6 a game (7th of 32 at keeping them down), and it's even stingier closer in: 10.6 ..., tied for 2nd-fewest": should be 2.8 (8th) and 11.5, 3rd-fewest.
- Rebounds chart title ("Tampa Bay is 7th at preventing them"): should be 8th.
- The goalie table changes (Vasilevskiy played 13 games, not 12).
- The whole side-by-side table changes, and so does the stat-heads factor 0.998.

**Fix:**
1. Run `python -m src.clean.nhl && python -m src.metrics.nhl_xg`, or `make ingest`.
2. Confirm that clean_nhl_shots_xg has 292 distinct 2026-27 game_ids.
3. Regenerate the story, charts and hero, and update the hand-written dek in build.py.
4. Add a validation check: every raw_nhl_games game_id has rows in clean_nhl_shots_xg, or the report refuses to run.

The Nov. 8 Vegas story is not affected: its AS_OF is Nov. 7, and the missing games start Nov. 8.

## 2. HIGH: the Ledger logger must run only after the rebuild, and must match the regenerated story

log_sabres_tbl.py uses the same inputs as the story: m.ratings(t, 20262027, "2026-11-11") with the same coef and p_ot.
- On the current stale DB it computes 0.4576, logged as 0.46. That matches the story today.
- After the rebuild it computes 0.4710, logged as 0.47.

Run it after regenerating, and confirm that the printed % equals the published Sabres %. Puck drop 00:00 UTC Nov. 12 equals 7:00 PM EST. That is correct.

## 3. MEDIUM: the generator's source does not match the original diff I was given

src/reports/sabres_pregame_tbl.py was edited at 17:03:04 and the outputs were regenerated at 17:03:26, during my review. The current md and charts match the current generator. Every number is the same as in the earlier version. Make sure stage 4 reviews this exact text.

## 4. LOW: the out-of-sample disclosure was dropped

- The Vegas story disclosed that the xG model's final fit includes 2025-26, and that a re-run with xG fit on 2023-25 only gave the same results (Brier 0.2444).
- This story keeps "tested on a season it hadn't seen" and "using only what was known before each game" but drops that note.

Restore the one stat-heads line from the Vegas story. The body wording is fine, because the xG validation itself was out of sample.

## 5. LOW: cosmetic

- The goalie cell "0.0 (about average) (30th of 75)" has double parentheses. This goes away after the rebuild (-0.5).
- A code comment still says "pinned to games before Nov 8" and "Sabres creating vs Vegas allowing". These are comments only and are not published.

## Headline check

"Buffalo's best weapon meets a defense that keeps shots away from the net" is still supported after the rebuild:
- Buffalo's best rank is rebound shots created, 3rd. Chances created is 9th.
- Tampa Bay is 3rd-fewest in close shots allowed.

But Tampa Bay drops to 13th in chances allowed (league average). Don't describe them as an elite overall defense; the current text doesn't. "Even stingier closer in" still holds: 8th on rebounds, 3rd on close shots.

## Verified (no issues)

- Records 8-6-3 and 11-4-2, and goals for and against per game 2.94/3.35 and 3.71/3.12. These come from raw games and are unaffected.
- Explainer numbers: 336,462 shots; 13.8% within 10 ft; 0.8% at 60+ ft; rebounds 11.5% vs. 6.3% other shots, ratio 1.82.
- Model test: 2025-26 (1,312 games) called 55% right vs. home 52%; Brier 0.2446 / 0.2504 / 0.2514. Buckets 52→49%, 57→54%, 62→62%, 68→69%. 2026-27: 292 games, 60% right, home 56%, Brier 0.2296. All unchanged after the rebuild. The 47/53 call is still in the 50-55% bucket, so the "slight lean" sentence holds.
- Coefficients -0.254 / 1.032 / 0.272, and home OT/shootout win rate 0.545 (shown as 55%).
- 75 goalies. Buffalo's last 5 games: 3-2-0 and 46.8% (unchanged).
- No Vegas leakage in the md, hero, dek or charts.
- No betting language. "Favorite" appears only in the calibration context, as in the story that passed review.
- No jargon in the body. Stat terms appear only in the stat-heads section.
- I did not independently re-derive the split-half correlations (0.07/0.45/0.17 and 0.75/0.63/0.69). They use only complete seasons and are unaffected by the missing games.
