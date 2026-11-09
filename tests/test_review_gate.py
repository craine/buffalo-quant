import json

import pytest

from src.site import review_gate as rg


def test_gate_blocks_until_all_stages_pass_on_current_text(tmp_path, monkeypatch):
    monkeypatch.setattr(rg, "REVIEWS", tmp_path / "reviews")
    md = tmp_path / "story.md"; md.write_text("v1")
    rep = tmp_path / "r.md"; rep.write_text("report")
    assert rg.problems(md)
    for s in ["self", "quant", "editor"]:
        rg.record(md, s, "pass", "checked", str(rep))
    assert rg.problems(md) == ["final: missing"]
    rg.record(md, "final", "pass", "checked", str(rep))
    assert rg.problems(md) == []
    md.write_text("v2")  # edited after the final check
    assert rg.problems(md) == ["final: story changed after the final check"]
    with pytest.raises(ValueError):
        rg.record(md, "final", "pass", "  ")


def test_every_non_legacy_article_passed_review():
    from src.site.build import ARTICLES, LEGACY, ROOT
    bad = {s: rg.problems(ROOT / "reports" / src) for s, src, *_ in ARTICLES if s not in LEGACY}
    assert not {s: p for s, p in bad.items() if p}, bad
