# Final check (stage 4): 2026-wk12-kc-leonhard — PASS

This checks the current text after round 4 (Charlie's rework around Rousseau and pressure) and the round-4 fixes.

## Fixes applied in round 4
- The 2025 fade now covers pressure as well (28th / 27th over the last eight games; 14th per dropback for the season).
- Pressure ranks are marked "tied for 3rd".
- Pressures are given per 100 dropbacks.
- The first-nine-games basis is used for 2025 extra rushers (24%, 22nd).
- Crosby's extra game is noted.
- "Through Week 10" is added to the lead.
- Polish: the lead lines and the Denver pressure bridge.

## Verified on the final text
- Every number matches my independent queries. Details are in quant reports r1-r5.
- Ranks are checked for ties, and the one tie is labelled.
- The windows line up: Buffalo played 9 games in Weeks 1-10 in both seasons. NFL and Denver are full 2025, as labelled.
- The generator reproduces the md, hero JSON and PNG byte-identically (PNG sha256 7adfab3f...18a45bca).
- No betting language. Stat terms appear only in "For the stat-heads". Small samples are labelled.
- No causal claims from timing or from one game.
- Leonhard's titles are verified (buffalobills.com, NFL.com, SI).

## Before publishing
- Freeze the current PNG with `scripts/freeze_images.py`. The image is new, and its old manifest entry was removed.
- If PFR loads Week 11 before publishing, re-check "leads the NFL" in the headline. The story is pinned to Weeks 1-10, and the lead says so.
