# Quant review: 2026-11-11-sabres-hot-cold

Round 1 verdict: FAIL (one must-fix). Round 2 verdict: PASS.

Independent re-derivation (reviewer's own code, not the generator), AS_OF 2026-11-10, regular season only:
- GP/G/A/P for all 24 Sabres skaters match skaters.json and the story table (0 mismatches), and the feed's running totals.
- Rating rebuilt from the stat-heads formula: rate_p82, rate_g82, proj_g, proj_p match for all 24 (max diff 0.0). Tage fin_ratio 1.287 -> "about 29%".
- Back-test: 6.43/9.51/7.28/12.24 (632 skaters); goals 3.28 vs 5.28; halfway 4.34/4.82/5.09; MSE and 0.868/0.743 correlations match player_model_backtest.json.
- fit() on 2024-25 alone returns W=0.5, K=5 (xG) and K=10 (assists); FIN_SHRINK 40 is best on 2024-25.
- Text claims: 8 ahead / 9 behind; hot gaps Power +29, Quinn +25, Benson +20, Thompson +16; cold McLeod -27, Doan -23, Norris -21, Crevier -13; Quinn 9 G on 6.1; Power 12 A; Benson 13 of 15; Thompson best rating on roster.

Round 1 issues (all fixed in round 2):
1. Must-fix: Ledger promise without ledger entries -> removed.
2. xG model trained including 2025-26; rescale uses full season -> stat-heads caveat added. Leak-free re-run: points error 6.43 either way.
3. Method text said "points" blended; code blends assists and chances -> fixed.
4. "Adjusted slightly" finishing (1.29 for Thompson) -> fixed, % computed from fin_ratio.
5-9. Eighth weight added; lead split; "due" -> "should pick up"; assist line made definitional; card pace hidden under 10 GP.
Optional nit applied: "only player stats known at that point".
