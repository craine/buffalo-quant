# Final check: 2026-11-22-sabres-tbl-pregame (stage 4)

Text: md sha256 549a051f960ee4c5a578f98386bb5b269f7c1461b1886788db35bf9b59c9656d, hero, card, sabres-tbl-nov22-{keys,rest,model-test}.png.

**Passes.** Changed since round 1: md lines 1, 9, 41, 44, 72, 78, 80; card dek and image; chart file names and the keys/rest subtitle dates. Each checked
against my independent numbers (-quant-r1.md) and the Ledger (P0022, 0.35, 13:58:15Z, before 22:00Z). Nothing else changed; no new claims, betting words or
jargon. Clean-copy run of `src/reports/sabres_pregame_tbl_nov22.py` reproduces the md, hero and all three PNGs byte-identically. The restored Nov. 11
generator reproduces its md, hero and model-test PNG byte-identically.
