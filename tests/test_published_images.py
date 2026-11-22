"""Published stories never change silently: every image a story on the site shows must match its frozen hash.

If this fails:
- a frozen image changed: another story or a re-run overwrote it. Restore it (git checkout the file) and give the new
  story its own file names. A deliberate correction uses scripts/freeze_images.py --change ... --reason ...
- an image isn't frozen: a new story was added to the site; run python3 scripts/freeze_images.py and commit the manifest.
"""
import importlib.util

from src.db import ROOT

spec = importlib.util.spec_from_file_location("freeze_images", ROOT / "scripts" / "freeze_images.py")
fz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fz)


def test_frozen_images_unchanged():
    m = fz.load()
    assert m["images"], "reports/published_images.json is missing or empty"
    changed = [n for n, h in m["images"].items() if not (ROOT / "reports" / n).exists() or fz.sha(n) != h]
    assert not changed, f"published images changed or missing: {changed}"


def test_every_story_image_is_frozen():
    m = fz.load()
    missing = sorted(set(fz.story_images()) - set(m["images"]))
    assert not missing, f"run scripts/freeze_images.py; not frozen yet: {missing}"
