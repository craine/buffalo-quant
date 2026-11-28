# Quant review: 2026-11-27-sabres-pit-pregame (commit 3a61acf6)

**Verdict: FAIL. One required fix (a small sample with no label). Every number checks out.**

## Re-derived independently
I wrote my own SQL and pandas against `raw_nhl_games`, `raw_nhl_schedule` and `clean_nhl_shots_xg`. I did not run the generator.

| Claim | Story | Mine | OK |
|---|---|---|---|
| Games through 11-25, none 11-26 | 399; none | 399 regular-season games, all OFF; 0 scheduled on 11-26 | yes |
| Records BUF / PIT | 11-10-4 (26), 7-15-2 (16) | same | yes |
| BUF home / PIT road | 5-6-0 / 3-9-1 | same | yes |
| PIT 2nd-fewest points | 2nd | VAN 13, PIT 16, LAK 18. No tie at 16. Also 2nd by points percentage (.333; VAN .241) | yes |
| Share of chances PIT / BUF | 50% (14th) / 48% (22nd) | 0.5041 (14th) / 0.479 (22nd). Rank is on the season share. Neighbours DET 0.5012 and BOS 0.5004 also round to 50%, but 14th is the correct rank. | yes |
| PIT finishing | about 8 fewer, 28th; "only 4 worse" | -8.2; 28th per game and 28th by total; 4 teams worse | yes |
| PIT goaltending | about 7 more allowed, 27th | -7.0; 27th per game and 27th by total | yes |
| BUF finishing / saves | 15th / 18th | +0.5 (15th), -1.0 (18th) | yes |
| Worth 74, scored 66 | | xGF 74.2, non-empty-net GF 66 | yes |
| Net about 15 | 15.2 | 8.218 + 6.994 = 15.2 | yes |
| Within 10 ft / 40+ ft | 14% / 2% | 13.53% (n 4,663) / 2.18% | yes (13.5 rounds to 14) |
| Rescale factor 2026-27 | 1.001 | 1.00138 | yes |
| Lizotte | 0 goals on chances worth about 3 | 0 G, 3.26 xG, **41 shots in 20 games** | number OK, **no small-sample label** |
| Silovs / Murashov games | 15 / 9 of 24 | same | yes |
| Goalie table (5 rows) | see story | UPL 15 gp, .885, +0.83, 28th; Ellis 8, .873, -0.30, 40th; Lyon 4, .890, -1.54, 50th; Silovs 15, .874, -4.08, 65th; Murashov 9, .891, -2.91, 58th; 79 goalies | yes |
| Split-half, 96 team-seasons, all 82 GP | | 96, all 82 | yes |
| Bottom-quarter finishing | -12 to -2 (n 24) | -11.94 to -1.73 (n 24) | yes |
| Bottom-quarter goaltending | -14 to -2 (n 24) | -14.02 to -1.83 (n 24) | yes |
| Thompson 17 goals, 5th | | 17, alone in 5th (23, 23, 20, 19 ahead; next 16). No tie. | yes |
| Novak and Rakell 9 each | | 9 each, a two-way tie, disclosed. Next is 7 (Robertson, Malkin). Same method as the NYR preview: goals from the shots table, empty-net included. No period above 4, so no shootout goals in the count. Empty-net goals: 0 / 0 / Thompson 0. | yes |
| Rest | both last played Wednesday | both last played 2026-11-25 (a Wednesday) | yes |
| Last season | won 1 of 3 | L 2-4, L 2-5, W 5-1 | yes |
| Puck drop | 8 p.m. ET | schedule 2026-11-28T01:00:00Z (game 2026020413) | yes |
| Model | 51%, 3.3 v 3.3, tie 16% | p 0.5082, mu 3.346 / 3.338, tie 0.157, coefficients -0.254 / 1.032 / 0.272, OT 0.545 | yes |

## Logger
`src/ledger/log_sabres_pit_nov27.py` calls `ratings(..., "2026-11-27")`, the same as the story's RATINGS_BEFORE. That gives 0.5082, logged as 0.51. Game id `NHL_20262027_2026-11-27_PIT_at_BUF` follows the existing ledger convention (P0023 is the NYR game). Puck drop is 2026-11-28T01:00Z, which matches the schedule. It has not been run (Charlie has not approved it). The story text correctly says "counts once it's logged".

## Brand and CLAUDE.md
- No betting language ("close to even" is fine). No penalty counts. Ties are disclosed (Novak/Rakell). Points rank has no tie.
- **Required fix:** Lizotte's "0 goals on chances worth about 3" rests on 41 shots and has no label. CLAUDE.md requires small samples to be labelled.

## Advisory (not blocking)
- Goaltending bounce-back. The mean fell from -14.0 to -1.8, but 16 of the 24 bottom-quarter teams were still below average in the second half (median -3.5). By comparison, 13 of 24 stayed below for finishing (median -0.7). Second-half saves correlate 0.22 with the first half; finishing correlates 0.10. "Mostly not lasted" holds on size. "So does the goaltending" is a bit flatter than the evidence. Option: "So, mostly, does the goaltending."
- The linked goalie cards (daily refresh, `goalies_league.json`) show slightly different values: UPL +0.6 (29th) vs. the story's +0.8 (28th), Silovs -4.0 vs. -4.1, Murashov 57th vs. 58th. CLAUDE.md says card values move by design. A reader who clicks through will see small differences.
- `reports/published_images.json` has an uncommitted change in the worktree that freezes `sabres-pit-nov27-chances.png` (hash 131248f1..., which matches the PNG). It is not in commit 3a61acf6, so commit it before publishing.

## Required fix (generator, then regenerate)
In `src/reports/sabres_pregame_pit_nov27.py`, after `cold_name = names[cold_id]` add:
`cold_n = int((cur[cur.team == THEM].shooter_id == cold_id).sum())`

Old text:
`{cold_name} has the biggest gap on the team: {int(cold.g)} goals on chances worth about {cold.x:.0f}.`

New text:
`{cold_name} has the biggest gap on the team: {int(cold.g)} goals on chances worth about {cold.x:.0f}, from {cold_n} shots, a small sample.`

Rendered: "Blake Lizotte has the biggest gap on the team: 0 goals on chances worth about 3, from 41 shots, a small sample."
