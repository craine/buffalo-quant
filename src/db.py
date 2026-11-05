"""All database access goes through here. Portable SQL only (Postgres migration later)."""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "buffalo.db"


def connect(path=DB_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def query(sql, params=None, con=None):
    own = con is None
    con = con or connect()
    try:
        return pd.read_sql(sql, con, params=params)
    finally:
        if own:
            con.close()


def write(df, table, con, if_exists="append"):
    df = df.copy()
    for c in df.columns:  # pandas 3.x Arrow strings -> plain objects for sqlite
        if str(df[c].dtype) in ("string", "str") or df[c].dtype == object:
            df[c] = df[c].astype(object).where(df[c].notna(), None)
    df.to_sql(table, con, if_exists=if_exists, index=False, chunksize=5000)
