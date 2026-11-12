# Quant review: 2026-11-12-sabres-tbl

Round 1: FAIL. Round 2: PASS. The reviewer re-derived every number with independent code in /tmp/qa3, ordering plays by raw sortOrder.

## Verified
- **Score and goals:** final 8-3 in regulation. The 11-goal table is correct: period, clock, scorer, shot, distance, chance, running score. Power-play goals checked by situationCode.
- **Score at each shot:** goals strictly before the shot. The same-second check is clean.
- **Chances overall:** Buffalo 3.52 on 50 shots, Tampa 3.48 on 29.
- **Chances by period:** Buffalo 0.65 / 1.60 / 1.27, Tampa 1.93 / 0.67 / 0.89.
- **Chances by score:** with Buffalo leading, tied or down one, 0.79 vs 2.02. With Buffalo down two or more, 2.73 vs 1.46.
- **Before the first goal:** 0.65 vs 1.31.
- **Goalies:** Luukkonen -2.31 and Ellis -2.21, with Luukkonen pulled down 5-3. Vasilevskiy +0.52.
- **Team goaltending:** -4.52, 4th-worst of 596 team-games. The 3 worse are VAN, LAK and CHI.
- **Save rate:** 0.636 vs league 0.891.
- **Season before and after:** Luukkonen -0.95 to -3.26, Ellis +1.64 to -0.57.
- **League chances for the trailing team at 2+ down:** 53% (0.5335). Buffalo's 65% while trailing is in the top 12% of comparable stretches.
- **Replays (200k):** 0.419 / 0.167 / 0.413. Tampa scored 8 or more in 1.1%.
- **Buffalo's season to date:** 3.11 created per game (10th) and 3.28 allowed (4 teams allowed more). League average 2.97.
- **Ledger:** 7 of 9. Brier 0.2209.
- **Brand rules:** no penalty counts, no betting words, no jargon in the body.

## Round-1 issues, all fixed
1. **Lead overclaimed** ("as bad as 8-3 looks"). Rewritten.
2. **Untraceable claim about the model's close-game tilt.** Cut.
3. **Uncomputed score-effects claim.** Now computed league-wide.
4. **Replay order sat inside the noise.** Now 200k runs, described as "about even".
5. **No small-sample label** on the close-game split. Added.
6. **No league context.** Added.

Nits 7-11 also applied.
