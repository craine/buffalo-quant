# Quant review: 2026-11-22-sabres-tbl-pregame (stage 2)

Text: md sha256 071b9200..., hero, card `sabres-lightning-pregame-nov-22`, sabres-tbl-keys.png, sabres-tbl-rest.png, sabres-tbl-model-test.png,
src/ledger/log_sabres_tbl.py (read, not run). Independent queries (scripts in /tmp/qa); generator reproduces all five outputs byte-identically in a clean copy.

**Verdict: don't publish until fixed (recorded as fail).** The stats are right, but the Ledger line is false and this branch overwrites files belonging to
the published Nov. 11 Tampa Bay preview.

## Issues, ranked
1. **False Ledger line.** "**Logged on the [Ledger](../ledger.html) at 2026-11-11 22:14:46 UTC, before puck drop.** It gets graded after the game, hit or miss."
   The generator filters the Ledger on `claim_text` containing "Lightning", which matches P0009 (the Nov. 11 game, 47%). Today's call isn't logged.
   Fix: filter on `game_id == "NHL_20262027_2026-11-22_BUF_at_TBL"`; until logged the line must read "**This is our model's number.** It counts once it's
   logged on the [Ledger](../ledger.html) before puck drop; every logged call is graded after the game, hit or miss." Re-check after logging.
2. **Published Nov. 11 story's files overwritten.** Modified tracked files: `src/reports/sabres_pregame_tbl.py` (the Nov. 11 generator, now rewritten),
   `src/ledger/log_sabres_tbl.py` (the P0009 logger), and `reports/sabres-tbl-model-test.png`, which `reports/2026-11-11-sabres-tbl-pregame.md` embeds.
   The published Nov. 11 story would show a new chart and could no longer be reproduced. Fix: restore all three from HEAD; put this story in new files
   (e.g. `src/reports/sabres_pregame_tbl_nov22.py`, `src/ledger/log_sabres_tbl_nov22.py`, `sabres-tbl-nov22-*.png`, and update the md links and card image).
3. **Keys chart subtitle says "through Nov. 19, 2026 (8,616 team-games)".** 8,616 is through Nov. 21 (4,308 games). Hard-coded. Fix: "through Nov. 21, 2026", from AS_OF.
4. **"Buffalo has played the second night of a back-to-back twice this season and lost both."** True, but both were extra-time losses (Oct. 13 at MTL, shootout;
   Nov. 12 at CHI, overtime), and "lost both" is hard-coded. Fix (computed): "...twice this season and lost both, once in overtime and once in a shootout."

Polish: the logger docstring says "ratings from games through Nov 19"; its code uses games before Nov. 22 (through Nov. 21), like the story. Fix the docstring.
Optional, stronger support for the rest claim (writer computes): in 2025-26 the model gave road teams on a back-to-back against a rested home team 45.6% on
average and they won 38.3% (193 games); this season 46.3% vs 38.9% (54). Rested road teams: 45.0% vs 50.2% (938). So "may be a little high" is if anything
understated, and the gap holds after accounting for team strength.

## Verified (my numbers)
- Data: 4,308 games through Nov. 21 (all 14 Nov. 21 games, OFF); 372 this season; 2026-27 factor 1.0014.
- Records: BUF 9-10-4 (22), TBL 15-5-2 (32); TBL at home 10-1-0. TBL last played Thu Nov. 19 (2 days off); BUF played Nov. 21; game Nov. 22 22:00 UTC = 5 p.m. ET;
  last of the 6-game trip (CHI, DAL, PHI, WSH, FLA, TBL).
- Rest (team's previous game in the same season; first games excluded, 128 team-games; no season crossings): road 0 vs home 1+ 38.58% (648);
  both 1+ 47.03% (3,162). By season 41.0, 36.7, 38.3, 38.9%. Counting first games as rested: 38.9% (656) / 47.2% (3,232). Buffalo second nights: 2, 0 wins.
- Keys (8,616): PPGA 0 59.22% (4,620), 2+ 25.50% (1,000, prints 26%), scored first 66.44%, 5v5 more 59.66%. TBL scored first 13, won 12; BUF 13, won 5.
  BUF 5v5 more 13 games, 6 W; fewer 10, 3 W.
- 5v5 share TBL 56.38% (3rd), BUF 49.99% (19th). TBL PP 0.676 (15th; league 0.663). BUF PK 0.810 (4th-most), 22 PP goals allowed in 23 games.
- Nov. 11: TBL 8-3 at Buffalo; chances BUF 3.560, TBL 3.592. 2025-26: Buffalo won 3 of 4 (OT L, W, W, W).
- Hagel 13 and Guentzel 13; Hagel's chances 11.14, most on TBL (Guentzel 9.15). Thompson 15, tied for 5th (with Lehkonen).
- Goalies (77): Luukkonen 13 GP 87.3% -2.10 (50th); Ellis 8 87.3% -0.30 (36th); Lyon 4 89.0% -1.54 (45th); Vasilevskiy 17 89.5% +2.85 (19th); Hildeby 5 89.9% +0.80 (28th).
- Explainer 13.8% / 0.8% (336,462 shots).
- Model (own re-implementation): ratings BUF 2.994 / 3.179, TBL 3.215 / 2.796; expected goals 2.81 vs 3.74; P(BUF) 0.3535; tie 0.150. Backtest 2025-26 unchanged
  (55% / 52%, buckets 528/426/231/127, 60-65% won 62%); 2026-27 372 games, right 59.7%, home won 52.69%, mean home chance 54.43%, Brier 0.2361.
- Logger: same model and ratings date, logs round(0.3535, 2) = 0.35, matches the story; puck drop 22:00 UTC.
- No betting language; jargon only in "For the stat-heads".
