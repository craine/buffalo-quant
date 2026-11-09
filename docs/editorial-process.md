# Editorial process (every published story)

No story or social post goes public without all four stages. The site build enforces it: `src/site/build.py`
refuses to build any story not listed in `LEGACY` unless `reports/reviews/<story>.json` shows all stages passed and the
final check matches the exact text being published (SHA-256 of the markdown). Edit the story after the final check and
the build fails until it's re-checked.

| Stage | Who | What it checks | Record |
|---|---|---|---|
| 1. Self-check | the writer (Claude) | checklist below | `python3 scripts/review.py record <md> self pass "<notes>"` |
| 2. Quant | independent agent `.claude/agents/quant.md` | every number re-derived from raw data; overclaims; brand rules | stage `quant` |
| 3. Editor | independent agent `.claude/agents/editor.md` | a regular fan can follow it and cares; plain English; story | stage `editor` |
| 4. Final check | the Quant again, on the edited text | edits didn't break numbers or claims | stage `final` (must match current text) |

Each reviewer's full report is saved next to the record (`reports/reviews/<story>-<stage>.md`); the record links to it.
Reviewers get the files, not the writer's conclusions. Fixes from stage 2 and 3 are applied before stage 4.
Charlie sees the story after stage 4, with a short note on what each stage changed. He makes the call to publish.

## Self-check (stage 1)

- [ ] Every number in the story is produced by the generator. Grep the generator's text for literal digits and justify each.
- [ ] The generator is pinned (AS_OF / THRU) and re-running it reproduces the committed files.
- [ ] Every chart opened and looked at: labels, overlaps, footer has source and sample size.
- [ ] Every claim (rank, "best", "first", "only", "still", "always") maps to a line of code.
- [ ] Small samples (< ~100 plays, a handful of games) are labeled.
- [ ] Ledger calls in the story match the logger script exactly (wording, probability, model version).
- [ ] No betting language: odds, lines, spreads, picks, locks, favorites as a betting term, over/under.
- [ ] The first sentence works on radio. Stat terms only in "For the stat-heads".

## Social posts

Same rule, lighter form: every number in a post must appear in a published, reviewed story. Posts are drafted from the
story and checked by the Quant against it before posting.
