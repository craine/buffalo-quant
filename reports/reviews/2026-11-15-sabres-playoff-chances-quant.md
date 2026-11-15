# Quant re-check 2 and final check (stage 4): 2026-11-15-sabres-playoff-chances, commit 85ae5817

## Verdict: PASS (quant and final)

**What changed since the last re-check (d0294b46):** only two chart strings in `src/reports/sabres_playoff_chances.py`, plus the
regenerated `sabres-playoffs-points.png` and `sabres-playoffs-whatif.png`. The story md is byte-identical. Its SHA-256 is
ba87b22cca22a0a798852c16419aec26c5592066f9206bd4412fecb2d60a6bd9, the same text I re-checked and the Editor passed. The hero, the
dek and the carry chart are unchanged.

**Both PNGs opened:**
- **Points chart:** the subtitle now ends "...usually lands." and fits. The title, the "about 94" annotation, the 90–97 shaded band
  and the footer (source, 64 Sabres games, 1,019 in all, 84-game season) are all intact. Nothing is clipped.
- **What-if chart:**
  - The title "Average defense or more offense about doubles the playoff chance" and the subtitle fit.
  - The claim holds. All scoring chances allowed cut to league average gives 32%, and 0.2 more created gives 31%, both from 16%.
    The subtitle names the Sabres, so the chart reads on its own.
  - The bars and labels (16/22/32/31/52%) are unchanged and match the story table. The footer is intact.

Every number and claim in the story was verified in the earlier re-check
(`2026-11-15-sabres-playoff-chances-quant-recheck.md`). Nothing in this change touches them.
