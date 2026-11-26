# Quant review, round 3: Sabres 5, Rangers 1 (2026-11-25-sabres-nyr-postgame)

Reviewer: independent Quant (stage 2), commit 5408f9d9. Story sha 10dad776. Earlier rounds: -quant-r1.md, -quant-r2.md.

## Verdict: pass

Round 3 makes two changes to the story and the generator, both text only:
1. The round-2 must-fix: "Not counting empty-net or shootout goals, they've been outscored 75-82, almost exactly what their chances
   say (74.5 to 81.0)." Now correct. Not counting empty-net or shootout goals, Buffalo has scored 75 (78 minus 3 empty-net goals) and
   allowed 82 (84 minus 1 empty-net goal and 1 shootout goal). Chances 74.535 and 80.985. This matches the table footnote.
2. "2,367" and "2,370": the formatting changed (`{raw_lg:,.0f}`, `{lg_goals:,}`), not the values. The raw sum is 2366.73 and there are 2370 goals,
   both re-derived.

No other line in the story, hero JSON, chart or site dek changed. Every number verified in rounds 1 and 2 still stands.
The worktree matches HEAD for reports/ and src/.
