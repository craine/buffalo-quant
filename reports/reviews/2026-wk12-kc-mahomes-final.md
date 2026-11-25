# Final check (re-run): 2026-wk12-kc-mahomes (stage 4)

**Verdict: PASS.**

The story text changed since the last final check (commit 1bf10c2e against 88cde99d, the text I passed). There are two changes, and both are text only:
1. The series line now links "[Part 4: rain and wind](bills-chiefs-rain-and-wind.html)".
2. A new paragraph, "The weather could shift that. …", sits before "Watch two things early".
   - It has no numbers.
   - Its claims ("a few fewer long passes and ran more", "could help Buffalo a little against big plays", "more of the load on its run defense") stay within what part 4 computes.
   - "Rain the whole game, with wind" matches part 4's forecast (light rain all game, 10-13 mph).

## Checks
- **Reproduction:** a clean `git archive HEAD` (44569e55) re-runs to byte-identical md, hero JSON and PNG. The PNG hash 4264ae9b… matches `published_images.json`.
- **Cross-links:** both slugs exist in `ARTICLES` in `src/site/build.py`: bills-chiefs-rain-and-wind and bills-chiefs-slowing-mahomes. Every article is written to the same directory as `{slug}.html`, so the relative links resolve.
- **Numbers:** none changed. The data fingerprint holds.
