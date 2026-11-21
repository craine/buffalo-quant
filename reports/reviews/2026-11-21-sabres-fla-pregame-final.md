# Final check: 2026-11-21-sabres-fla-pregame (stage 4, after Ledger logging)

Text checked: md sha256 06bc4badd2385daec956a3c363282999df137eeed9368ded5e691d05496dffe0. Previous final (pass on 89a42f80...): -final-r4.md.

**Passes.**

- Exactly one line changed from the round-4 text (line 69, the Ledger status line), now:
  "**Logged on the [Ledger](../ledger.html) at 2026-11-21 00:08:18 UTC, before puck drop.** It gets graded after the game, hit or miss."
  The hero JSON and all three PNGs are byte-identical to round 4.
- ledger/predictions.csv P0020 matches: created 2026-11-21T00:08:18Z (before puck drop, 23:00Z); probability 0.37, the story's 37%;
  model nhl-game-v0.1; claim "Sabres beat the Panthers (any result: regulation, OT or shootout)"; notes give expected goals 2.82 / 3.61
  and tie 0.154, matching my independent 2.819 / 3.605 / 0.1538.
- Clean-copy run of `src/reports/sabres_pregame_fla.py` (with the current ledger CSV) reproduces the md, hero and all three PNGs byte-identically.
