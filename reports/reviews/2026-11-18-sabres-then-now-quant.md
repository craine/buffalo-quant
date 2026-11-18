# Quant review (stage 2, round 5): 2026-11-18-sabres-then-now

Reviewed text SHA-256 `0d56c8aec389af90471a021557e950d5f7ac56e40e164620ffe705184b97dc2e` (re-checked after the editor's round-5 fixes; first reviewed at `c0dedb75…892a`) (generator `src/reports/sabres_then_now.py`, AS_OF 2026-11-17).
Scope: everything that changed since round 4 (`4ff3ec6a…fc3f`), diffed line by line. I verified every number in the earlier rounds with my own queries (scripts in /tmp/qa2) and none of those numbers changed.

## Verdict: pass

All three round-4 fixes are in, every number in the changed text checks out, and no new data claim overreaches. Since `c0dedb75` the editor made three changes: section 1 restores "A man down, it allows the 4th-most; more on that below." (BUF 0.794 a game, league 0.661, 4th-most ✓), the grammar slip is fixed ("but they're tied for 28th"), and "Small sample, too." is shortened. None of them changes a number.

## Round-4 findings: status

1. "The penalty kill alone…": **fixed.** It now reads "Cutting the chances allowed a man down to league average, on its own, moves it to 22%."
2. Power-play goals rank: **fixed.** The body says "is tied for 28th" and the stat-heads line says "T-28th". BUF and CHI are both at 0.476 a game.
3. Timing: **fixed.** "After 20 games last season…" and "…at the same point…" now match the playoff backtest cutoff of 2025-11-20, when Buffalo had played 20 games.

## Changed text checked

- What-if rows: "one more goal's worth of chances every 5 games" = 0.2 a game. That matches the playoff story ("0.2 more goals' worth… a game", "+0.2 xGF") and the generator asserts it. The percentages (16/22/32/31/52) are unchanged and still match the playoff story.
- Table intro: "using games through Nov. 14, before the Nov. 17 loss to Philadelphia" is right. PHI is Buffalo's only game since; it lost 4-3 in regulation.
- Lead plan and verdict ("don't sell"; "trade at the 40-game mark, for help a man down"; "help a man down first, then a proven finisher. Not a goalie."): these are first-person judgment calls, and the "— Charlie" line marks them as such. None is presented as a finding. The order fits the playoff story's carry-over numbers: shorthanded chances 0.46, finishing 0.05, goaltending 0.01. "Not a goalie" also fits goaltending's weak carry-over.
- Move 4: "Small sample, too: 10 goals" is right (10 power-play goals with a goalie in net, on chances worth 13.94; 17th in chances a game, tied 28th in goals).
- The GM intro absorbed "What it means" with no number changes. "Best goaltending-and-finishing stretch… barely ahead of Boston's" still holds (0.595 vs 0.582 a game).
- Section 3 is still supported without the cut sentence. Chances rose 14.0 → 16.7 while goals went 7 → 21, and "Last year's 7 was unusually low… about half" stays.
- Brand: no betting language. Stat terms still appear only under "For the stat-heads".
- Reproduction: I re-ran the generator in a fresh copy (/tmp/qa2/copy8, on the current text). The markdown, hero JSON and all three PNGs are byte-identical. The PNGs and hero JSON haven't changed since round 3.
