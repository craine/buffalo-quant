# Quant re-review (fresh Quant, Nov 12): 2026-11-12-sabres-tbl
Independent re-derivation from raw tables (/tmp/qa4). Confirmed: score, all 11 goals, power play by situationCode, chances by team, period and score state, the league trailing share of 0.533, goalie lines and the pull, team goaltending of -4.52 (4th of 596), save rates, season before/after, the Ledger, and the pregame expectations.
Issues:
1. "Coming in" ranks did not match the pregame story. Must-fix, fixed to 9th / 27th.
2. "Close to even" framing. Fixed.
3. Replay number was sampling noise. Now exact (Poisson-binomial): 1.17%, once in 85.
4. Score-effect claim. Softened, with sample size.
5. Goalie test claim. Now linked to the source story.
All fixed. The final check on the exact text follows as a separate stage.
