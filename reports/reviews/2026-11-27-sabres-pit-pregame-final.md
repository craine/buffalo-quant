# Final check: 2026-11-27-sabres-pit-pregame (commit b88bf96c)

**Verdict: PASS.**

- Ran in a clean clone of b88bf96c (`/tmp/tmp.TCqdz4Z8Q5/repo`, HEAD b88bf96cff42...), with the data symlinked in: `PYTHONPATH=. python3 -m src.reports.sabres_pregame_pit_nov27`. Exit 0; all asserts passed.
- The outputs are byte-identical to the committed files (SHA-256):
  - md: f1102b3be277185c6d4e7b396d1f0d561f6079c39f3691820aaebe031aea2a7d (identical)
  - PNG: 131248f1b9684de052d88d633e4036f9bb49b771e10d38c83d15ef29b916472d (identical; matches published_images.json)
  - hero: dde59ecf20b4280d9769ab6d90f3f69ee45cbb980d523f6d7f3e3c4f6e33591f (identical)
- `git status` in the clone was clean afterwards (only the untracked data symlink).
- The edited text keeps every number and claim that the Quant verified in rounds 1 and 2.
