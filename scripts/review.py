"""Record and check editorial reviews. See docs/editorial-process.md.

  python3 scripts/review.py record reports/<story>.md <self|quant|editor|final> <pass|fail> "notes" [report.md]
  python3 scripts/review.py status reports/<story>.md
"""
import sys
sys.path.insert(0, ".")
from src.site.review_gate import record, status

if __name__ == "__main__":
    cmd, md = sys.argv[1], sys.argv[2]
    if cmd == "record":
        print(record(md, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else None))
    else:
        print(status(md))
