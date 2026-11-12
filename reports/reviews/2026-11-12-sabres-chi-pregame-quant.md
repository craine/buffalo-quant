# Quant review (stage 2): 2026-11-12-sabres-chi-pregame

**Verdict: publish with fixes (stage-2 FAIL until fixes 1-4 are applied).** Every number in the body, tables, charts and hero
re-derives exactly. The problems are claims and framing in the back-to-back section, not the arithmetic.

**Which text this covers.** I first read the version with SHA 1be1f564... (the one the self-check and editor reviewed). The
writer changed the generator at 17:54:36 ET, and my generator run with `DUMP=1` at 17:54:57 rewrote the story, charts and hero
from the mid-edit generator. The file now on disk is SHA c698fead... (new lead, "bad bounces" wording, a "For Buffalo tonight"
paragraph, a corrected results-vs-chances bullet, and a new hero explainer). I reviewed both versions. The numbers are the
same in both. **The writer must re-run the finished generator and confirm the output is what they intend before stage 4.**

## Required fixes (most important first)

1. **Rested road teams also beat the model by more than chance allows, and the story calls it "a little."**
   Text: "Rested road teams, by comparison, won a little more often than it said (49% against 45%)."
   Evidence (out of sample, 2025-26 and 2026-27): rested road teams got 45.1% from the model and won 49.1% (n 1,155, SE 0.0146),
   about 2.7 SE. That is slightly *further* from chance than the tired gap (45.8% vs 37.6%, n 242, 2.6 SE). Across all road teams
   the model said 45.2% and they won 47.1% (n 1,610). So the model underrates road teams in general, and "Our model misses it" is
   not only about rest. This makes the rest effect stronger: tired teams fell 8 points short while rested teams beat it by 4, a
   12-point swing. But the reader needs to know.
   Fix: e.g. "Rested road teams actually beat the model's number (49% against 45%), also by more than chance would explain. So the
   model runs a little low on road teams in general, and tired ones still fell 8 points short of it." Compute the 8 and the 12 in
   the generator.

2. **"Closer to a coin flip" is a number the code doesn't compute.**
   Text: "if tonight goes the way games like it have, it's closer to a coin flip." (The lead also says "Read our 57% as too high.")
   Evidence: the only computed adjustment is the tired-road gap (46% said, 38% won, so 8.2 points). 57% minus 8 is about 49%, so
   the direction is right, but no line of code produces it, and applying an average gap to one game is a rough estimate.
   Fix: either compute it in the generator and show the arithmetic ("in games like this the model ran about 8 points high; 57 minus
   8 is about 49, a rough read, not a logged number"), or say only "about 8 points too high in games like this." Keep 57% as the
   only logged number.

3. **"Which is why we don't think it's luck" rests on weak reasoning.**
   Text: "The gap showed up in every one of the four seasons, which is why we don't think it's luck."
   Evidence: per-season gaps are 5.4, 7.6, 11.9 and 9.5 points, and 2026-27 has only 49 tired-road games. Getting the same direction
   four times isn't strong evidence by itself. The pooled test is strong and is computable: 38.3% (n 643) vs 46.8% (n 3,099),
   a gap of 8.5 points with SE 0.021, **about 4 SE**.
   Fix: base the claim on the pooled number ("a gap that size over 643 games is about four times what chance alone would usually
   produce, and it showed up in all four seasons") and compute it in the generator. Label 2026-27 (49 games) as small in the
   text or the chart.

4. **Buffalo's prior back-to-back was a shootout loss.**
   Text: "Oct. 13 at Montreal, a 4-3 loss."
   Evidence: raw_nhl_games 2026020092, MTL 4 BUF 3, last_period_type = SO. It counts as an overtime/shootout loss in the 8-7-3
   record, and Buffalo got a point.
   Fix: "a 4-3 shootout loss."

## Recommended fixes

5. **Hero says too much.** The current hero title "Tired legs cost road teams." is causal, but the story's own mechanism
   check says chance share barely moves (46.9% vs 48.3%) and "where the drop comes from is less clear." Use "Second nights cost
   road teams." The hero `note` drops the definition ("have won 38% since 2023-24"): add "against a rested home team." The 38%
   is the 643-game figure, not the 242-game model check.
6. **"Neither explains the whole gap"** isn't quantified. Use "Neither looks big enough to explain the gap", or compute the goals
   each one is worth.
7. **"336,462 shots that weren't blocked"**: that count also leaves out empty-net shots (339,167 unblocked in total). Say "...that
   weren't blocked, not counting empty nets."
8. **b2b chart footer** says the source is "Buffalo Quant Desk expected-goals model", but the chart only shows win rates from
   final scores. Point the source line at game results. Also label "2026-27 so far (49)" as a small sample.

## Verified (independent re-derivation from raw_nhl_games and clean_nhl_shots_xg)

- **Rest definition:** days since the team's previous game in the same season. All 4,234 games are regular season (type 02) and
  final. Seasons 2023-24, 2024-25 and 2025-26 are complete (1,312 each); 2026-27 has 298.
- **Back-to-back counts:** tired road (road rest 1, home 2+) 643, won 0.3826. Rested (both 2+) 3,099, won 0.4676.
  By season, tired / rested: 0.410/0.464 (183), 0.367/0.443 (218), 0.383/0.502 (193), 0.347/0.442 (49). All match.
- **Model check:** I rebuilt the out-of-sample predictions from nhl_game_model (trained on 2023-25; ratings use only games
  before each date, so nothing leaks). Tired road: n 242, mean p 0.4583, won 0.3760, SE 0.031 (0.032 on p); gap/SE 2.6 (2.57-2.64).
  Rested: n 1,155, p 0.4513, won 0.4909. Matches the story.
- **Mechanism (complete seasons):** road chance share 0.469 tired vs 0.484 rested. Usual starter in net 0.369 vs 0.617. Goals
  saved per game -0.059 vs +0.001. Including 2026-27 gives 0.359/0.618 and -0.064/+0.006, so the complete-seasons restriction
  is disclosed and doesn't change the story.
- **Tonight's call:** BUF off 3.108, CHI def 3.330, league 3.001, ratio 1.046; coefficients -0.254 / 1.032 / home 0.272;
  overtime/shootout home 0.545. Expected goals BUF 3.454 (road, home=0) and CHI 2.974 (home=1). P(BUF) 0.5665, tie 0.158.
  `round(p_b,2)` = 0.57, matching what log_sabres_chi.py would log; logger and story both use ratings(…, "2026-11-12"), version
  nhl-game-v0.1. Chicago has home ice (if Buffalo were home it would be 66%). Puck drop 01:00 UTC Nov 13 = 8 PM ET.
- **Model record:** 2025-26 accuracy 54.6%, home won 52.2%, Brier 0.2446. 2026-27 (298) 60.7% / 55.7%, Brier 0.2291.
  55-60% bucket: 426 games, won 54.0%.
- **Team table:** chances for/against/share BUF 3.133 (8th) / 3.291 (28th) / 0.488 (20th); CHI 2.339 (32nd) / 3.416 (31st) /
  0.406 (32nd); league 2.97 (rescale factor 0.9894). Within 20 ft (<20): BUF 13.4 (14th) / 12.9 (14th), CHI 10.8 (30th) /
  16.2 (30th), league 13.3. Rebounds 3.8 (7th) / 3.1 (22nd) / 3.3. Records 8-7-3 and 4-13-1. Goals per game 2.94/3.61 and
  2.17/4.22. Last 5: BUF 47.6% (2-3-0), CHI 40.0%. "Fewest chances, 2nd-most allowed" and "5th-most allowed" check out.
- **Shot explainer:** <10 ft 13.75%, >=60 ft 0.81%, n 336,462 (2023-26 unblocked, not empty net).
- **Goalies:** UPL 12 GP, .867, -3.19 (60th of 75); Ellis 8, .873, -0.57 (39th); Knight 14, .881, -2.34 (56th); Soderblom 5,
  .842, -6.17 (69th). Both Sabres goalies faced shots on Nov. 11 (22 and 8 unblocked).
- **Schedule:** Buffalo's only rest-1 game this season is Oct. 13 at MTL. Chicago last played Nov. 7 (5 days' rest).
  BUF lost 8-3 to TBL on Nov. 11. The postgame's "better than twice" (2.0 vs 0.8 while close) is in the published postgame.
- **Results-vs-chances bullet (current text):** goals run behind chances (2.94 vs 3.13 for; 3.61 vs 3.29 against). Correct
  direction now; the earlier "run ahead... fade" version was backwards.
- **Brand:** no betting words (odds, favorite, lean, pick, line, spread, bet) in the story or hero. No stat terms in the body.
  Links to sabres-lightning-postgame-nov-11 and sabres-50-win-mirage resolve in src/site/build.py.
- **Charts:** looked at all three. Numbers and sample sizes match; layout is clean; Bills blue on the b2b and model-test charts.
- **Not re-derived here:** the home-rate (0.2504) and log5 (0.2514) Brier baselines and the goalie-repeatability claim. Both
  carry over from earlier reviewed stories.
