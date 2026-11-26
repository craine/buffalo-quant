# Final check: Sabres 5, Rangers 1 (2026-11-25-sabres-nyr-postgame)

Reviewer: Quant (stage 4), commit 5408f9d9. Story sha256 10dad776310ccf344efe6f6c69a04147e4a2fd6661e0020414b86d00f8d20102.

## Verdict: pass

**What changed since the stage-2 and stage-3 reviews:**
- Round 2: lead rewrite, the goalie-rotation line plus its check, the Receipts rewrite, "cancelled out" in the lead and dek, "How we checked it", goal-difference sentence, footnote.
- Round 3: the "empty-net or shootout goals" label, and commas.

The Quant reviewed all of these in rounds 2 and 3 against an independent derivation. Nothing else changed.

**Byte-identical reproduction:**
- Method: `git archive 5408f9d9` into a clean directory (/tmp/q/clean3), `data/` symlinked to the live database, then `python3 -m src.reports.sabres_nyr_postgame_nov25`.
- Result: `cmp` finds these three files identical to the committed ones:
  - reports/2026-11-25-sabres-nyr-postgame.md
  - reports/2026-11-25-sabres-nyr-postgame.hero.json
  - reports/sabres-nyr-nov25-postgame.png
- AS_OF is 2026-11-25. All 399 games through that date are final; no late-game exclusions are needed.

**Other checks:**
- Site dek (src/site/build.py): "...cancelling out an unlucky first 21 games. What lasts: they get 48% of the chances, 22nd." Its numbers match the story.
- Ledger: P0023 graded once (outcome 1, 0.2601). The predictions and grades CSVs weren't touched this round.
