# Quant review (stage 2): reports/2026-11-20-sabres-wsh.md

**Verdict: publish with fixes** (two must-fix wording/accuracy items, no wrong numbers).

All numbers re-derived with my own queries on `raw_nhl_games`, `raw_nhl_plays`, `raw_nhl_rosters`, `raw_nhl_schedule`
and the per-shot model values in `clean_nhl_shots_xg` (my own per-season rescale and aggregation; scratch scripts in /tmp/qa,
not the generator's functions). Games through 2026-11-19; the three pinned late games (COL-ANA, SEA-VAN, VGK-DAL, start
02:00-03:00 UTC) are not in `raw_nhl_games` at all, so the pin is a no-op today but documented.

## Issues, ranked

1. **Lede replay omits ties (must fix).** Text: "Play this game over and over with those chances, and Buffalo wins about 14% of the time."
   Evidence: exact replay BUF win 0.137, tie after regulation 0.132, loss 0.731 (Monte Carlo 200k: 0.138 / 0.132). The 14% is
   regulation wins only; ties go to overtime, where Buffalo could still win, so its real "win" share is higher than 14%. The PHI
   recap stated all three. Fix: "Play this game over and over with those chances, and Buffalo wins it in regulation only about 14%
   of the time (it's tied after three periods another 13%)." Needs no new number (tie 0.132 is already computed as `p_tie`).
2. **Benson's goal count misleads (must fix).** Text: "He now has 2 on chances worth 7.9 this season." Evidence: Benson has
   3 goals (Oct. 27 empty-netter at 59:05 of BUF game 2026020198, Oct. 29 with a goalie in net, tonight; NHL
   `details_scoringPlayerTotal` = 3 tonight). A fan who sees "3 goals" on NHL.com reads "2" as wrong. Also, "his first goal with a goalie
   in net since Oct. 29" is true but the qualifier is unneeded: his last goal of any kind was Oct. 29. Fix: "Zach Benson scored at
   four-on-four in the first, his first goal since Oct. 29. Two of his 3 goals this season came with a goalie in net, on chances worth 7.9."
   The "3" is a new number: compute it in the generator (all non-shootout goals by shooter 8484145, season 20262027).
3. **GM story misquoted.** Text: "What it said to fix was the chances, and those weren't better tonight." Evidence: the GM story
   (2026-11-18-sabres-then-now.md) says "fix the penalty kill first, keep the five-on-five lineup, be patient with the shooters."
   It did not say fix the chances in general. Fix: "What it said to fix first was the penalty kill, and Washington's power play got
   9 shots worth 1.2 goals tonight." (both numbers already in the story).
4. **"the first 5 shots that reached him."** Logan Thompson faced only 5 shots on goal (5:25 G, 6:06, 6:10, 9:46 G, 10:11 G;
   Lindgren's first shot at 11:23 game time). "First 5" implies more. Fix: "Logan Thompson allowed 3 goals on the 5 shots he faced."
5. **"Washington had 66% of them."** 66% is share of chance value (3.70 / 5.57 = 0.664), not of shots (53 of 76 = 70%). Fans read
   "66% of the chances" as a count. Fix: "Washington's chances were worth about twice Buffalo's." (3.70 / 1.87 = 1.98, OK.)
6. **Thompson "6th in the NHL" is as of our feed.** 14 goals, alone in 6th (Draisaitl 21, Gauthier 21, Kaprizov 18, Connor 18,
   Lehkonen 15). Not tied. The three late Nov. 19 games aren't in the data; Sennecke (ANA, 12) would tie him only with 2 goals tonight.
   Low risk, no fix required.
7. **Code nits (no effect on output).** `assert en_goals == 1 and en[en.team == THEM].empty or True` always passes (precedence).
   `{tt_g}th` / `{tuch_g}th` hard-code the suffix (fine for 13 and 14; use `ordn`).

## "Was it luck? Mostly, yes": fair

Goals minus chances +3.13 (5 non-empty-net goals on 1.87), 2nd of 22 Buffalo games (best: 7 on 3.39, +3.61, game 2026020211).
Regulation-win replay 14%. Washington's starter was 2.33 goals worse than average on 5 shots. The framing is supported, and "that's
not a knock" plus the GM-story context keeps it from sounding dismissive. Keep it.

## Verified (my numbers)

- Final 6-3 BUF, REG, game 2026020351, BUF away. 9 goals from raw plays: Quinn 5:25 snap 26.4 ft 16.2%; Dahlin 9:46 wrap-around 4.5 ft
  5v4 7.4%; Malenstyn 10:11 backhand 10.4 ft 14.7%; Tuch 10:54 snap 31.8 ft 7.6%; Benson 15:55 poke 8.0 ft 4v4 (code 1441) 11.6%;
  T. Thompson P2 19:51 snap 29.4 ft 5v4 12.8%; Leonard P3 8:52 snap 25.0 ft WSH 5v4 (1451) 18.3%; Jenner 9:44 poke 1.4 ft 54.2%;
  Quinn 19:17 empty net (code 1560). Distances recomputed from x/y and `homeTeamDefendingSide`. Running scores match raw.
- Rescale 2026-27 factor 0.9915. BUF 1.872 on 23 unblocked (17 on goal); WSH 3.696 on 53 (37 on goal). Raw counts agree
  (BUF 12 SOG + 6 G + 8 missed minus 3 EN = 23; WSH 34 + 3 + 16 = 53).
- Periods: BUF 0.892 (11), 0.574 (6), 0.406 (6), goals 4/1/0; WSH 0.760 (16), 0.756 (12), 2.180 (25), goals 1/0/2.
- WSH share 66.4%. Replay win 0.137 / tie 0.132 / loss 0.731.
- Goalie change: L. Thompson last shot faced = Buffalo's 3rd goal at 10:11; 3 GA on 5 SOG, -2.33. Lindgren 2 GA on 12 SOG, -0.79.
- Luukkonen: faced 3.70, allowed 3, +0.70; season -2.42 in 13 games.
- Skid: 5 straight losses (VGK 1-4, TBL 3-8, CHI 2-3 OT, DAL 0-2, PHI 3-4), after a 5-2 win over CBJ; 9 goals on 14.35.
- Benson: 2 non-empty-net goals on 7.90 (3 goals total). Previous with goalie in net Oct. 29.
- Tuch 13th (raw count and `scoringPlayerTotal`). Thompson 14, 6th, not tied.
- WSH PP tonight 9 shots, 1.185 (all 5v4; 6v5 extra-attacker shots excluded); before tonight 0.516 a game over 19 games, which
  matches the preview's 0.52. 1.185 / 0.516 = 2.3, so "more than twice" holds. BUF PP 7 shots, 0.603, 2 goals.
- Ledger P0019: created 2026-11-18T18:13Z, before the 2026-11-20T00:00Z start; p 0.42, outcome 1, Brier (0.58)^2 = 0.3364.
  18 graded of 19 (P0017 season call is open): 11 right; NHL 4 of 6. Same "right" convention as earlier recaps.
- Record 9-9-4. Next: at FLA Sat Nov. 21, at TBL Sun Nov. 22, home NYR Wed Nov. 25 (Nov. 19, 2026 is a Thursday).
- Hero JSON (1.9 / 3.7, goals 5 vs 1.9) and site dek ("twice the chances": 1.98x) match.
- No betting language (grep for odds, spread, line, pick, lock, favorite, underdog, bet, wager, over/under, cover: none in that sense).
- Both charts viewed: titles, labels and footers correct; skid bars are games 17-21 and Thursday is game 22.
- Reproducibility: clean copy (repo without site/ and .git, same DB) re-ran `python -m src.reports.sabres_postgame_wsh`; the markdown,
  hero JSON and both PNGs are byte-identical to the committed files. Not tested against a freshly ingested DB.
