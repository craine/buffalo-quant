"""Freeze the images published stories show, so a later story can't silently change them.

reports/published_images.json maps every PNG a story on the site embeds (its markdown images plus its card image) to its
SHA-256. tests/test_published_images.py fails if a frozen image changes, or if a story on the site uses an image that
isn't frozen yet.

  python3 scripts/freeze_images.py              # add images of newly published stories; never changes existing entries
  python3 scripts/freeze_images.py --change reports/x.png --reason "dated correction, see note in story"
                                                # deliberately replace one frozen image; the reason is kept in the file
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MANIFEST = ROOT / "reports" / "published_images.json"


def story_images():
    """{image file name: [story md files that show it]} for every story on the site."""
    from src.site.build import ARTICLES
    out = {}
    for a in ARTICLES:
        md, hero = a[1], a[-1]
        text = (ROOT / "reports" / md).read_text()
        imgs = set(re.findall(r"\]\(([^)\s]+\.png)\)", text)) | ({hero} if hero else set())
        for im in imgs:
            out.setdefault(im, []).append(md)
    return out


def sha(name):
    return hashlib.sha256((ROOT / "reports" / name).read_bytes()).hexdigest()


def load():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"images": {}, "changes": []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--change", help="a frozen image to replace on purpose")
    ap.add_argument("--reason", help="why (required with --change)")
    args = ap.parse_args()
    m = load()
    if args.change:
        name = Path(args.change).name
        if name not in m["images"]:
            sys.exit(f"{name} isn't frozen")
        if not args.reason:
            sys.exit("--reason is required")
        old, new = m["images"][name], sha(name)
        m["images"][name] = new
        m["changes"].append({"image": name, "from": old, "to": new, "reason": args.reason,
                             "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
        print(f"changed {name}")
    added = []
    for name in sorted(story_images()):
        if name not in m["images"]:
            m["images"][name] = sha(name)
            added.append(name)
    MANIFEST.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(f"{len(added)} added: {', '.join(added) or '-'}; {len(m['images'])} frozen")


if __name__ == "__main__":
    main()
