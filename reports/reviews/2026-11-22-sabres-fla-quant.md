# Quant review: 2026-11-22-sabres-fla (stage 2, round 2)

Text: md sha256 94eae3f8768fd6bd113042338f53ddcdc8facc0a11a48b1a79a03b4478eac9a1. Round 1: -quant-r1.md (all numbers verified there still apply).

**Verdict: publish (pass).**
- Line 73 now "They play again Sunday, ..., at Tampa Bay (5 p.m.)", computed from the schedule row (2026-11-22, 22:00 UTC = 5 p.m. ET). Correct.
  (The hour code subtracts 12 unconditionally; fine here, fragile for a noon or morning start. Not blocking.)
- Line 19 "didn't score first": now matches the preview's key exactly; 46% of 1,775 unchanged (45.58%).
- Line 20 "Teams in Buffalo's spot win a little less than half the time": consistent with 45.6%.
- Flow chart now ends at 60 minutes; nothing else in the chart changed. Hero and card unchanged.
Clean-copy run reproduces md, hero and PNG byte-identically.
