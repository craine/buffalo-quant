# Stage 4 final check: 2026-11-12-sabres-chi-pregame

**Verdict: PASS.** Reviewed exact text sha256 7ada2eec711693750e8b31003d213a1749310c1ed3a0ecacdd639b04851fdc21 plus hero JSON, build.py dek, and charts.
Did not run the generator or logger; re-derived from data/buffalo.db opened read-only (mode=ro) with scratch code.

## Required fixes from stages 2 and 3: all applied correctly
- Quant 1 (rested road also beats model): now "49% when it gave them 45%, 4 points better ... model is a little low on road teams in general ... swings that by about 12 points". Correct.
- Quant 2 ("closer to a coin flip"): removed; replaced by "tired road teams have fallen about 8 points short of what the model said". 57% stays the only logged number. Correct.
- Quant 3 (luck claim): now rests on pooled 8.5-pt gap over 643 games, 4.0 SE in stat-heads; 49-game season labeled small. Correct.
- Quant 4: "a 4-3 shootout loss" (game 2026020092, MTL 4 BUF 3, SO; Buffalo on 1 day rest). Correct.
- Editor 1 (lead, "leans" removed), 2 (results vs chances direction), 3 ("number we log" + logged timestamp line), 4 (hero explainer now matches bars), 5 ("bad bounces"), 6 (rounded 47%/48%), 7 (For Buffalo tonight; unverified "fully rested" clause dropped), 8 (3.00 vs 2.97 explained correctly as unrescaled vs rescaled, not the editor's guessed reason). All applied.

## Re-derived numbers
- Tired road (road rest 1, home 2+): n 643, won 0.3826. Rested: n 3,099, won 0.4676. Gap 0.0850, two-sample SE 0.02116, 4.02 SE. By season tired 0.410/0.367/0.383/0.347 (183/218/193/49), rested 0.464/0.443/0.502/0.442. Matches.
- Out-of-sample model check (trained 2023-25, coef -0.2537/1.0316/0.2721, OT home 0.5451): tired n 242, mean p 0.4583, won 0.3760 (-8.2 pts); rested n 1,155, p 0.4513, won 0.4909 (+4.0). Swing 12.2. "8 points short", "4 points better", "about 12 points", closing "about 8 points short" all correct.
- Tonight: BUF off 3.108, CHI def 3.330, league 3.001; expected goals BUF 3.454, CHI 2.974; P(BUF) 0.5665 -> 57%; tie 0.158 -> 16%. Matches story and Ledger notes.
- Ledger P0010: created 2026-11-12T22:57:33Z, probability 0.57, resolves 2026-11-13T01:00:00Z (8 PM ET), model nhl-game-v0.1; single row. Story's timestamp and 57% match.
- Hero: 57%/43%; 38% big number labeled with the 242-game "gave them 46%" sample; note and explainer use the 643-game 38%/47% with "against a rested home team"; bars 0.383/0.468 match. Title "Second nights cost road teams." (non-causal). OK.
- Dek: 57/43, fewest chances, "won less often than our model expects" - supported. OK.
- Unchanged table/goalie/model-record numbers were verified at stage 2 and are unchanged.

## Brand
No betting language (scan for odds/favorite/lean/pick/lock/spread/bet/line); model-test chart now says "likelier team". Stat terms only in "For the stat-heads". No uncomputed numbers found. "Both are small next to the drop in wins" is qualitative but consistent with computed mechanism numbers (1.4-pt chance-share difference, 0.06 goals/game).

## Non-blocking (recommended at stage 2, not applied)
- b2b chart footer still credits "Buffalo Quant Desk expected-goals model"; that chart shows only final-score win rates. Suggest "NHL game results" next time.
- b2b chart doesn't label the 49-game 2026-27 bar as small (the body does).
