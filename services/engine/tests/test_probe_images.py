"""The harder probe pictures (chat screenshot, WhatsApp-compressed, cropped, phone photo of a
screen, low resolution) rendered by eval/images.py. The Tesseract tests are skipped without
Tesseract. They assert only SAFETY: an edited picture is never confirmed as genuine. How often
honest pictures come out right is measured by eval/run.py, not asserted here."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from confam_engine.ocr import check_readings
from confam_engine.ocr.imageio import load_image
from confam_engine.ocr.tesseract import default_readers, tesseract_available
from eval import images as im
from eval.corpus import load_record

RECORD, _ = load_record()
CURRENT = next(n for n in RECORD if n.id == "SEC-2026-140").text
NOW = datetime(2026, 11, 8, 12, 0, tzinfo=timezone.utc)
ABOVE, BELOW = ("Forwarded", "~ Ngozi Eze"), ("10:42 AM",)

needs_tesseract = pytest.mark.skipif(not tesseract_available(), reason="Tesseract is not installed")


def test_the_renderer_makes_valid_pictures_with_boxes_inside_the_image():
    r = im.render(CURRENT, above=ABOVE, below=BELOW, bubble=True)
    for _, x, y, w, h in r.body_words:
        assert 0 <= x <= 1 and 0 <= y <= 1 and w > 0 and h > 0 and x + w <= 1.001 and y + h <= 1.001
    for data in (im.to_png(r.image), im.whatsapp_compress(r.image), im.low_resolution(r.image), im.phone_photo(r.image)):
        assert load_image(data).size[0] > 100


def test_the_degraders_are_deterministic():
    r = im.render(CURRENT)
    assert im.phone_photo(r.image, 7) == im.phone_photo(r.image, 7)
    assert im.phone_photo(r.image, 7) != im.phone_photo(r.image, 8)


EDITS = {
    "date": CURRENT.replace("28th November", "29th November"),
    "link": CURRENT.replace("register.sec.example", "register-sec.example"),
    "month": CURRENT.replace("28th November", "28th December"),
}
DEGRADE = {
    "clean": im.to_png,
    "whatsapp": im.whatsapp_compress,
    "low_res": im.low_resolution,
    "phone": lambda img: im.phone_photo(img, 7),
}


@needs_tesseract
@pytest.mark.parametrize("how", DEGRADE)
@pytest.mark.parametrize("edit", EDITS)
def test_an_edited_picture_is_never_confirmed(edit, how):
    rendered = im.render(EDITS[edit], above=ABOVE, below=BELOW, bubble=(how != "low_res"))
    data = DEGRADE[how](rendered.image)
    img = load_image(data)
    verdict = check_readings([r.read(img) for r in default_readers()], RECORD, record_as_of=NOW, lang="en", now=NOW)
    assert verdict.verdict.value != "confirmed", (edit, how, verdict.verdict)