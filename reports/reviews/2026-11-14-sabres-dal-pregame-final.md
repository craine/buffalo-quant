# Stage 4 final check: 2026-11-14 Sabres at Stars pregame (sha256 07a7794d6267...)

**Verdict: PASS.** No required fixes.

I re-derived every number independently, reading data/buffalo.db read-only. My scratch code is in /tmp/f4/a.py, b.py and c.py. I did not use the generator or the logger.

## Model call and Ledger
- The ratings use games before Nov 14. The latest game in the data is 2026-11-12 (309 games). League average 2.994 (unrescaled). Ratio 1.048.
- Ratings: BUF attack 3.072, DAL defense 2.734.
- Expected goals: DAL 3.494, BUF 2.789. Tie after 60 minutes 0.157. P(DAL) 0.616, so the story's **62/38** holds.
- Home term 0.272 ("about 0.27"). Training-season home win rate in OT/SO 0.545 ("55%", n 543).
- P0011 matches: probability 0.38, nhl-game-v0.1, notes "BUF 2.79, DAL 3.49; tie after 60 0.157; data through 2026-11-12".
- Logged at 2026-11-14T00:05:13Z. Puck drop is 8 PM ET on Nov 14, which is 2026-11-15T01:00Z, so it was logged before puck drop. That also matches the story's "Logged ... 00:05:13 UTC".
- Model test, 2025-26: 1,312 games, called right 54.6% (55%), home team won 52.2%, Brier 0.2446. 2026-27: 309 games, called right 60.5% (61%), home team won 55.0%, Brier 0.2303. The 60-65% bin had 231 games and that team won 61.9% (62%).

## Team table (rescale factor 0.9922)
- Created: BUF 3.088 (13th), DAL 3.012 (16th). Allowed: BUF 3.245 (27th, which is 6th-most), DAL 2.627 (4th). League 2.971.
- Share of chances: BUF 48.8% (20th), DAL 53.4% (9th).
- Goals scored and allowed: BUF 2.895 / 3.579, DAL 2.889 / 2.722.
- Close shots (<20 ft) allowed: BUF 12.84 (13th), DAL 11.06 (2nd), league 13.31.
- Rebound shots allowed: BUF 2.84 (10th), DAL 2.06 (1st), league 3.31.
- Last-5 share: BUF 50.2%, DAL 52.1%.
- Records: BUF 8-7-4 in 19 games, DAL 10-6-2 in 18.
- Recent results: BUF lost 8-3 at home to TBL on Wed Nov 11, then lost 3-2 in OT at CHI on Nov 12. DAL lost 8-3 at home to WPG on Nov 12.
- Shot facts, 2023-24 to 2025-26: 336,462 shots, 13.75% from within 10 ft (13.8%), 0.81% from 60+ ft (0.8%).
- Oct. 8 at BUF: DAL won 4-0. Chances 2.57 BUF vs 2.11 DAL (2.6 vs 2.1).

## Bounce-back
- Next-game win rate by previous result: lost by 4+ 0.463 (697), lost by 1-3 0.493 (3,486), won by 1-3 0.513 (3,482), won by 4+ 0.508 (697). All other results combined 0.504 (7,665). These match the lead, body, chart, hero bars (0.463 / 0.504) and dek.
- Out of sample, 2025-26 and 2026-27: after a loss by 4+, the model gave 0.487, the teams won 0.460, n 261. Other teams: model 0.501, won 0.504. The gap of 0.027 is under 1 SE (0.031), so "small enough to be chance" is fair.

## Goals allowed and goalies
- Goals allowed: 3.58 actual vs 3.25 chances, a gap of 0.33 a game. Buffalo's goalies total -4.34 goals saved vs. average over 19 games = -0.228 a game ("about 0.23"). "Much of that gap" is fair.
- Goalie table (76 goalies; ids checked against the rosters):
  - Luukkonen: 12 games, 86.7%, -3.09, 61st
  - Ellis: 8 games, 87.3%, -0.51, 40th
  - Lyon: 1 game, 88.0%, -0.74, 43rd
  - Oettinger: 14 games, 89.5%, +3.57, 17th
  - DeSmith: 5 games, 89.4%, -0.28, 37th
- The goalie carry-over sentence uses the same wording as the earlier reviewed Sabres stories.

## Chicago contrast
- The Nov. 12 pregame said tired road teams won 38% while the model gave them 46%: the model misses this. Here the model's 49% vs. 50% for teams after a blowout means it doesn't miss it. The claim is accurate.

## Charts, hero, dek
- All three PNGs viewed.
  - Chances scatter: title 4th-fewest / 6th-most; footer has the source and 19/18 games.
  - Bounce chart: 46/49/51/51 with the n's; the title matches.
  - Model test: the 60-65% bin shows 231 games, 62% predicted, 62% won.
- The hero JSON and the dek (slug sabres-stars-pregame-nov-14) match the verified numbers.

## Brand rules
- No betting language. Grep hits were only "better".
- No stat terms in the body. xG, Poisson, Brier, GSAx and log5 appear only in "For the stat-heads".
- The prediction is logged before puck drop. Every number traces to my re-derivation above.

## Optional (not required)
- The table header says "within 20 feet", but the code counts shots under 20 ft (<20). At exactly 20 ft (<=20) Buffalo would show 12.9. This is a definitional nit and the label is acceptable.
