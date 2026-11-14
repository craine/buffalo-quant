# Quant review, re-check of edited text (sha256 5b40732dce48...)

**Verdict: FAIL on one sentence (one-line fix); everything else passes.**

## Required fix

1. **Wrong reason given for 2.99 vs 2.97.** Text: "(After that blending, an average team comes out at 2.99, slightly different from the 2.97 in the table above.)"
   Blending is not the cause. The model works on chances *before* the per-season rescale (stat-heads: "on unrescaled xG"); the table is after it.
   League chances per team-game this season: 2.971 rescaled, 2.994 unrescaled; 2.971 / 0.9922 = 2.994. Blending pulls toward that same 2.994; it doesn't create it.
   Fix: "(The model works with the chances before our small season adjustment, so an average team is 2.99 there, against 2.97 in the table.)"
   The same scale difference also sits under "Buffalo creates chances worth 3.09 ... makes Buffalo's attack worth 3.07": the attack is 3.11 unrescaled, blended down to 3.07. The fix above covers it; no separate change needed.

## Checked and OK

- Lead "a little less often than everyone else (50%)": 0.463 vs 0.504. OK. Dek "a little less than usual" OK. Hero unchanged and consistent.
- "49% vs 50% for everyone else" out of sample: blowout losers 0.487 (n 261), everyone else 0.501 (n 2,917); won 0.460. OK.
  "because those teams were a little weaker": that is what the lower model number means. OK.
- "Much of that gap is in goal": 68 goals against in final scores (3.58/game), chances against 61.66 (3.25/game). Gap 6.34 = 0.33/game. Breakdown:
  goalies -4.34 goals saved vs average (Luukkonen -3.09, Ellis -0.51, Lyon -0.74) = 0.228/game, about 68% of the gap. The rest is 1 empty-net goal and
  1 shootout-deciding goal (at MTL Oct 13, 4-3 SO) that final scores count; 66 + 1 + 1 = 68. "Much of" is fair, and "about 0.23" is correct.
- Oct 8: Buffalo home, lost 0-4; chances BUF 2.57, DAL 2.11 -> 2.6 vs 2.1. OK.
- "Dallas got blown out 8-3 at home Thursday" (DAL 3, WPG 8, Nov 12). OK.
- "Second chances": rebound shots allowed DAL 2.056 (1st; WSH 2.353 next); close shots allowed DAL 11.056 (2nd; NJD 11.050). OK.
- Goalie note: same wording as the reviewed TBL/CHI pregames; the claim is backed by scripts/tune_nhl_game_model_g.py. The dangling "(see below)" is gone. OK.
- Chicago contrast: the Nov 12 story found tired road teams (second night, against a rested home team) won 38% when the model gave 46%, in 242 games it never saw.
  "Lose more often than our model says" is accurate. It leaves out "against a rested home team", which is acceptable in a one-line callback; it's linked.
  The contrast holds: back-to-back gap 8 pts, about 2.6 SE; blowout residual 2.7 pts, under 1 SE.
- Ledger: P0011 created 2026-11-14T00:05:13Z, before puck drop (2026-11-15T01:00Z). Probability 0.38, nhl-game-v0.1. Notes BUF 2.79 / DAL 3.49 / tie 0.157
  match my independent rebuild (2.788 / 3.493 / 0.1569). The story's timestamp matches the CSV.
- All other numbers are unchanged from the stage-2 review and were verified there. No betting language; the body has no jargon.
