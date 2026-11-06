"""NHL release assets (tag nhl-raw, built by .github/workflows/nhl-ingest.yml) -> raw_nhl_* tables.

Downloads with the GitHub CLI because the repo is private. Fails loudly if assets are missing.
"""
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.db import ROOT, connect, write

REPO = "craine/buffalo-quant"
DL = ROOT / "data" / "nhl"


def gh_api(path, accept=None):
    cmd = ["gh", "api", path] + (["-H", f"Accept: {accept}"] if accept else [])
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"BLOCKED: gh api {path}: {r.stderr.decode().strip()[:300]}")
    return r.stdout


def download():
    """REST only (GraphQL is unavailable in this environment)."""
    import json
    DL.mkdir(parents=True, exist_ok=True)
    rel = json.loads(gh_api(f"repos/{REPO}/releases/tags/nhl-raw"))
    for a in rel["assets"]:
        (DL / a["name"]).write_bytes(gh_api(f"repos/{REPO}/releases/assets/{a['id']}", "application/octet-stream"))
        print("downloaded", a["name"], a["size"])


def main():
    download()
    con = connect()
    for kind in ("games", "plays", "rosters"):
        files = sorted(DL.glob(f"nhl_{kind}_*.parquet"))
        if not files:
            sys.exit(f"BLOCKED: no nhl_{kind} files in release")
        df = pd.concat([pd.read_parquet(f).assign(season=int(f.stem.split("_")[-1])) for f in files], ignore_index=True)
        write(df, f"raw_nhl_{kind}", con, if_exists="replace")
        print(f"raw_nhl_{kind}", len(df), sorted(df.season.unique()))
    con.commit()


if __name__ == "__main__":
    main()
