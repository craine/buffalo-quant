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
| Snap counts | `snap_counts/snap_counts_{year}.parquet` | 2012+ (loaded 2018+); verified 2026-11-10; carries `pfr_player_id` |
| Weekly rosters | `weekly_rosters/roster_weekly_{year}.parquet` | 2026 loaded; verified 2026-11-12; status (ACT, DEV practice squad, RES reserve, INA) and team by week |
| Players (one file) | `players/players.parquet` | all; verified 2026-11-12; links `gsis_id` to `pfr_id` (snap counts, PFR charting) |

Current-season files update as games finish. Ingest must be idempotent: re-running replaces
the season's rows, never duplicates them.

Other candidate sources (FTN charting, participation, Next Gen Stats, injuries)
are **unverified**. Confirm the URL returns 200 and inspect the schema before relying on one,
and add it to this table when you do.

### NHL (Sabres)

The NHL API (`api-web.nhle.com/v1/gamecenter/{id}/play-by-play`) is not reachable from the agent shell. A GitHub
Action (`.github/workflows/nhl-ingest.yml`, daily) runs `scripts/nhl_fetch.py` and publishes
`nhl_{games,plays,rosters}_{season}.parquet` to the `nhl-raw` release; `src/ingest/nhl.py` downloads them via the
REST API (`gh api`, not `gh release download`, which needs GraphQL). Seasons 2023-24 onward.

- `details_eventOwnerTeamId` is the shooting team for every shot attempt, including blocked shots.
- `situationCode` digits are [away goalie][away skaters][home skaters][home goalie].
- `homeTeamDefendingSide` gives the net being attacked (x = +/-89); compute distance per period from it.
- xG model: `src/metrics/nhl_xg.py`, unblocked non-empty-net shots only. Validated out of sample on 2025-26. It has no
  season term and drifts (ran 3% hot in 2025-26): rescale per season so league xG = league goals before any G-xG or GSAx.
- Penalty attribution via eventOwner is unverified. Don't publish penalty counts until checked.
- "Departed" players come from game rosters; a player who hasn't dressed yet is not necessarily gone.
- **Daily cards refresh** (`.github/workflows/cards-refresh.yml`): runs after each NHL ingest, rebuilds the league cards
  (`reports/cards/*_league.json`), then commits those two files to `main` as `buffalo-quant-bot`. This is the one approved
  exception to the never-push-to-main rule (approved by Charlie, Nov 2026), and it covers those card data files only. It refuses
  to publish unless `scripts/validate_cards.py`, `tests/test_nhl.py`, `tests/test_cards.py` and `tests/test_review_gate.py` pass and
  pinned story files are untouched. The xG model trains only on completed seasons, so reruns reproduce it exactly
  (`config/xg_fingerprint.json`); this season's per-season rescale moves card numbers slightly each day by design. If the NHL edits
  old play-by-play or a fetch drops a past game, the fingerprint check stops publishing: re-run the ingest, confirm the change is real,
  then `PYTHONPATH=. python scripts/validate_cards.py --update-fingerprint` and commit the new fingerprint in a PR.

- **The site is built by Cloudflare Pages, not committed.** Pages runs `python -m src.site.build` (output `site/`) on every deploy,
  production and preview. `site/` is gitignored: commit the inputs (code, `reports/`, card JSON, `ledger/`), never the pages. The build
  reads only repo files (no database), so anything a page shows must be in a committed file. `make test` builds the site first.
  On Cloudflare (`CF_PAGES` set) a failed NFL card build fails the deploy instead of shipping without `/cards/nfl/`. Python is
  pinned by `.python-version`.

## Known gotchas

- Do **not** use the `nfl_data_py` pip package. It is outdated and its URLs 404. Use the
  release URLs above.
- In `bills_games`-style tables a column named `location` collides with derived `CASE WHEN`
  aliases. Use `loc` for home/road splits.
- PFR charting data does not exist before 2018. Do not backfill or impute.
- pandas 3.x: strings are Arrow-backed by default; be explicit with dtypes when writing to SQLite.
- Team abbreviations change across eras (OAK/LV, SD/LAC, STL/LA). Normalize in `clean_*`.
- **Identify players by gsis id, never by name.** nflverse spells the same player differently across
  games (Josh Allen is both `J.Allen` and `Jos.Allen`; also Minshew, Rodgers, T.Taylor, RG3).
- On scrambles the QB is the *rusher*: use `COALESCE(passer_player_id, rusher_player_id)` for dropbacks.
- NFL participation data (pressure, coverage) does not chart sacks or scrambles before 2023. Use pass
  attempts only for multi-year series that cross 2022/2023, or split at 2023.
- nflverse `pass_attempt` counts sacks. Use `pass_attempt == 1 and sack == 0` for true attempts.
- Participation pressure charting changed definition in 2023 even for pass attempts; compare within season.
- Combined tackles = `def_tackles_solo + def_tackles_with_assist + def_tackle_assists`. Matched ESPN on the 4 players checked and is the
  closest to PFR's count (exact for 59% of players, about 1.8 high on average); solo + assists alone undercounts.
- `raw_players.pfr_id` can point a rookie at a retired player with the same PFR id (e.g. `WoodPe00`). Only trust the link when the
  player's `last_season` is recent; otherwise match snap counts to box scores by team, name and week (`src/reports/nfl_cards.py`).
- Every source lists edge rushers as linebackers. The NFL cards group linebackers with 1+ pressure and <6 tackles a game as pass rushers.
- PFR charting can lag a week behind box scores; use only fully charted weeks (`nfl_cards.py` computes `pfr_week`).
- **Weekly NFL cards refresh** (`.github/workflows/nfl-refresh.yml`, Tuesday and Wednesday 12:17 UTC): loads the new week, runs
  `nfl_cards --latest`, and commits `reports/cards/nfl_players.json` to `main` as `buffalo-quant-bot`. Same approved bot exception as the
  NHL refresh, for that one file only. It refuses to publish unless `scripts/validate_nfl_cards.py`, `tests/test_nfl_cards.py` and
  `tests/test_review_gate.py` pass and pinned story files are untouched. `WEEK` in `nfl_cards.py` is only the default for a manual run.
- NFL weeks (`week_status`): a week's window is its first scheduled game plus five days (the longest real week, 2024–26, is exactly 5).
  It's complete when every game in the window is final. A game rescheduled past the window is **postponed**: it doesn't hold the week,
  and the cards index names it until it's played and loaded; it's also left out of the charting week, team last-week notes and the
  week date. A week counts only once every final game's box score, snap counts and play-by-play have loaded (a Tuesday run can be
  early for Monday night); two days after a week's last game, if it still hasn't, validation fails and names the games. If nflverse
  never posts one game's snaps or play-by-play, the cards can't pass that week: report it upstream (nflverse-data issues) and tell
  Charlie rather than adding a workaround. An unfinished game still inside a window that ended 3+ days ago (cancelled, or the
  schedule not updated) fails validation on purpose: check the schedule rather than letting the cards quietly stop.
- `raw_schedules.home_coach`/`away_coach` is stale for 2026 Bills games (still McDermott). Don't use it for eras.
- `temp` is missing for many outdoor games (about half of 2022 and 2026). Disclose exclusions.
- 2026 Bills play-caller is still Joe Brady (HC); Carmichael is a non-play-calling OC.
- Every article goes through the four-stage editorial process in `docs/editorial-process.md` (self-check, Quant,
  Editor, final check). The site build and `make test` refuse any new story without passing reviews on its exact text.

## Writing for fans (standing rule from Charlie)

- **No jargon in the story body.** Jargon is boring. Say "chances," "goals saved vs. an average goalie" and
  "carries over to next season," not xGF%, GSAx, PDO, Corsi or correlation. Stat terms go only in a
  "For the stat-heads" section at the end.
- **Show the behind-the-scenes reasoning every time.** Every story explains where its key number comes from:
  the source data, the reasoning (with real computed examples, e.g. "shots from within 10 feet go in 13.8% of
  the time"), the math in one plain paragraph, and how we checked it. Include the chart that shows it.
- Tie the explanation back to the headline number ("their chances were worth 237 goals; they scored 256").
- **Published stories never change silently.** Every generator pins its data with an `AS_OF` date (games through that
  date). Re-running it reproduces the published numbers. Updated numbers mean a new, clearly dated story or note.

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
