# Quant review: 2026-11-21-sabres-fla-pregame (stage 2, round 2)

Reviewed md sha256 712b924c..., hero JSON, site card, all three PNGs. Round-1 report: `2026-11-21-sabres-fla-pregame-quant-r1.md`
(all round-1 numbers verified there still apply; the diff against round 1 touches only the sentences below).

**Verdict: publish (pass).**

Round-1 issues:
1. "Florida spreads its scoring around": replaced with "Florida's top two..." in the suggested wording. Fixed.
2. Florida penalty-kill claim: dropped. The paragraph is now "Buffalo's own power play scored twice in Washington on Thursday."
   Generator computes `thu_ppg` from game 2026020351 (my check: 2026-11-19, WSH 3, BUF 6) and asserts 2; my count is 2 (Dahlin, Thompson, both 5-on-4). Fixed.
3. "Staying out of the penalty box matters on Saturday" with the unsupported "can't yet split out" and "than almost anyone" removed. Fixed.
4. Chances chart: Panthers label and corner notes no longer overlap any dot. Fixed.
5. Five-game skid now asserted (sk == 5); matches my L, L, OTL, L, L. Fixed.

Changed sentences checked against my numbers: home-ice OT share 55% (0.5451, fit on 2023-24 and 2024-25, home teams' OT/SO wins); caution
54.9% / 52.2% of 1,312 and 54.4% / 52.2% of 358 (mine 54.92 / 52.21 / 1,312; 54.38 / 52.23 / 358); attack 3.1 and allowed 3.2 (3.112, 3.193);
model-test title 60-65% / 62% (61.9%, 231 games); hero "1st" (FLA 1.048, next CAR 0.867); card dek 37% and 4th-most unchanged.
No betting language, no jargon in the body. Generator reproduces md, hero and all three PNGs byte-identically in a clean copy.

Polish (not blocking): "Sabres" label on the chances chart just touches the grey dot at about (3.00, 3.18).
