# Final check: Penguins 6, Sabres 3 (2026-11-27)

Commit 117133bd. **Verdict: PASS.**

## Reproduction
- Clean `git clone` of the worktree, checked out at 117133bd.
- `data` symlinked to `/home/claude/buffalo-quant/data`.
- Ran `PYTHONPATH=. python3 -m src.reports.sabres_pit_postgame_nov27`. All asserts passed, and `git status` showed no tracked changes.
- `cmp` against the committed files: all three are byte-identical.
  - `reports/2026-11-27-sabres-pit-postgame.md`: sha256 2ac6cbd6268374a812ee12b48ef695a8bad94fbfe2f0a3e119fa6706659f1188
  - `reports/sabres-pit-nov27-postgame.png`: sha256 a9b2d59e75b038848232a9ae01129010e3bef6e8e6f40535e2e603d83c513bfd. This matches `published_images.json`.
  - `reports/2026-11-27-sabres-pit-postgame.hero.json`: sha256 345a9cc5029ee68c6f61c699cb63e1ca35585a543a5d650f2b6635c82c7b5243

## Scope
The round-2 Quant and Editor reviews cover every change since round 1. The edits didn't break any number or claim.
