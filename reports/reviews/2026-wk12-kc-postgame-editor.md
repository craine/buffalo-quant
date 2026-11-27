# Editor review, round 2: 2026-wk12-kc-postgame (stage 3)

**One sentence:** Josh Allen threw for just 81 yards, the fewest in any of his 105 career wins, and the Bills still beat Kansas City by running 40 times and kicking a 57-yarder with 4 seconds left.

**Verdict: ready.** Story sha256: bf4236b5214965fa0bee01944b9119696bcfc865b20831a8fc11f48ed1e48b99. Round 1 report: -editor-r1.md.

- Headline: trimmed, no longer redundant; still the shareable hook.
- "dropbacks" -> "pass plays" in the body (remains only in stat-heads, where it belongs).
- "runs worked, leaving it more likely to score": plain and correct for the measure; reads a little clunky with the commas but a fan
  follows it. Accepted the writer's deviation.
- Small-sample sentence added; accuracy-score line now explains itself; chart legend reads on its own (dated).
- Rejected phrases: none ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end"). No betting language.
- Links: part 3 and part 4 slugs exist in src/site/build.py. Hero JSON and site dek stand alone.
- No typed numbers: every new number (137, 19) is a template variable in the generator.

Optional polish, not required: "Kansas City's runs worked 63% of the time (19 runs), meaning they left it more likely to score".
