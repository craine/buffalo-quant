# Quant re-check (stage 2), 2026-11-12-sabres-chi-pregame, text sha256 7ada2eec7116...

**Verdict: PASS.** All four required fixes are in, and each new number is computed in the generator (not hard-coded) and
matches my independent figures.

1. Rested road teams vs the model: the text now reads "4 points better than it said... the model is a little low on road teams in
   general, and the second night swings that by about 12 points." My figures: +3.96 and -8.23, swing 12.2. Fixed.
2. "Closer to a coin flip" is gone. It now reads "tired road teams have fallen about 8 points short of what the model said"
   (`short_t`, generator line 359). The logged number is still 57% only. Fixed.
3. "Not luck": now based on the pooled gap, "8.5 points over 643 games, far too big to be luck", with 2026-27's 49 games labeled
   small. The generator computes pool_gap/pool_se, and the stat-heads section shows the SE (mine: 0.085, SE 0.021, about 4.0). Fixed.
4. Oct. 13 now reads "a 4-3 shootout loss." Fixed.

Recommendations: taken were the hero title ("Second nights cost road teams."), the hero note definition ("against a rested home
team") and the empty-net qualifier on 336,462. Softened to "Both are small next to the drop in wins" (still not quantified;
acceptable). Not taken: the b2b chart footer still credits the expected-goals model as the source for a win-rate chart.
That's cosmetic and not blocking; fix it next time.

Process notes for Charlie:
- Ledger P0010 (0.57, nhl-game-v0.1, 22:57:33Z) was logged after this stage's first FAIL (22:56:19Z) and before this re-pass.
  The probability matches what I computed (0.5665), so the call itself is unaffected.
- The final check was recorded (22:59:39Z) before this quant re-pass. The process doc orders stage 2 before stage 4.
- Headline "Buffalo is on tired legs" is fine as a description (they played last night). The story body doesn't claim fatigue is
  the cause.
