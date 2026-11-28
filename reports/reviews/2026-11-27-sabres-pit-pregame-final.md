# Final check, round 3: 2026-11-27-sabres-pit-pregame (commit 3f00953c)

**Verdict: PASS.**

- **Story diff:** from b88bf96c to 3f00953c the story changes in one line only, the Ledger status. It now reads: "**Logged on the [Ledger](../ledger.html) at 2026-11-28 00:32:32 UTC, before puck drop.** It gets graded after the game, hit or miss." The generator, hero and PNG are unchanged.
- **Ledger row P0026:** matches the logger.
  - Created 2026-11-28T00:32:32Z, before the 01:00Z puck drop.
  - Game id NHL_20262027_2026-11-27_PIT_at_BUF; this is the only row for that game.
  - Claim "Sabres beat the Penguins (any result: regulation, OT or shootout)", metric BUF_win, probability 0.51, resolves 2026-11-28T01:00:00Z, model nhl-game-v0.1.
  - The notes (BUF 3.35, PIT 3.34, tie 0.157) match my independent recompute (3.346, 3.338, 0.157).
- **Reproduction:** in a clean clone of 3f00953c with the data linked in, `PYTHONPATH=. python3 -m src.reports.sabres_pregame_pit_nov27` finished without errors. The outputs are byte-identical to the committed files (SHA-256):
  - md: 7d34e541dea4f3c0f85b2147d09cedb906871ec045f69da318ad8a787b4f8044 (identical)
  - PNG: 131248f1b9684de052d88d633e4036f9bb49b771e10d38c83d15ef29b916472d (identical; matches the frozen manifest)
  - hero: dde59ecf20b4280d9769ab6d90f3f69ee45cbb980d523f6d7f3e3c4f6e33591f (identical)
- The clone's working tree was clean afterwards, apart from the untracked data symlink.
