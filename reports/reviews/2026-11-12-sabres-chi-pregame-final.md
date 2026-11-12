# Stage 4 final check (re-check): 2026-11-12-sabres-chi-pregame

**Verdict: PASS.** Text sha256 c041cff8fbe2131e40654247e765f0cdea962c7a42186e895c803b28a336205c. Generator and Ledger logger not run.

## What changed since the 7ada2eec pass (git diff HEAD~1; HEAD~1 story hash confirmed = 7ada2eec...)
- Story: exactly 4 edits. Three "points" -> "percentage points" (8.5 pooled gap; "8 percentage points short"; closing line "about 8 percentage points short"); the sentence "Over 242 games, a gap that size is too big to write off as a few bad bounces." removed. Numbers unchanged (8.5, 8, 4, 12 all still match my re-derivation: gap 0.0850; -8.2; +4.0; swing 12.2).
- Generator: the same text edits as f-strings, plus the b2b chart's source line set to "Source: NHL final scores and schedule (league game feed)." and then reset to the shared SRC (other charts keep the xG credit, correctly).
- b2b chart: looked at it. Only the footer changed; it now credits final scores and schedule, which is accurate for win rates. All bars, labels and sample sizes are unchanged (46/41, 44/37, 50/38, 44/35; 643 and 3,099).
- Unchanged vs HEAD~1: hero JSON, build.py dek, ledger/, the chances and model-test charts. P0010 (0.57, 22:57:33Z) still matches.

## Nothing broke
- Removing the "bad bounces" sentence leaves no orphaned reference. The 242-game claim is now descriptive. The significance claim rests on the pooled 643-game gap ("far too big to be luck", 4.0 SE in the stat-heads section), which is the claim stage 2 asked for.
- No betting language or new jargon introduced.

## Nit (non-blocking)
- "4 points better" and "about 12 points" still say "points" while the nearby figures now say "percentage points". In context it's clear, but for consistency they could say "percentage points" too.
- The 49-game 2026-27 bar on the chart still isn't labeled small (the body labels it).
