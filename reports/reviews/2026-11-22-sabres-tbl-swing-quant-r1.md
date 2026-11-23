# Quant review: 2026-11-22-sabres-tbl-swing (stage 2)

**Verdict: FAIL (publish with fixes).** The numbers reproduce. The central claim is overstated, one ranking claim is wrong, the key grade "half" doesn't exist in our grading, and the homepage hero puts two unrelated 9s on one bar scale.

Independent re-derivation: team-game table built from raw_nhl_games plus clean_nhl_shots_xg (pivot on is_home, not the generator's team_games), xG rescaled per season over regular-season games through 2026-11-22. Goals checked against raw_nhl_plays. VAN-CHI (2026020377) isn't in raw_nhl_games (still LIVE in the schedule), so the pin changes nothing today.

## Must-fix

1. **Overclaim: "hasn't carried over" / "told you nothing" / "it doesn't".** The odd/even result reproduces: r = 0.014. Quartile examples match: top quarter by chances 54.4% then 53.2%; bottom 45.5% then 46.5%; top quarter by finishing plus saves +22.2 then -1.0 (n = 24 each). Games are ordered by date within team-season: dates are ISO strings, every team-season has 82 games, and no team plays twice on one date. But the odd/even split is a lucky draw for the story:
   - Over 500 random half-splits of the same 96 team-seasons, mean r = 0.15 (90% range 0.03 to 0.28). Only 2% of random splits come out as low as 0.014. First half vs second half: r = 0.31.
   - Over random splits, the top quarter goes from +20.3 to +3.1, so about 15% carries over, not 0%.
   - **Goaltending alone does carry over.** Saves (xGA - GA, non-empty-net): odd/even r = 0.16 (season by season 0.11, 0.21, 0.19); random splits 0.18; halves 0.22. Top quarter by saves in odd games: +14.3, then +4.3 in even games (bottom quarter -14.4, then -3.4). Finishing alone: r = -0.04 (halves 0.10). Finishing is the part that washes out. Goaltending keeps about a third.
   - Fix: say "barely" and add a goaltending caveat (exact text in the editor report and the hand-off). The new numbers (14 then 4) have to come from the generator.
2. **"Only 6 NHL teams have done it less often."** Teams have played 20 to 26 games. By count, 6 teams have fewer than 9 (VAN 4, SJS 4, CGY 6, CBJ 7, CHI 7, NYI 8), and PHI, WPG, SEA and TOR are tied at 9. "Less often" reads as a rate. Buffalo's rate is 37.5% (9/24), and 8 teams are lower: VAN 16%, SJS 16%, CGY 25%, CHI 30%, CBJ 33%, PHI 35%, TOR 36%, NYI 36%. WPG is tied at 37.5%. Fix: "Only 8 NHL teams have done it in a smaller share of their games." Compute it in the generator with the rate and rank method="min".
3. **Key 2 graded "half".** The keys are binary. The Florida recap graded this key "No". The preview defines it as "the first goal, and no giving it back", though its stat-heads computation is first goal only. Buffalo scored first (Kulich, 3:35), and Kucherov tied it on the power play at 12:21. A grade of "half" is new and has no code behind it. Fix: grade it a miss on the published wording, and keep the honest note that Buffalo scored first.
4. **Hero JSON "big" values.** build.py draws bars whenever both values are numeric, scaled to the larger one. Two full-width bars now set a 9-goal swing against 9 games. They look identical and compare different things. Fix: make the second value one that shares the unit, e.g. `[8.5, "goals of it from finishing and saves"]`. Recomputed: finishing plus saves went from -4.97 to +3.53, so +8.49. The 9-goal swing breaks down as +8.5 finishing plus saves, +1 empty-net goal and -0.5 from chances. Or pass the values as strings, which turns the bars off. The hero note repeats the overclaim ("That part doesn't carry over"). Fix it with the body.

## Should-fix / polish

- "The chances moved 0.5 of a goal Tampa Bay's way. The rest came from who finished and who made saves." Checked: 0.49. "The rest" is 9.5 goals, of which 8.5 is finishing plus saves and 1 is Zach Benson's empty-netter. Better: "Finishing and saves made up 8.5 goals of it, and an empty-netter one more."
- "about 7 goals behind ... they're 10 behind": checked xGD -6.57, GD -10. The -10 includes empty-net goals (+3 for, -1 against) and one shootout loss (MTL, Oct. 13). The like-for-like gap is -11 vs -6.6, which gives the stated -4.4. The direction holds, but the 10-vs-7 comparison understates it. Use 11 (and say "not counting empty nets"), or keep 10 and drop the implied subtraction.
- Explainer bar shows "22.2" while the body says 22. Round to match (fmt "goals" gives "+22.2 goals", or round to 0).
- Goalie row "Ukko-Pekka Luukkonen, then Colten Ellis: 4.4 goals worse": correct combined (UPL 2.79 xGA, 5 GA, -2.21; Ellis 0.80 xGA, 3 GA, -2.20). Splitting it (2.2 each) is fairer to Ellis. The name order comes from sorting by goalie_id, which happens to be chronological here. It's fragile.
- Out of scope: ledger P0017 (playoffs, resolves_at 2026-11-18) is still ungraded. It's correctly left out of the 21.

## Verified (all match)

- Finals 3-8 (REG) and 6-2 (REG); swing 9; Benson empty-net goal 18:53 3rd; Buffalo 5 on Hildeby (8483710); Thompson 2 goals (5v3, 5v5), both on Hildeby.
- xG Nov 11 BUF 3.556 / TBL 3.588; Nov 22 BUF 3.050 / TBL 3.575; chance move 0.49; 2026-27 factor 1.0001.
- GSAx: Nov 11 BUF combined -4.41, Vasilevskiy +0.56; Nov 22 Luukkonen +1.58 (3.58 xGA, 2 GA), Hildeby -1.95. UPL Nov 11: 5 GA on 2.79, pulled after the 5th (3rd period 1:25). Ellis was in by 4:11.
- 96 team-seasons; r share 0.83; r combination 0.01; quartiles as above.
- 57.3% of 3,936 games (no equal-xG games; 57.0% excluding OT/SO); this season 62.2% of 752 team-games.
- BUF 10-10-4, 24 pts; 9 of 24 with more chances; 5 of 9 and 5 of 15 won; share 47.82%, 22nd (WPG 48.50% above, ANA 47.63% below, no tie); xGD -6.57; finishing plus saves -4.43.
- Best chance nights: Oct 6 MIN (+1.99) and Oct 3 CHI (+1.97). Same top two by margin and by share.
- Rangers 52.70%, 9th (FLA 52.80% 8th; no tie). Next game Wed Nov 25 vs NYR.
- Thompson 17 goals, 5th outright (Draisaitl 23, Gauthier 21, Connor 19, Kaprizov 18). Shootouts excluded, from raw plays.
- Keys: TBL 1 PP goal (5v4); BUF scored first and TBL tied 1-1; 5v5 xG BUF 2.43 vs TBL 2.62. TBL 10-1 at home before the game (the one loss was DET, Nov 14).
- Ledger: P0022 p 0.35, outcome 1, Brier 0.4225; 13 of 21 graded; 5 of 8 NHL; matches predictions.csv/grades.csv.
- Reproduction: in a clean copy with the three outputs deleted, `python3 -m src.reports.sabres_tbl_swing_nov22` regenerates the md, hero JSON and PNG byte-identically.
- `python -m src.site.build`: the review gate blocks it as designed (quant/editor/final missing, exit 1). With the gate stubbed in the clean copy, the build completes. The article page and homepage hero render; the hero issue is above.
- No betting language. No jargon in the body. The PNG is not yet in reports/published_images.json; freeze it at publish.
