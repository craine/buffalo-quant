# Quant review, round 2: Sabres 5, Rangers 1 (2026-11-25-sabres-nyr-postgame)

Reviewer: independent Quant (stage 2), commit 77664ce9. Round 1: -quant-r1.md.

## Verdict: fail. One small must-fix.

All three round-1 must-fixes are fixed correctly. One new sentence miscounts by a goal.

### Must-fix: "Not counting empty nets, they've been outscored 75-82"

Text: "Not counting empty nets, they've been outscored 75-82, almost exactly what their chances say (74.5 to 81.0)."

The 82 also leaves out the shootout goal Buffalo allowed on Oct. 13 at Montreal. By the scoreboard, Buffalo has allowed 84 goals.
Take out 1 empty-net goal (Oct. 1 at Columbus) and that's 83, not 82. A fan who checks NHL.com gets 83.
Goals for: 78 scored minus 3 empty-net goals = 75. That's correct.

Replace with: "Not counting empty-net or shootout goals, they've been outscored 75-82, almost exactly what their chances say (74.5 to 81.0)."
This changes text only. The numbers stay the same, and they match the table's footnote.

## Round-1 fixes checked

1. Goalie rotation: "taking turns with Dylan Garand since early November." My own starter list (first NYR goalie to face a shot, from raw_nhl_plays)
   is Korpisalo Nov. 7, Garand Nov. 9, Korpisalo Nov. 11, Garand Nov. 13, Korpisalo Nov. 16, Garand Nov. 22, Korpisalo Nov. 25. The stat-heads
   list and the generator's check (strict alternation, two goalies, last start Korpisalo's, 6+ games) match it. Pass.
2. Receipts: the preview bullet now uses the agreed wording. It's fair: both calls are season-long, and the preview's "won't show up in one game" is reflected. The Ledger bullet
   is correct: 0.49, a miss, 0.26, 13 of 22. Pass.
3. "Cancelled out" is in the lead and the dek. "No more likely to last than the cold start was" fits the Tampa split-half finding. Pass.
4. "How we checked it": raw values 2366.73, rounded to "2367"; 2370 goals; scale 1.0014, shown as "1.001". All re-derived. The Tampa claim is
   supported (chance share r 0.77; finishing 0.10; saves 0.22). Pass.
5. Footnote "empty-net and shootout goals": correct (first 21 games: 74 on the scoreboard, minus 1 empty-net goal and 1 shootout goal = 72). Pass.
6. Goal difference 75-82 vs 74.5-81.0: the numbers are right (74.535, 80.985). Only the label is wrong (see must-fix).
7. New lead: 57 on 64 and 72 on 69 through 21 games; "both running totals are back near zero" (+0.47, -1.02); 2.5 to 2.3; 5-1. All correct.
8. Unchanged numbers from round 1 still re-derive: game, goalies, Korpisalo +2.79/-2.53, split table, ranks 22nd/15th/18th, NYR 30th. Pass.

## Reproduction
git archive of 77664ce9 into a clean directory, data symlinked, generator re-run: md, hero JSON and PNG are byte-identical to the committed files.

## Brand
No betting language. No stat jargon in the body. Typed literals are guarded by asserts ("Season (25 games)" is now a variable).
