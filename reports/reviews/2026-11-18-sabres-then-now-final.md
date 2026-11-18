# Final check (stage 4): 2026-11-18-sabres-then-now

Checked text SHA-256 `e048490095517e3ed22d0c5a0398023104df518020560ad4da9bf1950f888309` (generator `src/reports/sabres_then_now.py`, AS_OF 2026-11-17).
Scope: everything that changed since my round-3 Quant pass (SHA `6bd9fe65…ceae`), plus anything those changes touch. I compared the old and new text line by line.

## Verdict: pass

| Change | Check |
|---|---|
| §1: "A man down, it allows the 4th-most." | Opponent power-play chances allowed: BUF 0.794 a game, league 0.661, 4th-most of 32 ✓. Section 1's header ("the penalty kill is the worst of it") now has support in its own paragraph. |
| §2: Benson "80 shots at a goalie that weren't blocked, worth about 7.5 goals, and one goal to show for it. (His other goal was into an empty net.)" | 80 unblocked shots, none of them at an empty net, worth 7.55; 1 goal with a goalie in net. raw_nhl_plays shows 2 goals in all, 1 of them into an empty net ✓. |
| §3 header: "the jump from 7 to 21 is mostly how many went in" | Chances rose 14.0 → 16.7 (+2.7). The other ~11 of the +14 comes from goals compared with chances (−7.0 → +4.3) ✓. The "bounces" wording I flagged in round 3 is gone. |
| §3: "fewer shots, but better ones. The average power-play shot against has been about 30% more dangerous." | 0.0852 → 0.1111 a shot, ratio 1.30 ✓ (punctuation change only). |
| Finishing bullet: "about 13 more goals than its chances were worth over the last 61 games" | Goals minus chances over games 22-82 of 2025-26 = +13.04 ✓. Goaltending gives 23.25, so 13.04 + 23.25 = 36.3, which matches "about 36" ✓. |
| GM 1: "That's as much a coaching job as a roster one." | Opinion, offered as the GM view, and no number depends on it. Acceptable. |
| GM 3: "though not quite their usual form" removed | What remains, "almost exactly what their chances were worth" (1.006, n=11, labeled a small group), is still true ✓. |
| GM 4: "Over a few weeks, finishing swings a lot. Over three years, some of it holds." | Consistent with the cold-shooter result (1.006 afterwards), with hot starters' partial carry-over (1.12), and with 46 three-year finishers against a luck baseline of 32.7 ✓. |

- Reproduction: I re-ran the generator in a fresh copy (/tmp/qa2/copy5). The markdown, the hero JSON and all three PNGs are byte-identical to the committed files.
- The hero JSON and all three charts are unchanged from the versions I reviewed in round 3. The site card text ("sabres-same-start") is unchanged and still matches the story (8-9-4 twice, won 50, 21 vs 7).
- Brand: no betting language. Stat terms appear only in "For the stat-heads". The small sample is labeled.
