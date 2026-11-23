# Quant review, round 2: 2026-11-22-sabres-tbl-swing (stage 2)

**Verdict: PASS, with one required fix outside the markdown** (hero note and card dek; see 1). Round-1 report: `-quant-r1.md`.

## Required fix

1. **The hero note and card dek still lump saves in with finishing as "rarely last".** The body and chart now say goaltending lasts partly. Checked on the first/second-half split: finishing plus saves together has r = 0.31. The top quarter goes from +17.7 to +6.3 (35% kept), and the bottom quarter from -16.6 to -7.2. So "those rarely last" overclaims and disagrees with the story.
   - Hero note. X: "Finishing and saves swung it, and those rarely last. Chances do, and Buffalo has had more of them in only 9 of 24 games."
     Y: "Finishing and saves swung it. Finishing rarely lasts, and goaltending only partly. Chances do, and Buffalo has had more of them in only 9 of 24 games."
   - Card dek (build.py). X: "Finishing and saves swung it, and those rarely last. Chances do."
     Y: "Finishing and saves swung it. Finishing rarely lasts, goaltending only partly. Chances do."

## Polish

- "In the second half they were 1 worse": the real value is -0.50, which rounds to -1. "they were right at average" is more honest and matches the explainer title. The explainer bar shows -1 for the same reason.
- Chart subtitle: "Middle and right: ... Each dot is one team-season." The right panel is bars. Say "Middle: each dot is one team-season. Right: the top quarter's average."

## Re-derived (independent team-game table; all match)

- Halves: games 1-41 vs 42-82 by date. All 96 team-seasons have 82 games, with no same-date duplicates.
  - Chances share: r 0.767. Top quarter 54.2% then 53.3%. Bottom quarter 45.7% then 45.7%.
  - Finishing: r 0.104. Top quarter +13.8 then -0.5.
  - Saves: r 0.216. Top quarter +13.4 then +4.8 (35%, so "about a third" holds). Bottom quarter -14.0 then -1.8.
  - n = 24 in each quarter.
- The stat-heads line saying odd/even gives lower values is true: odd/even gives saves 0.16, finishing -0.04, combined 0.01.
- Swing:
  - Goal margin went from -5 to +4.
  - Chances: Tampa Bay's edge grew from 0.03 to 0.53, so 0.49.
  - Finishing plus saves: -4.97 then +3.53, so +8.49.
  - Plus 1 empty-net goal (Benson). 8.49 + 1 - 0.49 = 9.
- Goalies, Nov. 11: Luukkonen -2.21 (5 goals on chances worth 2.79, pulled after the fifth), Ellis -2.20 (3 on 0.80), Vasilevskiy +0.56. Nov. 22: Luukkonen +1.58 (2 on 3.58), Hildeby -1.95 (5 on 3.05). Ellis didn't appear on Nov. 22.
- "Only 8 NHL teams have done it in a smaller share": by rate, VAN, SJS, CGY, CHI, CBJ, PHI, TOR and NYI are below 37.5%. WPG is tied and correctly not counted.
- Buffalo's goal gap: chances say -6.57. Not counting empty nets, the gap is -11 (all goals -10: empty-net goals +3/-1, and one shootout loss). Finishing plus saves -4.43, so "a few goals" fits.
- Best nights: Oct. 6 Minnesota +1.99 and Oct. 3 Chicago +1.97, so "about two goals more" holds.
- Unchanged from round 1 and still matching:
  - 57.3% of 3,936 games; 47.8% of the chances, 22nd; Rangers 52.7%, 9th; Thompson 17, 5th; 10-10-4.
  - Keys: one Tampa Bay power-play goal; Buffalo scored first, then Tampa Bay tied it; five-on-five chances 2.43 vs 2.62. Key 2 is now "missed", consistent with Florida, so it's one of three. Tampa Bay was 10-1 at home before the game.
  - Ledger: P0022 0.4225; 13 of 21; 5 of 8.
- Hero: 9 and 8.5 share a unit, and the bars render 100% and 94%. The explainer shows 14 and -1 with fmt "num", and it renders.
- Reproduction: in a clean copy with the outputs deleted, the generator re-creates the md, hero JSON and PNG byte-identically. Its own asserts pass.
- Site build: with the review gate stubbed in the clean copy, the build exits 0, and the article page and homepage hero render. Unstubbed, the gate blocks the build until reviews pass.
- No betting language. No jargon in the body.
