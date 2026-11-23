# Quant review: 2026-11-22-sabres-tbl-postgame (stage 2, round 1)

Reviewed: reports/2026-11-22-sabres-tbl-postgame.md (sha256 8609fa8f...22bb, same as self-check), hero JSON, flow PNG,
site card `sabres-lightning-postgame-nov-22`, generator `src/reports/sabres_postgame_tbl_nov22.py`, grader `src/ledger/grade_p0022.py`.
Independent scripts: own queries on raw_nhl_plays / raw_nhl_games / raw_nhl_schedule / raw_nhl_rosters, own per-season rescale of
clean_nhl_shots_xg, own key table built from raw goal events (situationCode by scorer's side).

**Verdict: don't publish yet (fail). Every number checks out; one claim is inconsistent and misleading.**

## Must fix

1. **Key 2 "Half" contradicts the league comparison under it, and the 60% isn't Buffalo's spot.**
   The table grades key 2 "Half" because Tampa Bay tied it. The next paragraph then counts key 2 as hit: "teams that allowed one
   power-play goal at most and scored first, but had fewer of the five-on-five chances, won 60% of the time (1,856 games). Teams that
   hit all three won 78%." "Hit all three" uses scored-first as key 2, so the story uses two definitions of key 2 three lines apart.
   Worse, the 1,856 includes 570 teams that never gave the lead back. Those teams win every time by construction (never tied after
   scoring first means you won). Teams in Buffalo's actual spot (one PPG allowed at most, scored first, opponent later tied or led,
   lost 5v5 chances) won **42.3% of 1,286**. So the story implies "teams like Buffalo usually win" when they usually lose.
   - Is "Half" fair? It matches the preview's wording ("the first goal, and no giving it back"); Buffalo gave it back. It does not
     match the preview's numbers (66% etc. measure the first goal only), and the Florida recap graded key 2 on the first goal alone.
     Either grade is defensible; mixing them isn't. Note "keep it" can't be measured as a predictive key: by itself it always means a win.
   - Fix (keeps "Half", which is closest to what the preview told readers):
     - Current: `Since 2023-24, teams that allowed one power-play goal at most and scored first, but had fewer of the five-on-five chances, won 60% of the time (1,856 games).`
       `Teams that hit all three won 78%. Buffalo scored first for the 14th time this season and has won 6 of those games.`
     - Replace: `Since 2023-24, teams in Buffalo's spot won 42% of the time (1,286 games). They allowed one power-play goal at most, scored first but saw the other team tie it, and had fewer of the five-on-five chances.`
       `Buffalo has scored first 14 times this season and won 6 of those games.`
     - Stat-heads, current: `- Key 2 is graded "Half": BUF scored first (the preview's first-goal numbers) but TBL tied it. Keys (definitions as in the preview): team-games 2023-24 through 2026-11-22, n = 8,624. PPGA <= 1 and first goal but 5v5 xG lost: win 0.600 (n 1,856);`
       `  all three keys: 0.781 (n 2,063).`
     - Replace: `- Key 2 is graded "Half": BUF scored first but TBL tied it. Keys (definitions as in the preview): team-games 2023-24 through 2026-11-22, n = 8,624. PPGA <= 1, first goal, opponent later tied or led, 5v5 xG lost: win 0.423 (n 1,286).`
       `  Without the tie condition: 0.600 (n 1,856), of which 570 never gave the lead back and all won.`
     - The generator must compute and assert the 1,286 / 0.423 / 570 (my independent figures; "gave it back" = after the first goal,
       the opponent's running total at any point equals or exceeds the first-scoring team's; shootout goals excluded).
   - Alternative if Charlie prefers the Florida precedent: grade key 2 **Yes** (first goal) and keep 60%/78%, with the row saying
     Tampa Bay tied it. Don't keep "Half" with the current paragraph.

## Verified (story value = my value)

- Final 6-2 TBL home, REG, OFF (raw_nhl_games). Back-to-back: BUF at FLA 2026-11-21.
- Goals from raw plays (period, clock, situationCode, scorer, distance computed from homeTeamDefendingSide): Kulich 1 3:35 5v5 41 ft;
  Kucherov 1 12:21 1451 = TBL 5v4, 28 ft; Quinn 2 1:22 29 ft; Thompson 2 11:05 1531 = BUF 5v3, 30 ft; Thompson 2 16:17 27 ft;
  Goncalves 3 5:50 46 ft; Ostlund 3 6:50 13 ft; Benson 3 18:53 1560 = TBL goalie out. Running scores match; Buffalo never trailed.
  Shot types wrist/snap/snap/slap/snap/slap/wrist match. Chance percentages 4/10/11/19/17/6/17 match.
- Chances (rescale 2026-27 factor 1.000115): BUF 3.050 on 37 (27 on goal), TBL 3.575 on 50 (31 on goal). By period BUF 0.62/1.72/0.71
  on 13/14/10; TBL 1.29/1.13/1.16 on 19/15/16. Raw event counts agree: TBL 29 SOG + 2 G + 19 missed = 50; BUF 22 + 6 + 10 = 38 incl. EN.
- 5v5: BUF 2.43, TBL 2.62. PP: BUF 0.60 (6), TBL 0.70 (7). TBL 6v5 0.26 (2). BUF 5v5 goals 4. PPG 1 each.
- Goalies: Luukkonen 31 on goal, 2 GA, 29 saves, xGA 3.575, +1.58; season -0.57, 14 GP, 38th of 77. Hildeby 3.05 xGA, 5 GA, -1.95.
- Replays (exact convolution, non-EN shots): win 0.332, tie 0.168, loss 0.501. Empty net handled correctly: Benson's EN shot is out
  of chances and replays, in the goal totals, and disclosed in the table note and chart footer. TBL's two goalie-pulled shots (0.26) are
  in; disclosed in stat-heads. Fine.
- Nov. 11 (2026020293): BUF 3, TBL 8; chances BUF 3.56, TBL 3.59. "Even" is fair, matches the preview.
- Tampa Bay home before tonight: 10-1-0 (91%); next best MIN 6-2, NYR/NJD 9-3. Best by win % and by points % (TBL .909, MIN .875).
  Also best through Nov. 21. Claim holds.
- Thompson: 17 goals by raw goal events (and details_scoringPlayerTotal = 17), 5th alone (Draisaitl 23, Gauthier 21, Connor 19,
  Kaprizov 18). Benson top shooter on either team, 0.69 (Thompson 0.56).
- Ostlund 13 ft is the closest goal (closest shot overall was Benson's 3 ft miss; the sentence says "goal", fine).
- Record 10-10-4, 24 points. Trip: CHI, DAL, PHI, WSH, FLA, TBL = 6 road games. Next: home vs NYR 2026-11-25 00:00 UTC = Wednesday 7 p.m. ET.
- BUF scored first 14 times this season, won 6 (raw goals). Preview said 13 and 5; consistent.
- Keys league set: writer's definitions reproduce 0.600 of 1,856 and 0.781 of 2,063 exactly. My raw-situationCode version gives
  1,857 / 2,064: the difference is goalie-pulled codes (e.g. 1450) that clean_nhl_shots_xg labels 5v4. Writer matches the preview's
  definition; percentages unchanged. Not an issue.
- Ledger: P0022 p 0.35, created 2026-11-22 13:58:15Z (puck drop 22:00Z), outcome 1, Brier 0.4225 (0.65^2). Graded 21 of 22
  (P0017 season call open); hits 13 of 21, NHL 5 of 8. Florida recap said 12 of 19, then P0021 hit, P0022 miss. Consistent.
  Grader reads final from raw_nhl_games; grades.csv row appended, no edits to earlier rows.
- Penalty counts: none published (7 penalties exist in raw; story gives only PP goals and PP shots). OK.
- Betting language: none. Jargon in body: none (xG, GSAx, Poisson only in stat-heads). Rejected phrasing: none of the listed.
- Pin: VAN-CHI 2026020377 is LIVE in raw_nhl_schedule and absent from raw_nhl_games; the pin keeps the story stable after it loads.
  It is the only Nov. 22 game not loaded.
- Reproducibility: clean copy (git archive HEAD + new generator, pins.py, grades.csv, same DB) reproduces md, hero JSON and PNG
  byte-identically.
- Hero (3.0 / 3.6; Luukkonen 2 vs 3.6) and card dek (6-2, back-to-back, 35% miss) match the body.

## Notes, not blocking

- `nxt_hr` subtracts 12 unconditionally (fine for 7 p.m.; wrong for a noon or morning start).
- `data` is a symlink, so `.gitignore`'s `data/` doesn't match it and `git status` lists `data` as untracked. Don't `git add -A`.
