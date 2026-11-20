# Final check (stage 4), round 5: reports/2026-11-20-sabres-wsh.md

**Verdict: pass.** Story text SHA-256 b35127cec33dea32e65c79e893f1ff8245a28080f0441e85f1bdc35d33365b28.

I checked every sentence changed since round 4 against my independent numbers (queries on raw_nhl_* and clean_nhl_shots_xg with my own per-season rescale, factor 0.9915):
- "After a cold-shooting skid": skid 9 G on 14.35 xG. True of the five games taken together.
- "former Sabre Alex Tuch scored for Washington": rosters BUF 2023-24 to 2025-26, WSH 2026-27; goal by team 15.
- "...and things like rebounds and power plays": the nhl_xg.py features include rebound, skaters_for and skaters_against.
- "In the third period Washington took over: ... 2.2 goals to Buffalo's 0.4": 2.180 vs. 0.406.
- "In the five losses before Thursday ... 9 goals on chances worth about 14.3. On Thursday it scored 5 ... 1.9, about 3 more ... second-best ... in 22 games": 9 / 14.35; 5 / 1.87; +3.13; rank 2 of 22.
- GM paragraph: no evening-out claim. The GM story says "fix the penalty kill first".
- Benson: 2 non-empty-net goals on 83 shots worth 7.90. Last goal before Thursday was Oct. 29.
- "The power play wasn't quiet on Thursday: 9 power-play shots worth 1.2": 9 / 1.185.
- Finishing chart title "Nov. 19 was the Sabres' second-best shooting night of the season" and label "Nov. 19 at WSH": rank 2 of 22, game 22. Viewed: nothing overlaps or is cut off.
- Card dek "Washington's chances were worth twice Buffalo's": 1.98x. Hero JSON unchanged (1.9 / 3.7, 5 vs. 1.9, 4 in the first on 0.9).
- Unchanged numbers (score, goal table, replays 0.137 / 0.132, goalies, Tage Thompson 6th, Tuch 13th, Luukkonen +0.70 / -2.42 in 13, power play 0.52 coming in, Buffalo 2 on 0.60, record 9-9-4, schedule, Ledger 11 of 18 and 4 of 6, Brier 0.3364) are still correct.
- No betting language. No stat terms above "For the stat-heads".
- Reproduction: I copied the working tree (without .git, data or site), deleted the four outputs, and linked the same DB. Then I ran `python -m src.reports.sabres_postgame_wsh`. The md, hero JSON and both PNGs are byte-identical to the files in the repo, and the md SHA matches the one above. AS_OF 2026-11-19 with the Nov. 19 pins.
