"""The Ledger: append-only predictions and grades.

ledger/*.csv is the permanent, committed record. The DB tables are rebuilt from it.
Rules enforced here: created_at_utc must precede kickoff; no UPDATE or DELETE, ever;
corrections are new rows whose notes reference the old id.
"""
import csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from src.db import ROOT, connect, query

LEDGER_DIR = ROOT / "ledger"
PRED_CSV = LEDGER_DIR / "predictions.csv"
GRADE_CSV = LEDGER_DIR / "grades.csv"
PRED_COLS = ["id", "created_at_utc", "sport", "season", "week", "game_id", "subject", "claim_text",
             "metric", "threshold", "probability", "resolves_at_utc", "model_version", "notes"]
GRADE_COLS = ["prediction_id", "graded_at_utc", "outcome", "actual_value", "brier", "source_query"]


def _read(path, cols):
    if not path.exists():
        return pd.DataFrame(columns=cols)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _append(path, cols, row):
    LEDGER_DIR.mkdir(exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow(row)


def kickoff_utc(game_id, con=None):
    g = query("SELECT gameday, gametime FROM raw_schedules WHERE game_id = ?", params=(game_id,), con=con)
    if g.empty or not g.gametime[0]:
        raise ValueError(f"No kickoff time for {game_id}")
    local = datetime.strptime(f"{g.gameday[0]} {g.gametime[0]}", "%Y-%m-%d %H:%M")
    return local.replace(tzinfo=ZoneInfo("America/New_York")).astimezone(timezone.utc)  # nflverse times are ET


def add_prediction(*, game_id, subject, claim_text, metric, threshold, probability,
                   model_version, notes="", sport="NFL", now=None, con=None):
    now = now or datetime.now(timezone.utc)
    ko = kickoff_utc(game_id, con)
    if now >= ko:
        raise ValueError(f"Rejected: {now.isoformat()} is not before kickoff {ko.isoformat()}")
    if not 0 < float(probability) < 1:
        raise ValueError("probability must be strictly between 0 and 1")
    existing = _read(PRED_CSV, PRED_COLS)
    pid = f"P{len(existing) + 1:04d}"
    season, week = game_id.split("_")[0], int(game_id.split("_")[1])
    row = dict(id=pid, created_at_utc=now.strftime("%Y-%m-%dT%H:%M:%SZ"), sport=sport, season=season,
               week=week, game_id=game_id, subject=subject, claim_text=claim_text, metric=metric,
               threshold=threshold, probability=f"{float(probability):.2f}",
               resolves_at_utc=ko.strftime("%Y-%m-%dT%H:%M:%SZ"), model_version=model_version, notes=notes)
    _append(PRED_CSV, PRED_COLS, row)
    return pid


def grade(prediction_id, outcome, actual_value, source_query, now=None):
    preds = _read(PRED_CSV, PRED_COLS).set_index("id")
    if prediction_id not in preds.index:
        raise KeyError(prediction_id)
    if prediction_id in set(_read(GRADE_CSV, GRADE_COLS).prediction_id):
        raise ValueError(f"{prediction_id} already graded; grades are append-only")
    p = float(preds.loc[prediction_id, "probability"])
    o = int(outcome)
    row = dict(prediction_id=prediction_id,
               graded_at_utc=(now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
               outcome=o, actual_value=actual_value, brier=f"{(p - o) ** 2:.4f}", source_query=source_query)
    _append(GRADE_CSV, GRADE_COLS, row)


def summary():
    p = _read(PRED_CSV, PRED_COLS)
    g = _read(GRADE_CSV, GRADE_COLS)
    if p.empty:
        return {"predictions": 0, "graded": 0}
    m = p.merge(g, left_on="id", right_on="prediction_id", how="left")
    graded = m[m.outcome != ""].dropna(subset=["outcome"])
    out = {"predictions": len(p), "graded": len(graded)}
    if len(graded):
        out["brier"] = graded.brier.astype(float).mean()
        out["baseline_brier"] = 0.25  # coin-flip baseline
        out["hits"] = int(((graded.probability.astype(float) >= 0.5) == (graded.outcome.astype(int) == 1)).sum())
    return out


def load_to_db():
    con = connect()
    _read(PRED_CSV, PRED_COLS).to_sql("ledger_predictions", con, if_exists="replace", index=False)
    _read(GRADE_CSV, GRADE_COLS).to_sql("ledger_grades", con, if_exists="replace", index=False)
    con.commit()
