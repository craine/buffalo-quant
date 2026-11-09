"""Publishing gate: a story builds only after self, quant, editor and final reviews pass on its exact text."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.db import ROOT

REVIEWS = ROOT / "reports" / "reviews"
STAGES = ["self", "quant", "editor", "final"]


def sha(md_path):
    return hashlib.sha256(Path(md_path).read_bytes()).hexdigest()


def _file(md_path):
    return REVIEWS / f"{Path(md_path).stem}.json"


def load(md_path):
    f = _file(md_path)
    return json.loads(f.read_text()) if f.exists() else {}


def record(md_path, stage, verdict, notes, report=None):
    if stage not in STAGES or verdict not in ("pass", "fail"):
        raise ValueError("stage must be one of %s; verdict pass|fail" % STAGES)
    if not notes.strip():
        raise ValueError("notes required: say what was checked and what changed")
    REVIEWS.mkdir(parents=True, exist_ok=True)
    rec = load(md_path)
    entry = dict(verdict=verdict, sha256=sha(md_path), at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), notes=notes)
    if report:
        dst = REVIEWS / f"{Path(md_path).stem}-{stage}.md"
        shutil.copyfile(report, dst)
        entry["report"] = dst.name
    rec.setdefault("history", []).append(dict(stage=stage, **entry))
    rec[stage] = entry
    _file(md_path).write_text(json.dumps(rec, indent=1))
    return status(md_path)


def problems(md_path):
    rec, cur = load(md_path), sha(md_path)
    out = [f"{s}: missing" for s in STAGES if s not in rec]
    out += [f"{s}: {rec[s]['verdict']}" for s in STAGES if s in rec and rec[s]["verdict"] != "pass"]
    for s in ("quant", "editor"):
        if s in rec and "report" not in rec[s]:
            out.append(f"{s}: no saved reviewer report")
    if "final" in rec and rec["final"]["sha256"] != cur:
        out.append("final: story changed after the final check")
    return out


def status(md_path):
    p = problems(md_path)
    return "READY: all reviews pass on the current text" if not p else "BLOCKED: " + "; ".join(p)
