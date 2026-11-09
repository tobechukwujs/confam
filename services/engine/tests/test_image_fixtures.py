"""Fixture pictures of the fictional notice, and the full image pipeline on them.

The OCR tests need the Tesseract program and are SKIPPED when it is not installed. Everything
else here runs anywhere."""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from confam_engine import OfficialNotice, Replacement
from confam_engine.ocr import check_readings
from confam_engine.ocr.imageio import load_image
from confam_engine.ocr.tesseract import default_readers, tesseract_available

ROOT = Path(__file__).resolve().parents[3]
IMAGES = ROOT / "fixtures" / "sec-sim" / "images"
NOTICES = json.loads((ROOT / "fixtures" / "sec-sim" / "notices.json").read_text(encoding="utf-8"))["notices"]
EXPECTED = json.loads((IMAGES / "expected.json").read_text(encoding="utf-8"))
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
AS_OF = datetime(2026, 11, 8, 11, 30, tzinfo=timezone.utc)


def record():
    out = []
    for n in NOTICES:
        sup = n.get("superseded_by")
        out.append(
            OfficialNotice(
                id=n["id"], title=n["title"], published=n["published"], url=n["url"], text=n["text"],
                superseded_by=Replacement(sup["id"], sup["published"]) if sup else None,
            )
        )
    return out


needs_tesseract = pytest.mark.skipif(
    not tesseract_available(), reason="Tesseract is not installed (see README: winget install UB-Mannheim.TesseractOCR)"
)


# --- no OCR needed ------------------------------------------------------------


@pytest.mark.parametrize("name", ["honest", "date_edit", "cropped", "blurry"])
def test_fixture_pictures_exist_decode_and_are_small(name):
    data = (IMAGES / f"{name}.png").read_bytes()
    assert len(data) < 200_000
    img = load_image(data)
    assert img.size == (1200, 520)


def test_the_pictures_are_the_fictional_commission_notice_only():
    text = next(n["text"] for n in NOTICES if n["id"] == "SEC-2026-140")
    assert "Simulated Electoral Commission" in text
    for forbidden in ("INEC", "Independent National"):
        assert forbidden.lower() not in text.lower()


def test_the_generator_reproduces_the_committed_pictures():
    spec = importlib.util.spec_from_file_location("make_images", IMAGES / "make_images.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fresh, _ = mod.render(mod.TEXT)
    committed = Image.open(IMAGES / "honest.png").convert("RGB")
    assert ImageChops.difference(fresh, committed).getbbox() is None


def test_the_expected_box_is_a_valid_box_over_the_edited_date():
    x, y, w, h = EXPECTED["date_edit"]["box"]
    assert all(0 <= v <= 1 for v in (x, y, w, h)) and w > 0 and h > 0
    assert x + w <= 1 and y + h <= 1
    # the edited picture differs from the honest one inside that box and nowhere much else
    honest = Image.open(IMAGES / "honest.png").convert("L")
    edited = Image.open(IMAGES / "date_edit.png").convert("L")
    diff = ImageChops.difference(honest, edited).getbbox()
    assert diff is not None
    W, H = honest.size
    bx0, by0, bx1, by1 = x * W - 5, y * H - 5, (x + w) * W + 5, (y + h) * H + 5
    assert diff[0] >= bx0 - 80 and diff[2] <= bx1 + 80 and diff[1] >= by0 and diff[3] <= by1


# --- full pipeline, needs Tesseract --------------------------------------------


def run(name: str):
    img = load_image((IMAGES / f"{name}.png").read_bytes())
    readings = [r.read(img) for r in default_readers()]
    return check_readings(readings, record(), record_as_of=AS_OF, lang="en", now=NOW)


@needs_tesseract
def test_an_honest_picture_is_confirmed():
    v = run("honest")
    assert v.verdict.value == "confirmed", (v.verdict, v.reason, v.changes)
    assert v.notice.id == "SEC-2026-140"


@needs_tesseract
def test_a_one_date_edit_is_altered_with_a_box_over_the_date():
    v = run("date_edit")
    assert v.verdict.value == "altered", (v.verdict, v.reason, v.changes)
    date = next(c for c in v.changes if c.kind.value == "date")
    assert date.copy_ == "29th November" and date.official == "28th November"
    ex, ey, ew, eh = EXPECTED["date_edit"]["box"]
    bx, by, bw, bh = (b.root for b in date.box)
    overlap_w = min(ex + ew, bx + bw) - max(ex, bx)
    overlap_h = min(ey + eh, by + bh) - max(ey, by)
    assert overlap_w > 0 and overlap_h > 0, "the mark must sit over the edited date"


@needs_tesseract
def test_a_cropped_picture_is_partial():
    v = run("cropped")
    assert v.verdict.value == "partial", (v.verdict, v.reason, v.changes)
    assert v.notice.id == "SEC-2026-140"


@needs_tesseract
def test_a_blurry_picture_is_never_confirmed_or_altered():
    v = run("blurry")
    assert v.verdict.value == "cannot_confirm", (v.verdict, v.reason)


@needs_tesseract
def test_no_edited_picture_is_ever_confirmed():
    assert run("date_edit").verdict.value != "confirmed"
