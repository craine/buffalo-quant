# Quant review: 2026-11-22-sabres-tbl-pregame (stage 2, round 2)

Text: md sha256 549a051f960ee4c5a578f98386bb5b269f7c1461b1886788db35bf9b59c9656d. Round 1: -quant-r1.md (all numbers there still apply).

**Verdict: publish (pass).**

Round-1 issues:
1. Ledger line: lookup is by game_id; P0022 in ledger/predictions.csv: created 2026-11-22T13:58:15Z, before the 22:00Z puck drop; 0.35 (my 0.3535);
   nhl-game-v0.1; notes give 2.81 / 3.74 and tie 0.150, matching mine. The story line reads "Logged ... at 2026-11-22 13:58:15 UTC". Fixed.
2. Overwrites: src/reports/sabres_pregame_tbl.py, src/ledger/log_sabres_tbl.py and reports/sabres-tbl-model-test.png are unmodified vs HEAD.
   This story now uses sabres_pregame_tbl_nov22.py, log_sabres_tbl_nov22.py and sabres-tbl-nov22-*.png; md links and card image updated; stray PNGs gone.
   Restored Nov. 11 generator, re-run in a clean copy: md, hero JSON and sabres-tbl-model-test.png reproduce byte-identically. Fixed.
3. Keys and rest chart subtitles now "through Nov. 21, 2026", from AS_OF. Fixed.
4. "lost both, once in overtime and once in a shootout": asserted in the generator (['OT', 'SO']); mine: Oct. 13 at MTL (SO), Nov. 12 at CHI (OT). Fixed.
5. "The back-to-back works against Buffalo, though." Fixed.

Clean-copy run of src/reports/sabres_pregame_tbl_nov22.py reproduces the md, hero and all three PNGs byte-identically.

## Pre-existing, outside this story (not blocking)
The Nov. 11 story's other two charts don't match their committed files: `sabres-tbl-rebounds.png` regenerates identical to the original Nov. 11 commit
(dcfb8440) but the committed copy was replaced in 0af34367 (the Nov. 14 Dallas preview); `sabres-tbl-chances.png` matches neither. The published Nov. 11
story's charts changed silently on Nov. 14. Worth a separate fix (restore the dcfb8440 versions after checking), not part of this branch.

Note: P0022 was logged before this round of reviews passed. Its number matches my independent recomputation, so no harm here, but logging normally waits
for the gate.
