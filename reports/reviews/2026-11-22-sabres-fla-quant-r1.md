# Quant review: 2026-11-22-sabres-fla (stage 2)

Text: md sha256 af5cf2d2..., hero JSON, card `sabres-panthers-postgame-nov-21`, sabres-fla-post-flow.png, grade row P0020.
Independent queries on raw_nhl_games / raw_nhl_schedule / raw_nhl_plays / raw_nhl_rosters / clean_nhl_shots_xg (xg column not rebuilt), with the
nine pinned late games removed and the per-season rescale applied (scripts in /tmp/qa). Generator reproduces md, hero and PNG byte-identically in a clean copy.

**Verdict: publish with fixes (recorded as fail).** Every number checks. One time word is wrong for a story dated Nov. 22.

## Issues
1. **"They play again tomorrow, the second night of a back-to-back, at Tampa Bay (5 p.m.)"**: the story and card are dated Nov. 22, the day of the Tampa game,
   and "tomorrow" is a literal in the generator. Earlier recaps use day names. Fix: "They play again Sunday, the second night of a back-to-back, at Tampa Bay
   (5 p.m.), then come home for the Rangers." (The 5 p.m. is right: 22:00 UTC Nov. 22; consider asserting it from the schedule.)

Minor: "teams that hit the first and third keys but allowed the first goal" includes 5 team-games where nobody scored (0-0 to a shootout). With those out,
45.5% of 1,770; the story's 46% holds either way. "didn't score first" would match the preview's definition exactly.

## Verified (my numbers)
- Data: Nov. 21 games kept = 359, 360, 361, 362, 367 (DET-NYI, FINAL); 9 pinned out (363-366, 368-372), matching pins.py. 2026-27 factor 0.9935.
- Final FLA 4, BUF 3, regulation. Goals from raw plays (situationCode, scorer's side): Bennett 1st 3:00 5v5; Kulich 9:56 5v5; Quinn 2nd 5:10 5v5;
  Bennett 5:28 5v5 (18 seconds later); Bennett 3rd 0:48 at 4v5 (shorthanded; Buffalo on the power play); Thompson 8:49 5v5; Vilmanis 16:42 5v5 (3:18 left).
  No empty-net shots. Florida power-play goals 0.
- Goal chances: 10.7% (31 ft), 30.0% (4 ft), 3.5% (46 ft), 13.9% (30 ft), 9.2% (37 ft), 2.9% (34 ft), 20.5% (10 ft): table's 11/30/3/14/9/3/21 correct.
- Chances: BUF 2.923 on 33 (19 on goal), FLA 2.746 on 48 (30 on goal). Periods BUF 1.327/1.058/0.538 (9/14/10 shots), FLA 0.932/0.975/0.839 (15/17/16).
  5v5 BUF 2.286, FLA 1.966. PP BUF 0.338 (3 shots), FLA 0.585 (6 shots).
- Replays (exact): BUF win 0.442, tie 0.181, FLA 0.377.
- Goalies: Lyon faced 2.746, allowed 4: -1.254; season -1.634 in 4 games. Markstrom faced 2.923, allowed 3: -0.077. The goaltending gap (1.18) is bigger than
  the chances gap (0.18 to Buffalo) plus the one-goal margin, so "the difference was in goal" holds.
- Bennett: 3 goals from 31.0, 30.0 and 37.1 ft, worth 0.337 combined; 10 on the season. Kulich 1.247, best on the ice (Benson 0.58 next).
- Thompson 15, tied for 5th with Lehkonen (Draisaitl 22, Gauthier 21, Connor 18, Kaprizov 18).
- Keys (preview definitions, 8,598 team-games): hit 1 and 3, didn't score first: 45.58% (1,775); all three: 78.23% (2,058). This game: FLA scored first,
  BUF allowed 0 PP goals and won 5v5 chances. Buffalo this season: other team scored first 10 times, Buffalo won 4.
- Record 9-10-4. Next: at TBL Nov. 22, 22:00 UTC (5 p.m. ET), then home vs. NYR Nov. 25.
- Ledger: P0020 p 0.37, outcome 0, Brier 0.1369 (= 0.37^2), graded 02:36Z after the final. 19 graded calls, 12 right (no 50% calls); Sabres games 7, 5 right
  (P0001, P0009, P0011, P0018, P0020 right; P0010, P0019 wrong). Consistent with the WSH recap's 11 of 18 and 4 of 6.
- Hero 2.9 / 2.7; Lyon bars 4 / 2.7. Card: two keys hit (PP, 5v5) and 18 seconds, correct.
- No betting language; jargon only in "For the stat-heads". One game is labeled; Lyon's season says "in 4 games".
