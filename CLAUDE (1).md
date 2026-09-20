# CLAUDE.md — Buffalo Quant Desk

Project memory for Claude Code. Read this fully before any task.

## What this is

A sports analytics platform covering the Buffalo Bills (first) and Buffalo Sabres (later).
Goal: become the trusted quantitative voice on Buffalo sports — a public site, a graded
prediction tracker, and material for local radio and podcast appearances.

Owner: Charlie. He is the voice and makes editorial calls. You build the plumbing,
models, and drafts.

## Brand rules (non-negotiable)

1. **No betting content.** No spreads, odds, picks, units, or market comparisons. Projections
   are analysis, not wagering advice.
2. **Receipts.** Every public prediction is logged before kickoff with a probability and graded
   afterward. Misses are never deleted or edited.
3. **Predictive over descriptive.** Say what happens next and why, not only what happened.
4. **Plain English.** Every finding must reduce to one sentence a radio host can repeat and
   one chart a fan can read.
5. **Every published number is traceable** to a query in this repo. Never state a number you
   did not compute. Never estimate, recall from training, or fill gaps with plausible values.

## Architecture

Same raw-to-cleaned pattern as Charlie's trading system.

```
raw_*      league-wide tables, loaded as-is from source, never hand-edited
clean_*    typed, filtered, Bills-scoped or league-scoped analysis tables
ledger_*   predictions and grades (append-only)
```

- Backend: SQLite at `data/buffalo.db`. Postgres migration comes later; write portable SQL
  and keep all DB access behind `src/db.py`.
- **The database is disposable.** It is gitignored and must rebuild from scratch with
  `make ingest`. Never commit `.db` or `.parquet` files.
- Exception: `ledger_*` tables are the permanent record. They are exported to
  `ledger/*.csv` (committed) after every write and re-imported on rebuild.

## Repo layout

```
CLAUDE.md
Makefile                 ingest | test | report | all
requirements.txt         pandas, pyarrow, matplotlib, pytest
config/seasons.yaml      season ranges per source
src/db.py                connection + helpers
src/ingest/              one module per source -> raw_*
src/clean/               raw_* -> clean_*
src/metrics/             reusable metric functions (EPA splits, ranks, filters)
src/ledger/              add_prediction, grade, export
src/reports/             report generators
tests/                   validation + unit tests
reports/                 generated markdown + PNG charts (committed)
ledger/                  CSV exports of ledger tables (committed)
data/                    gitignored
```

## Data sources (nflverse-data GitHub releases)

Base: `https://github.com/nflverse/nflverse-data/releases/download/`
Direct parquet URLs, no auth. Ingest with `pd.read_parquet(url)`.
All confirmed live for 2026 on 2026-09-20.

| Data | Path | Seasons |
|---|---|---|
| Play-by-play | `pbp/play_by_play_{year}.parquet` | 1999+ |
| Weekly player stats | `stats_player/stats_player_week_{year}.parquet` | |
| Weekly team stats | `stats_team/stats_team_week_{year}.parquet` | |
| Schedules (one file) | `schedules/games.parquet` | all |
| PFR advanced passing | `pfr_advstats/advstats_week_pass_{year}.parquet` | 2018+ (hard floor) |
| PFR advanced defense | `pfr_advstats/advstats_week_def_{year}.parquet` | 2018+ |

Current-season files update as games finish. Ingest must be idempotent: re-running replaces
the season's rows, never duplicates them.

Other candidate sources (FTN charting, participation, Next Gen Stats, injuries, snap counts)
are **unverified**. Confirm the URL returns 200 and inspect the schema before relying on one,
and add it to this table when you do.

## Known gotchas

- Do **not** use the `nfl_data_py` pip package. It is outdated and its URLs 404. Use the
  release URLs above.
- In `bills_games`-style tables a column named `location` collides with derived `CASE WHEN`
  aliases. Use `loc` for home/road splits.
- PFR charting data does not exist before 2018. Do not backfill or impute.
- pandas 3.x: strings are Arrow-backed by default; be explicit with dtypes when writing to SQLite.
- Team abbreviations change across eras (OAK/LV, SD/LAC, STL/LA). Normalize in `clean_*`.

## Analysis conventions

- Regular season only unless stated. Playoffs tagged separately, never mixed silently.
- Play filter for efficiency metrics: `pass == 1 or rush == 1`, EPA not null. Exclude kneels,
  spikes, two-point tries, and no-plays.
- Core metrics: EPA/play, success rate, dropback vs. rush splits, explosive play rate
  (pass 20+ yds, rush 10+ yds), third-down and red-zone rates, sack rate, turnover rate.
- **Garbage time:** report both unfiltered and filtered (win probability between 0.10 and 0.90).
  Say which one a headline number uses.
- **Always show sample size.** Anything under ~100 plays gets an explicit small-sample label.
- **Always give context:** league rank and league average next to every Bills number.
- Opponent adjustment: early season, use the opponent's prior-season numbers and say so.
  Switch to in-season once 6+ weeks exist.
- Coaching eras for splits: Brady as OC began mid-2023; Brady HC / Leonhard DC / Carmichael OC
  began 2026; McDermott HC 2017–2025; Babich DC 2024–2025. Verify exact game boundaries from
  the schedule before hard-coding them.

## The Ledger

`ledger_predictions` (append-only):
`id, created_at_utc, sport, season, week, game_id, subject, claim_text, metric, threshold,
probability, resolves_at_utc, model_version, notes`

`ledger_grades` (append-only): `prediction_id, graded_at_utc, outcome (0/1), actual_value,
brier, source_query`

Rules:
- `created_at_utc` must be before kickoff of the referenced game. Reject otherwise.
- No UPDATE or DELETE on either table, ever. Corrections are new rows that reference the old id.
- Benchmarks are a naive baseline (prior-season rate, or 50%) and, where available, public
  non-betting models. Never sportsbook lines.
- Summary metrics: Brier score, calibration by probability bucket, record vs. baseline.

## Validation (must pass before any report is generated)

- Row counts per season within expected range; no duplicate `(game_id, play_id)`.
- Bills game count and final scores in `raw_pbp` match `raw_schedules`.
- No nulls in key columns (`game_id`, `posteam`, `defteam`, `epa` on filtered plays).
- Every season requested in `config/seasons.yaml` is present.
- League-wide sanity: mean EPA/play near zero per season.

## How to work

- Work on a branch, open a PR, never push to `main`. Small commits with clear messages.
- Write tests alongside code. `make test` must pass before you open the PR.
- **If a network fetch is blocked or a source is missing: stop and report it in the PR
  description.** Do not substitute synthetic, cached-from-memory, or sample data.
- If a result looks surprising, check it a second way before writing it up, and show both.
- Reports are markdown in `reports/` with matplotlib PNGs. Lead with the one-sentence
  finding, then the chart, then the method and caveats.
- Charts: clean, high-contrast, Bills blue `#00338D` and red `#C60C30`, source line and
  sample size in the footer.
- When you finish a task, end the PR description with: what was built, what was verified,
  what is uncertain, and the three most interesting things in the data.

## Roadmap

1. **POC (now):** ingest, validation, 2025-vs-2026 defense baseline, Ledger schema.
2. Josh Allen module (pressure, red zone, temperature vs. location, turnover-worthy plays).
3. Coaching fingerprints: Brady play-calling (2023–25 vs. 2026), Leonhard defense tracker,
   fourth-down and game-management decisions.
4. Weekly cycle: Monday post-game report, Thursday preview with logged predictions.
5. Sabres: own xG model from public shot-location data. Sources unverified; research and
   confirm before building.
6. Public site, Postgres, subscriptions.
