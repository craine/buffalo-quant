# Quant review, round 5: reports/2026-11-20-sabres-wsh.md (SHA-256 b35127ce...5b28)

**Verdict: pass.** All three round-4 overclaims are fixed. No number changed, and every changed sentence matches my numbers from round 4 (scratch in /tmp/qa).

- Lede, "After a cold-shooting skid": the skid as a whole was cold, 9 goals on chances worth 14.35. It no longer claims each game was cold.
- Finishing chart title, "Nov. 19 was the Sabres' second-best shooting night of the season": rank 2 of 22 at +3.13. The bar label "Nov. 19 at WSH" is on game 22.
- GM paragraph: "tends to even out. For one night, at least, the puck went in." makes no claim that it evened out. "the first thing to fix was the penalty kill" matches the GM story ("fix the penalty kill first").
- Benson, "Not counting an empty-netter, he has 2 goals this season on shots worth about 7.9 goals": 2 goals with a goalie in net on 83 unblocked shots worth 7.90.
- "former Sabre Alex Tuch scored for Washington": rosters show BUF 2023-24 to 2025-26 and WSH 2026-27, and the goal is credited to team 15.
- Model description, "and things like rebounds and power plays": the model's features include rebound and skaters for and against.
- Third period: 2.18 vs. 0.41. "five losses before Thursday": 9 on 14.35. "On Thursday it scored 5 on 1.9, about 3 more": +3.13.
- Card dek, "Washington's chances were worth twice Buffalo's": 3.70 / 1.87 = 1.98. The hero JSON is unchanged and correct.
- No betting language. No stat terms above "For the stat-heads" (the stat-heads section still says "tonight"; fine there).
- Generator diff: only text changed and the chart title and label. The calculations are untouched.
