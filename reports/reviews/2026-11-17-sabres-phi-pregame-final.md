# Final check (stage 4): 2026-11-17-sabres-phi-pregame — PASS

## Required fixes from round 1

Quant
1. Home-team over-credit: done ("One caution, and it matters tonight"); road-trip edge now put down to it. Numbers verified below.
2. Skid uses the 4 losses only: done. My figures: share 48.3%, xGF 12.10 / GF 6, xGA 12.94 / GA 17 (matches final scores; the 8-3 TBL game is 3.54 xGA / 8 GA, so it accounts for more than the whole 4.1 gap). "1 in overtime" = Nov. 12 at CHI, OT.
3. "only because" softened to "mostly because ... can't rule out a small one": done.
4. Hero: note and "goals just haven't gone in" fixed. Explainer title still reads "A skid tells you nothing the chances don't already show." (see minor issue).
5. Model-test chart title not cut off: done (looked at the image).
6. Out-of-sample caveat in stat-heads: done.
7. Goalie claim traceable: r = 0.07 / 0.45 / 0.17 reproduced independently (52/53/52 goalies, 400+ shots each half; same with game-date or goalie-game median split). "Weak guide" fits. The Vegas preview link target `sabres-vegas-pregame-nov-8` is in ARTICLES (and LEGACY) and says the same (Brier 0.2375-0.2377 vs 0.2375; 0.07-0.45).
Minor: exact calculation sentence and "full season, blended with last season": done.

Editor: items 1-10 all applied (forward-looking watch list with Woll +4.5 / Vladar -3.5; aside moved; "chances allowed, 3.11 a game"; myths chart labels and subtitle; lead "no sign of wearing down"; back-to-back wording; hero; model-test title; 3.17-3.23 bridge; OT note).

## New or changed numbers (own queries)

- Home calibration: 2025-26 mean model p 0.5492 vs home won 0.5221, 1,312 games (raw game count 1,312, home win 0.5221 from raw scores); 2026-27 0.5414 vs 0.5303, 330 games. Story 54.9/52.2/1,312 and 54.1/53.0: correct.
- All road games: won 0.476, model 0.452, n 1,642 -> "48% won, 45% expected, 1,642 games": correct.
- Deep trip (3rd game+): n 528, won 0.489, model 0.448; 1st game n 693, 0.486 vs 0.453: correct (own trip counter).
- 50-55% bucket 2025-26: n 528, won 0.487, said 0.525 (the 528 coincides with the deep-trip n; both checked separately).
- Model inputs: BUF attack 3.058, PHI allowed 3.110, PHI attack 2.779, BUF allowed 3.192, home 0.272, OT home 0.545: correct.
- Rest: BUF last played Sat Nov 14 (2-0 at DAL), PHI last game Nov 15 (Sunday): correct; "two days off" correct.
- Skid numbers above.

## Overclaims, jargon, betting

No jargon in body (stat terms only in stat-heads). No betting language. "Buffalo's real chance may be a little better than 48%" is properly hedged and consistent with the logged number being the model's.

## Reproducibility

Saved copies, re-ran `src.reports.sabres_pregame_phi`: markdown and hero JSON identical; all three PNG md5s unchanged.

## Charts

Chances (5th-fewest / 6th-most, footer has n), myths (labels "2nd game of trip", subtitle covers both panels), model-test (title "Teams our model gave 50-55%, like Philadelphia tonight, won 49%" fully visible, n per bucket). All fine.

## Minor (non-blocking, hero JSON only; does not change the story text)

- Hero explainer title "A skid tells you nothing the chances don't already show." is stronger than the body ("can't rule out a small one", n=219, SE 0.034). Suggest: "A skid hasn't told us more than the chances already show." Changing it in the generator leaves the markdown (and this check's hash) unchanged.
