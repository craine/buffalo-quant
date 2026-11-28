# Quant review, round 2: 2026-11-27-sabres-pit-pregame (commit b88bf96c)

**Verdict: PASS.** Round 1 is in `-quant-r1.md`. All round-1 numbers were re-derived independently there and still stand.

Changes since 3a61acf6 (I diffed the md, the generator and the manifest; the hero and PNG are unchanged):
- The Lizotte line now reads "from 41 shots, a small sample." The 41 matches my independent count of his unblocked, non-empty-net PIT shots (41 shots in 20 games). `cold_n` is computed and asserted < 100, so the label can't go stale silently. The required fix is resolved.
- "So, mostly, does the goaltending." This matches the evidence: the mean fell from -14.0 to -1.8, and 16 of 24 teams were still below average. Advisory 1 is resolved.
- Stat-heads: "Novak and Rakell 0 of 18 combined". 9 + 9 = 18, with 0 empty-net goals. Correct.
- `published_images.json` now freezes `sabres-pit-nov27-chances.png` at 131248f1..., which matches the committed PNG.

Logger unchanged: 0.5082, logged as 0.51; game id NHL_20262027_2026-11-27_PIT_at_BUF; puck drop 2026-11-28T01:00Z. No betting language, no penalty counts, ties disclosed, small samples labelled.
Still advisory: the linked goalie cards differ slightly from the story's table (they refresh daily, by design).
