"""The demo set (fixtures/sec-sim/demo): six checks that must behave as the README says.

Files, README and expected.json are checked everywhere; the pictures are also run through the real
pipeline (Tesseract, two readings, the default confidence gate of 95) when Tesseract is installed."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from confam_engine.ocr.tesseract import tesseract_available

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "fixtures" / "sec-sim" / "demo"
EXPECTED = json.loads((DEMO / "expected.json").read_text(encoding="utf-8"))
README = (DEMO / "README.md").read_text(encoding="utf-8")

FILES = [
    "01_honest_confirmed.png", "02_altered_date.png", "03_altered_link_PASTE.txt",
    "04_not_official.png", "05_partial_crop.png", "06_cannot_confirm_blurry.png",
]
VERDICTS = {
    "01_honest_confirmed": "confirmed", "02_altered_date": "altered", "03_altered_link_PASTE": "altered",
    "04_not_official": "not_official", "05_partial_crop": "partial", "06_cannot_confirm_blurry": "cannot_confirm",
}


def test_all_six_files_exist_are_small_and_documented():
    for name in FILES:
        path = DEMO / name
        assert path.exists(), name
        assert path.stat().st_size < 200_000, name
        assert name in README, f"{name} is not described in the demo README"


def test_expected_json_covers_every_item_with_the_verdict_the_readme_promises():
    assert {k: v["verdict"] for k, v in EXPECTED.items()} == VERDICTS
    for stem, verdict in VERDICTS.items():
        assert {"confirmed": "Confirmed", "altered": "Altered", "not_official": "Not official", "partial": "Partial", "cannot_confirm": "Cannot confirm"}[verdict] in README


def test_the_set_is_the_fictional_commission_only():
    text = (DEMO / "03_altered_link_PASTE.txt").read_text(encoding="utf-8")
    assert "Simulated Electoral Commission" in text
    assert "inec" not in (README + text).lower()
    assert "." + "gov" not in (README + text).lower()  # built in pieces: the repo-wide address scan reads this file too


def test_the_readme_is_honest_about_the_changed_link_and_the_confidence_gate():
    assert "never called Altered" in README and "95" in README
    assert "pasted text, not a photo" in README


@pytest.mark.skipif(not tesseract_available(), reason="Tesseract is not installed")
def test_every_demo_item_still_gives_its_verdict_through_the_real_pipeline():
    from eval import make_demo as md

    for name, stem, _text, how, accept in md.SCENARIOS:
        if how == "text":
            from confam_engine import check_notice

            v = check_notice((DEMO / f"{stem}.txt").read_text(encoding="utf-8").strip(), md.RECORD, record_as_of=md.NOW, now=md.NOW)
        else:
            v = md.verdict_for((DEMO / f"{stem}.png").read_bytes())
        assert accept(v), (stem, v.verdict)
        assert v.verdict.value == VERDICTS[stem]
        assert v.verdict.value != "confirmed" or stem == "01_honest_confirmed"  # only the honest one is ever confirmed
