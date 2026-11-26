# Final check: 2026-wk12-kc-preview

Text SHA-256 8a76608dc35d98a960f7d422931d605b233873029be5387e671ca86d966056e8 (commit b2d857cc). Verdict: **pass**.

- Reviewed only the round-2 changes and what they touch (see the -quant.md and -editor.md round-2 reports). The edits broke no numbers or claims.
- Byte-identical reproduction: fresh clone of bills-kc-preview-wk12 at b2d857cc into /tmp/qa/clean2, data/ symlinked to the working copy's database, `PYTHONPATH=. python3 -m src.reports.bills_kc_preview_wk12` exited 0, and all asserts passed (fingerprint, Ledger match, 659/657, wind directions, timestamp, weather, part 4). `cmp` shows identical output for reports/2026-wk12-kc-preview.md, reports/bills-kc-wk12-preview.png and reports/2026-wk12-kc-preview.hero.json. The clone's git status was clean apart from the data symlink.
- Open, non-blocking: the 0.500-game wording in stat-heads (see -quant.md). If it's changed, the text hash changes and the final check must be re-run.
- Before publishing: freeze the chart with `python3 scripts/freeze_images.py`.
