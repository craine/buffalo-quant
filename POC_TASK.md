# POC_TASK.md — First unattended build

Read `CLAUDE.md` first. Execute these steps in order on a branch named `poc`. Open a PR at the end.

## Step 0 — Connectivity check (do this first, fail fast)

Fetch `https://github.com/nflverse/nflverse-data/releases/download/schedules/games.parquet`
with pandas. If it fails, **stop immediately**: commit a short `reports/BLOCKED.md` with the
exact error and the domains that need allowlisting (likely `github.com`,
`release-assets.githubusercontent.com`, `objects.githubusercontent.com`), open the PR, and end.
Do not proceed with any substitute data.

## Step 1 — Scaffold

Create the repo layout from `CLAUDE.md`: Makefile, requirements, `.gitignore` (data/, *.db,
*.parquet), `config/seasons.yaml`, `src/` packages, `tests/`.

## Step 2 — Ingest

- Seasons: play-by-play, team stats, player stats, PFR pass and PFR def for **2023–2026**.
  Schedules: the single all-years file. Season range is config-driven so it extends to 1999 later.
- Load to `raw_*` tables. Idempotent per season.
- Note in the PR which 2026 weeks are present at run time.

## Step 3 — Validation

Implement every check in the Validation section of `CLAUDE.md` as pytest tests. Include a
specific check that the Bills' 2026 results in play-by-play match the schedule file.

## Step 4 — Clean tables

- `clean_plays`: filtered plays with era tags, garbage-time flag, explosive flag, normalized teams.
- `clean_team_defense_week`: one row per team-week with EPA/play allowed, success rate allowed,
  dropback and rush splits, explosive rate, third-down rate, red-zone TD rate, sack rate,
  turnover rate, play counts. Filtered and unfiltered versions of EPA and success rate.

## Step 5 — Report: "Is the Bills defense actually better?"

Write `reports/2026-defense-baseline.md`:

- 2025 Bills defense (full season, by-week trend, league rank in each metric) as the baseline.
- 2026 Bills defense to date, same metrics, with league rank to date and play counts.
- Run defense specifically (the 2025 weak spot) and pass-rush proxies (sack rate, PFR pressure
  and blitz data if the def file supports it; inspect the schema and report what it offers).
- Context for points allowed in 2026: opponent offensive quality using 2025 numbers, garbage-time
  share of yards and points allowed, and drives-level view (points per drive, drive success rate).
- 3–4 charts. One must be a single shareable summary chart.
- Lead with a one-sentence finding. Label everything from 2026 as small sample.
- End with: five follow-up angles the data suggests, ranked by how interesting they are.

## Step 6 — Ledger

Implement `ledger_predictions` and `ledger_grades` per `CLAUDE.md`: schema, append-only
enforcement (triggers that block UPDATE/DELETE), `add_prediction` and `grade` functions with a
small CLI, CSV export/import, Brier and calibration summary, and tests — including a test that a
prediction timestamped after kickoff is rejected. Do not add any real predictions.

## Step 7 — PR

`make all` runs clean from an empty `data/`. PR description follows the template at the end of
the "How to work" section in `CLAUDE.md`.
