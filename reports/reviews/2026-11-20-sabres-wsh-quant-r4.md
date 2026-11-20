# Quant review, round 4 (independent): reports/2026-11-20-sabres-wsh.md

**Verdict: fail (fixable in wording).** Every number checks out against my own queries. Three sentences claim more than the
numbers show, and the finishing chart's title has the same problem. No number needs to change.

Method: my own queries on `raw_nhl_games`, `raw_nhl_plays`, `raw_nhl_rosters`, `raw_nhl_schedule` and the per-shot model values in
`clean_nhl_shots_xg`. I did my own per-season rescale (league goals / league xG on unblocked, non-empty-net shots, games through
2026-11-19 with the pinned games dropped) and my own aggregation, not the generator's code. Scratch scripts are in /tmp/qa.

## Must fix

1. **"After five games of cold shooting" is false game by game.** Buffalo's goals minus chances in the skid games: VGK -2.88,
   TBL -0.53, CHI -0.11, DAL -2.63, **PHI +0.79**. Buffalo scored more than its chances in the last game of the skid (3 on 2.21).
   Taken together the skid was cold (9 goals on 14.35), but not each game. The finishing chart shows it: one red "skid" bar sits above zero.
   - Lede: "After five games of cold shooting, it was Buffalo's second-best shooting night of the season."
     -> "After a five-game skid with 9 goals on chances worth 14, it was Buffalo's second-best shooting night of the season."
     (or shorter: "After a cold-shooting skid, it was Buffalo's second-best shooting night of the season.")
   - Finishing chart title: "After a skid of cold shooting, the Sabres' second-best shooting night"
     -> "Thursday was the Sabres' second-best shooting night of the season"
2. **"and tonight it did" claims shooting has evened out. It hasn't.** Over the skid plus tonight, Buffalo has 14 goals on 16.22.
   This season it has 62 on 65.33. One hot night isn't cold shooting evening out.
   - "Our GM story said cold shooting tends to even out, and tonight it did."
     -> "Our GM story said cold shooting tends to even out. For one night, at least, the puck went in."
3. **Benson's 7.9 is pinned to the wrong thing.** "Two of his three goals this season came with a goalie in net, on chances worth 7.9."
   reads as if those two goals came on chances worth 7.9. In fact 7.90 is the value of all 83 of his unblocked, non-empty-net shots
   this season, and he scored on 2 of them.
   - -> "Not counting an empty-netter, he has 2 goals this season on shots worth about 7.9 goals."

## Optional

- "His 14 goals are 6th in the NHL." Correct in our feed (alone in 6th: Gauthier 21, Draisaitl 21, Connor 18, Kaprizov 18, Lehkonen 15).
  The three late Nov. 19 games aren't loaded. Low risk; could add "through Thursday's early games".
- "Every shot has a chance of going in, based on where it was taken and what kind of shot it was." The model also uses rebound, rush,
  time since the last shot and skaters on the ice (`FEATURES` in nhl_xg.py). Could read "...where it was taken, what kind of shot it
  was, and things like rebounds and power plays."
- Logan Thompson's pull time: there's no goalie-change event in the feed. Lindgren is in net for Buffalo's next attempt (11:23), so
  "after Buffalo's third goal" is right. Just don't add an exact pull time.

## Verified (my numbers)

- Final: BUF 6, WSH 3, REG, game 2026020351, BUF away (raw_nhl_games OFF). My nine goals from raw plays match the table on time, team,
  scorer, shot type, strength (situationCode 1541/1441/1451/1560), distance (from x/y and homeTeamDefendingSide), chance (16, 7, 15, 8,
  12, 13, 18, 54%) and running score. Quinn's 19:17 goal was into an empty net (code 1560, no goalie in net).
- Rescale 2026-27 factor 0.9915 (table: 0.992). BUF 1.872 on 23 unblocked (17 on goal), WSH 3.696 on 53 (37 on goal). Raw SOG events
  agree (BUF 12 SOG + 6 G minus the EN goal = 17; WSH 34 + 3 = 37). Periods: BUF 0.89/0.57/0.41 on 11/6/6, goals 4/1/0; WSH
  0.76/0.76/2.18 on 16/12/25, goals 1/0/2. Ratio 1.98 ("about twice"; card "twice the chances" OK).
- Replays (exact convolution): win 0.137, tie 0.132, loss 0.731. Monte Carlo 400k: 0.137 / 0.132.
- Goals minus chances tonight +3.13, rank 2 of 22 Buffalo games (best +3.61 at ANA Oct. 29). "About 3 more" OK.
- Skid: 5 straight losses (1-4, 3-8, 2-3 OT, 0-2, 3-4) after a win; 9 goals on 14.35 ("about 14.3" OK). It's 0-4-1, so "five-game
  losing streak" is fine as everyday usage.
- Logan Thompson: 5 shots on goal (2 saves + 3 goals; raw awaySOG counter = 2 saves at 11:01), 3 goals against, -2.33; last shot faced
  was the 10:11 goal; Lindgren in net at 11:23; Lindgren 2 goals on 12 shots, -0.79.
- Benson: 3 goals (Oct. 27 empty-netter, Oct. 29, tonight; scoringPlayerTotal 3); last goal before tonight Oct. 29; 2 non-EN goals on 83
  unblocked shots worth 7.90.
- Tage Thompson 14 goals, alone in 6th (raw goal events, shootouts excluded; scoringPlayerTotal 14).
- Tuch: 13th goal (scoringPlayerTotal 13), scored for WSH (team 15). Rosters: BUF in 2023-24 (75 games), 2024-25 (82), 2025-26 (79);
  WSH in 2026-27 (20). "Against his old team" is true.
- Luukkonen tonight: 3.70 faced, 3 allowed, +0.70. Season: -2.42 in 13 games (13 games with him in net in raw plays too).
- Power play: WSH 9 shots (5v4) worth 1.185, 1 goal; the 6v5 extra-attacker shots aren't counted, correctly. BUF 7 shots worth 0.603,
  2 goals. WSH coming in: 9.81 over 19 games = 0.516 a game.
- Record 9-9-4. Next: at FLA Sat Nov. 21, at TBL Sun Nov. 22, home vs. NYR Wed Nov. 25 (raw_nhl_schedule). Six-game trip: CHI,
  DAL, PHI, WSH, FLA, TBL.
- Ledger: P0019 logged 2026-11-18T18:13Z, before the 2026-11-20T00:00Z puck drop. p 0.42, outcome 1, Brier 0.58^2 = 0.3364
  (shown as 0.34). 18 graded (P0017, the season call, is still open): 11 right; NHL 4 of 6. Every grade's Brier matches (p - outcome)^2.
- Pins: the three late games (2026020356-58) are LIVE in raw_nhl_schedule and absent from raw_nhl_games. The pin is a no-op today, but
  it's correct and the stat-heads section discloses it. AS_OF = 2026-11-19.
- Hero JSON (1.9 / 3.7; note "4 in the first period on chances worth 0.9"; bars 5 vs 1.9) and site dek all match.
- No betting language (grepped spread, odds, favorite, underdog, long shot, lean, cover, line, pick, lock, bet, wager, unit). No stat
  terms above "For the stat-heads".
- Reproducibility: ran `python -m src.reports.sabres_postgame_wsh` in a clean `git archive HEAD` copy with the same DB. The md, hero JSON
  and both PNGs are byte-identical to the committed files.
