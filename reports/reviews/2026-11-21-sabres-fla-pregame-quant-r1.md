# Quant review: 2026-11-21-sabres-fla-pregame (stage 2)

Reviewed `reports/2026-11-21-sabres-fla-pregame.md` (sha256 03957cae...), hero JSON, site card `sabres-panthers-pregame-nov-21`,
the three charts, and `src/ledger/log_sabres_fla.py` (read, not run). Every number was re-derived with my own queries on
`raw_nhl_games`, `raw_nhl_schedule`, `raw_nhl_plays`, `raw_nhl_rosters` and `clean_nhl_shots_xg` (the xg column is the one input
not rebuilt), with the per-season rescale applied, plus my own re-implementation of the game model's ratings, fit, Poisson and
backtests (scripts in /tmp/qa, not committed). The generator reproduces the md, hero and all three PNGs byte-identically in a clean copy.

**Verdict: publish with fixes (recorded as fail until fixed).** Every printed number is right. Three claims are not supported
as written, and one chart has overlaps.

## Issues, ranked

1. **"Florida spreads its scoring around."** Not true by any measure I tried. Reinhart and Tkachuk have 23 of Florida's 72 goals
   (31.9%); the league average for a team's top two is 29.7%, so Florida is the 22nd-most spread out of 32. Florida has 6 players
   with 5+ goals; the league average is 5.8. (Buffalo is the most top-heavy team, which may be where the idea came from.)
   Fix: "**Florida's top two.** Sam Reinhart leads the Panthers with 12 goals, and his chances add up to the most on the team, worth about 11 goals."

2. **"It cuts the other way too. Florida's penalty kill allows the 3rd-most chances in the league..."** True per game (0.83, 3rd-most),
   but misleading. Using situationCode time, Florida has been shorthanded 6.79 minutes a game (2nd-most); per minute shorthanded it
   allows chances worth 7.30 goals per 60 minutes, the league average is 7.31 (15th of 32). Florida's kill is average once it's out
   there; the per-game number comes from taking a lot of penalties. "Buffalo scored twice on the power play in Washington on Thursday"
   is correct (Dahlin and Thompson, both 5-on-4), but "twice" is a hard-coded literal, not computed or asserted in the generator.
   Fix (writer computes shorthanded time and the Thursday PP goal count in the generator):
   "Buffalo may get chances of its own. Florida has spent more time a man down than all but one team, though its penalty kill is about
   average once it's out there. Buffalo scored twice on the power play in Washington on Thursday."

3. **"Both numbers also depend on how many penalties get called, which we can't yet split out. Staying out of the penalty box matters
   more against Florida than against almost anyone."** The conclusion happens to be true, but nothing in the generator supports it, and
   the sentence before it says the data can't. It can: power-play time comes from situationCode (this is not the unverified penalty
   attribution). Florida has the most power-play time (6.66 minutes a game, 1st; league 5.41) and, per minute, the 2nd-most chances
   (9.44 goals' worth per 60 power-play minutes; Dallas 9.67; league 7.31). Buffalo's kill is also bad per minute (9.11 per 60, 4th-most;
   its shorthanded time is 17th), so "leaky" holds up.
   Fix (writer computes these in the generator): "Part of that is how often Florida goes on the power play: it has had more power-play
   time than any team. But minute for minute, its power play still creates the 2nd-most chances in the league. Staying out of the penalty
   box matters more against Florida than against almost anyone."
   No-new-numbers fallback: "Both numbers also depend on how many penalties get called. Staying out of the penalty box matters on Saturday."

4. **Chances chart overlaps** (`sabres-fla-chances.png`): the bold "Panthers" label is drawn over a grey team dot (about 3.23, 2.73), and
   the "Create little, allow a lot" note sits on the dot at about (2.42, 3.58). Move the Panthers label so it clears the dot, give the
   corner notes clear space (pad the axes limits), and reopen the PNG.

5. Minor, traceability: "five-game skid" is a literal. It's correct (VGK L, TBL L, CHI OTL, DAL L, PHI L, then the 6-3 win at WSH;
   the recap says the same), but add an assert.

No betting language (searched odds, spread, favorite, underdog, long shot, lean, cover, line, lock, pick, bet). No jargon in the body;
xG, Brier and Poisson appear only in "For the stat-heads". Small samples labeled (first meeting, early-season ranks). Backtest uses only
games before each date; the 2025-26 shot-model overlap is disclosed.

## Verified (my numbers)

- Data: 358 regular-season games through Nov. 19, the same in games, schedule and shots; none on Nov. 20; 14 on Nov. 21. Shootout attempts are not in shots (periods 1-4 only).
  Rescale factors: 2023-24 1.0227, 2024-25 1.0104, 2025-26 0.9713, 2026-27 0.9894 (story 0.989).
- Records: BUF 9-9-4, 22 points, 22 GP; FLA 12-8-3, 27 points, 23 GP. Goals per game BUF 2.91 / 3.50, FLA 3.13 / 2.96.
- Table: created BUF 2.967 (17th), FLA 3.117 (8th), league 2.958; allowed BUF 3.247 (27th; 6th-most), FLA 2.767 (11th), league 2.956;
  five-on-five share BUF 49.8% (19th), FLA 51.0% (15th); PP created BUF 0.663 (18th), FLA 1.048 (1st; CAR 0.867 next), league 0.657;
  a man down BUF 0.810 (29th = 4th-most), FLA 0.826 (30th = 3rd-most), league 0.659. Top PK-allowed: SJS 0.930, VAN 0.900, FLA, BUF.
- PP goals (5v4, 5v3, 4v3): FLA 22 in 23; BUF allowed 22 in 22 (GM story said 21 through Nov. 17; WSH scored one PP goal Thursday).
- Chart titles/labels: 11th-fewest / 6th-most; 1.05 (most of 32), 0.81 (4th-most of 32), league 0.66 / 0.66; footers 22 and 23 games.
- Oct. 12: BUF 5, FLA 3 at Buffalo, regulation; chances 3.397 vs 3.523; PP goals 2 each (BUF 1st and 3rd periods, FLA twice in the 2nd).
- 2025-26: BUF won 3 of 4 (3-0 W, 3-4 L, 5-3 W at FLA, 3-2 W at FLA).
- Reinhart 12 goals (9 not into an empty net), 11.25 in chances, most on FLA (B. Tkachuk 10.01 next). B. Tkachuk 11; roster team 9 (OTT) in 2023-24 to 2025-26 (60 games last season), 13 (FLA) now.
- Thompson 14, 6th in the NHL, not tied (Gauthier 21, Draisaitl 21, Kaprizov 18, Connor 18, Lehkonen 15).
- Schedule: FLA last played Tue Nov. 17 (vs EDM), 3 days off; BUF Thu Nov. 19 at WSH, 1 day off; at TBL Sun Nov. 22; start 23:00 UTC = 6 p.m. ET.
  Trip: CHI, DAL, PHI, WSH, FLA, TBL; Florida is game 5 of 6.
- Goalies (77 with shots faced): Luukkonen 13 GP, 87.3%, -2.59 (52nd); Ellis 8, 87.3%, -0.57 (40th); Lyon 3, 89.8%, -0.42 (39th);
  Markstrom 12, 89.8%, +0.71 (30th); Schmid 11, 88.5%, -0.09 (35th); Black 1, 85.7%, -0.98 (44th).
- Explainer: 336,462 unblocked non-empty-net shots in 2023-24 to 2025-26; within 10 ft 13.75%; 60+ ft 0.81%.
- Model (own re-implementation): coef -0.2537, 1.0316, 0.2721; home OT/SO 0.5451. Ratings before Nov. 20: BUF attack 2.996, FLA allowed 2.834,
  FLA attack 3.112, BUF allowed 3.193 (unrescaled; ratio 1.048). Expected goals BUF 2.819, FLA 3.605; P(BUF) 0.3735; tie after 60 0.1538.
- Backtest 2025-26: 1,312 games, right 54.65%, home won 52.21%, model's mean home chance 54.92%, Brier 0.2446 (home rate 0.2504).
  2026-27: 358 games, right 59.8%, home won 52.23%, mean home chance 54.38%, Brier 0.2358.
- Calibration chart: 50-55% said 52.5 / won 48.7 (528); 55-60% 57.4 / 54.0 (426); 60-65% 62.1 / 61.9 (231); 65%+ 68.0 / 68.5 (127).
  FLA's 62.65% falls in 60-65%.
- Ledger logger: same model, version and ratings date; logs round(0.3735, 2) = 0.37, matching the story; puck drop 23:00 UTC.
