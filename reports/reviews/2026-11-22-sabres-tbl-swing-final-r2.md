# Final check: 2026-11-22-sabres-tbl-swing (stage 4)

**Verdict: FAIL (not yet).** The markdown as it stands passes. Every number and claim was re-derived in round 2, and the round-1 must-fixes are resolved in the text:

- method changed to halves, with goaltending reported separately
- rate-based rank (8 teams)
- key 2 "missed"
- hero second value 8.5
- definitions split into separate sentences
- overclaims softened in the body and chart

It still can't pass, because the final check covers every published line and two homepage lines still say "those rarely last" about finishing and saves together:

- the hero note in `reports/2026-11-22-sabres-tbl-swing.hero.json`
- the card dek in `src/site/build.py`

The halves split shows about a third of the combined edge carries over. The review gate hashes only the markdown, so recording a pass now would let those lines publish unfixed.

To pass, change both lines:
- Hero note: "Finishing and saves swung it. Finishing rarely lasts, and goaltending only partly. Chances do, and Buffalo has had more of them in only 9 of 24 games."
- Card dek: "Finishing and saves swung it. Finishing rarely lasts, goaltending only partly. Chances do."

Then re-run final. If the optional polish is taken ("right at average", chart subtitle), the markdown and PNG change, and the final check will cover those too.
