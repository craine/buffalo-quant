# Quant final check, round 4: power-play bullet

**Result: PASS.**

The bullet is accurate, every number in it comes from the generator, and re-running the generator reproduces the story byte for byte.

## Bullet, claim by claim

- **"Vegas had the better chances, 1.8 to 0.7":** `st_a` and `st_f` are each team's total minus its five-on-five chances.
  - This game had only three states: five on five, a Vegas power play and a Buffalo power play.
  - So these totals cover exactly the penalty-box time: Vegas 1.81, Buffalo 0.72. This matches my raw count.
- **"though 0.9 of that came in the final two minutes with the game decided":**
  - `late_pp_a` is Vegas's power-play chances at 58:00 or later. It uses the same set of shots as the 1.8 (unblocked, not at an empty net), so the 0.9 really is part of the 1.8.
  - Value 0.886. My hand list: six power-play shots after Buffalo's slashing minor at 58:53, totaling 0.203 + 0.145 + 0.052 + 0.051 + 0.389 + 0.048 = 0.888. The small gap is the season rescale factor.
  - Vegas had led 4-1 since 50:00. Rounding is consistent (1.81 and 0.89).
- **"Buffalo's power play came up empty":** 5 power-play shots worth 0.49, no goals.
- **"Marner's shorthanded goal opened the scoring":** first goal of the game, 2nd period at 12:17, with Vegas down a man (4 on 5).
- **"Three of Vegas's four goals came at full strength":** `vgk_goals` counts every Vegas goal (4; none into an empty net). `vgk_es_goals` counts those at five on five: 3, by Eichel and Hertl twice. This matches the raw plays.
- **"where Buffalo had the better chances":** five on five, 3.19 to 1.84.
- **"didn't decide it":** supported. Without any power-play time the score is 3-1 Vegas, and the bullet no longer contradicts the lead ("The difference was in goal").

## Code note (not blocking)

The number words in line 233 come from fixed lists. The generator would crash if Vegas had more than 4 five-on-five goals or more than 6 total. That can't happen here because the generator is pinned to games through Nov 8, but it's worth hardening before the next post-game reuses this template.

I edited no files and did not run the Ledger grade script.
