# Final check: 2026-wk12-kc-postgame (stage 4)

**Verdict: pass.** Story sha256: bf4236b5214965fa0bee01944b9119696bcfc865b20831a8fc11f48ed1e48b99.

Reviewed the round-2 diff (commit 32a781f3 vs a60dd0d6) and everything it touches: Mahomes start count and rule, big-play line,
run line and sample sentence, rain sentence, Receipts wording, headline, chart legend. No number or claim broke; see quant round 2.

Reproduction: `git archive HEAD` into a clean directory, data/ symlinked to the working copy's database, ran
`python3 -m src.reports.bills_kc_postgame_wk12`. All asserts passed (incl. 2026 pbp fingerprint (28843, -180.1391)). Byte-identical:
- reports/2026-wk12-kc-postgame.md  bf4236b5214965fa0bee01944b9119696bcfc865b20831a8fc11f48ed1e48b99
- reports/bills-kc-wk12-postgame.png  b3c448bc13036551c168e2f5e061d7cb07871e9aecdd22d499668e7f5abca300
- reports/2026-wk12-kc-postgame.hero.json  6f595a796aa0fb3761fa0750af945feeaa490d960eb82904a8e11b41d90f57c7

Still to do at publish: the PNG is not in reports/published_images.json; run scripts/freeze_images.py.
