# Final check (stage 4): 2026-wk12-kc-leonhard — PASS

Checked the current text (after all round-1, round-2 and round-3 edits) against my own queries.

## Fixes applied (all rounds)
Quant r1: Week 11 paragraph rewritten (Denver man 56% wks 1-8, 35% wk 9+; no cause claim); blitz line removed and FTN note added; league
context for the rise in extra rushers (27% -> 31%, Buffalo's jump 2.26x); "pressure" -> "extra rushers"; Mahomes split labelled small with league
context (+0.06 / +0.01); hero note no longer claims cause.
Editor r1: headline; lead's last line; points per dropback glossed and explained plainly; stilted line; dropback defined up top.
Quant r2: closing line replaced with Buffalo's 5+ sack rate (6.8%, 25th, league 8.6%); FTN numbers computed in the generator.

## Re-verified on the final text
Every number in the body, stat-heads, hero, card and chart matches my independent queries (see quant reports r1-r3). Ranks have no ties.
Generator re-run in a clean copy reproduces md, hero JSON and PNG byte-identically (PNG sha256 710505058a3b...e8a2a0). Chart re-opened: labels,
footer source and sample sizes fine. Leonhard's titles match buffalobills.com, NFL.com and SI. No betting language; stat terms only in
"For the stat-heads"; small samples labelled; no causal claim from timing or one game.

Note for publishing: the PNG differs from the round-1 image; freeze the current one with `scripts/freeze_images.py`.
