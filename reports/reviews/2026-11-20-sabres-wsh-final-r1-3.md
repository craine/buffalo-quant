# Final check (stage 4): reports/2026-11-20-sabres-wsh.md

**Verdict: pass.** Story text SHA-256 71068ef962704546e6ac45c9c0c9f2878b0b0e44e47f37989030ae45eafa4143.

Changes since the stage-2 Quant review were all checked against my independent numbers (scratch queries in /tmp/qa):
- Replay: regulation win 14% and tie 13% (0.137 / 0.132). Correct.
- Benson: "first goal since Oct. 29. Two of his three goals… on chances worth 7.9" (3 goals; 2 with a goalie in net, on 7.90). Correct.
  The generator now asserts ben_all == 3.
- GM paragraph: the GM story's first fix is the penalty kill, and it says shooting evens out. "9 shots worth 1.2" (1.185) and
  "about twice Buffalo's" (3.70 / 1.87 = 1.98). Correct.
- "Logan Thompson gave up 3 goals on the 5 shots he faced… 10:11 in." Correct.
- "2nd-best shooting night in 22 games" (rank 2 of 22, +3.13). Correct.
- Penalty kill: "9 power-play shots worth 1.2 goals and scored once. Coming in, its power play averaged chances worth 0.52 goals a
  game" (0.516 over 19 games). Correct. The text no longer says "more than twice".
- "poked in" (shot type poke); "in goals" headers; receipts line ("less than an even chance… a miss", 42%, outcome 1). Correct.
- Flow chart title "Buffalo scored 5 (plus an empty-netter) on chances worth 1.9": correct, and it fits. Finishing chart unchanged.
- Hero JSON and site-card dek ("twice the chances", 1.98x; "made the most of what it got") are consistent.
- No betting language. No stat jargon in the body.
- Reproduction: a clean copy (repo without site/ and .git, same DB) re-ran src.reports.sabres_postgame_wsh. The md, hero JSON
  and both PNGs are byte-identical to the committed files.
