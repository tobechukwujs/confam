"""Safe in-memory image loading, the two preparations, and the Tesseract reader (with the
Tesseract call itself replaced, so no binary is needed here)."""

from __future__ import annotations

import io
import os

import pytest
from PIL import Image

from confam_engine.ocr import imageio
from confam_engine.ocr.imageio import ImageError, load_image, sniff_type
from confam_engine.ocr.tesseract import (
    OcrUnavailable,
    TesseractReader,
    default_readers,
    prepare_threshold,
    prepare_upscale,
    tesseract_available,
)


def encode(img: Image.Image, fmt: str) -> bytes:
    buf = io.BytesIO()
    img.save(buf, fmt)
    return buf.getvalue()


def picture(w=200, h=100, mode="RGB", color="white"):
    return Image.new(mode, (w, h), color)


# --- type sniffing: by the bytes, never by the name -------------------------


@pytest.mark.parametrize("fmt,expected", [("PNG", "png"), ("JPEG", "jpeg"), ("WEBP", "webp")])
def test_sniff_recognises_png_jpeg_webp(fmt, expected):
    assert sniff_type(encode(picture(), fmt)) == expected


@pytest.mark.parametrize(
    "data",
    [b"", b"hello world", b"%PDF-1.7 ...", b"GIF89a....", b"<svg xmlns='http://www.w3.org/2000/svg'/>", b"MZ\x90\x00", b"RIFFxxxxWAVEfmt "],
)
def test_sniff_rejects_everything_else(data):
    assert sniff_type(data) is None


def test_load_rejects_a_non_image_with_the_type_kind():
    with pytest.raises(ImageError) as e:
        load_image(b"not an image at all")
    assert e.value.kind == "type"


def test_load_rejects_something_too_big_before_decoding():
    with pytest.raises(ImageError) as e:
        load_image(b"\x89PNG\r\n\x1a\n" + b"0" * (imageio.MAX_BYTES + 1))
    assert e.value.kind == "size"


def test_load_rejects_a_decompression_bomb_by_pixel_count():
    big = encode(Image.new("L", (6000, 6000), 255), "PNG")  # tiny file, 36 million pixels
    assert len(big) < imageio.MAX_BYTES
    with pytest.raises(ImageError) as e:
        load_image(big)
    assert e.value.kind == "pixels"


def test_load_rejects_a_truncated_or_corrupt_image():
    good = encode(picture(), "PNG")
    for bad in (good[:30], good[:8] + b"garbage" * 20):
        with pytest.raises(ImageError) as e:
            load_image(bad)
        assert e.value.kind in {"unreadable", "type"}


def test_load_downscales_the_long_side_and_keeps_the_shape():
    img = load_image(encode(Image.new("RGB", (4000, 3000), "white"), "PNG"))
    assert max(img.size) == imageio.OCR_MAX_SIDE
    assert abs(img.size[0] / img.size[1] - 4 / 3) < 0.01


def test_load_leaves_small_images_alone_and_returns_rgb():
    for mode in ("L", "RGBA", "RGB"):
        img = load_image(encode(picture(300, 200, mode), "PNG"))
        assert img.mode == "RGB" and img.size == (300, 200)


def test_loading_writes_nothing_to_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TMP", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    load_image(encode(picture(500, 400), "JPEG"))
    assert list(tmp_path.iterdir()) == []


# --- the two preparations ---------------------------------------------------


def test_threshold_preparation_is_pure_black_and_white_and_same_size():
    img = Image.new("RGB", (120, 80), "white")
    for x in range(30, 60):
        for y in range(20, 40):
            img.putpixel((x, y), (30, 30, 30))
    out = prepare_threshold(img)
    assert out.size == img.size
    assert set(out.convert("L").getdata()) <= {0, 255}
    assert 0 in set(out.convert("L").getdata())


def test_upscale_preparation_doubles_the_size_and_keeps_the_shape():
    out = prepare_upscale(picture(150, 90))
    assert out.size == (300, 180)


def test_the_two_preparations_really_differ():
    img = Image.new("RGB", (100, 60), (200, 200, 200))
    for x in range(20, 40):
        for y in range(10, 30):
            img.putpixel((x, y), (90, 90, 90))
    assert prepare_threshold(img).size != prepare_upscale(img).size


# --- the reader --------------------------------------------------------------


class FakePyt:
    def __init__(self, data):
        self.data = data
        self.seen = None

    def image_to_data(self, image, lang=None, config=None, output_type=None):
        self.seen = (image.size, lang, config)
        return self.data


def reader_with(data, monkeypatch, prep=prepare_upscale):
    fake = FakePyt(data)
    r = TesseractReader("test", prep)
    monkeypatch.setattr("confam_engine.ocr.tesseract._pytesseract", lambda: fake)
    monkeypatch.setattr("confam_engine.ocr.tesseract.tesseract_available", lambda: True)
    return r, fake


def test_reader_normalises_boxes_to_the_image_and_skips_blanks(monkeypatch):
    data = {
        "text": ["Hello", " ", "world", ""],
        "left": [20, 0, 100, 0],
        "top": [10, 0, 10, 0],
        "width": [60, 0, 80, 0],
        "height": [20, 0, 20, 0],
        "conf": ["96", "-1", "91", "-1"],
    }
    r, fake = reader_with(data, monkeypatch)
    reading = r.read(picture(200, 100))  # upscaled to 400x200 for Tesseract
    assert fake.seen[0] == (400, 200) and fake.seen[1] == "eng"
    assert [w.text for w in reading.words] == ["Hello", "world"]
    hello = reading.words[0]
    assert (round(hello.x, 3), round(hello.y, 3), round(hello.w, 3), round(hello.h, 3)) == (0.05, 0.05, 0.15, 0.1)
    assert all(0 <= v <= 1 for w in reading.words for v in (w.x, w.y, w.w, w.h))


def test_reader_clamps_boxes_that_run_past_the_edge(monkeypatch):
    data = {"text": ["edge"], "left": [380], "top": [190], "width": [60], "height": [30], "conf": ["90"]}
    r, _ = reader_with(data, monkeypatch)
    w = r.read(picture(200, 100)).words[0]
    assert w.x + w.w <= 1.0000001 and w.y + w.h <= 1.0000001


def test_a_reading_carries_no_confidence(monkeypatch):
    data = {"text": ["x"], "left": [0], "top": [0], "width": [10], "height": [10], "conf": ["77"]}
    r, _ = reader_with(data, monkeypatch)
    word = r.read(picture(100, 100)).words[0]
    assert not hasattr(word, "conf") and not hasattr(word, "confidence")


def test_reader_says_so_when_tesseract_is_missing(monkeypatch):
    monkeypatch.setattr("confam_engine.ocr.tesseract.tesseract_available", lambda: False)
    with pytest.raises(OcrUnavailable):
        TesseractReader("x", prepare_upscale).read(picture())


def test_default_readers_are_two_different_preparations():
    a, b = default_readers()
    assert a.name != b.name and a.prepare is not b.prepare


def test_tesseract_available_is_a_bool_and_honours_the_env_var(monkeypatch, tmp_path):
    assert isinstance(tesseract_available(), bool)
    fake = tmp_path / ("tesseract.exe" if os.name == "nt" else "tesseract")
    fake.write_text("x")
    monkeypatch.setenv("TESSERACT_CMD", str(fake))
    from confam_engine.ocr.tesseract import find_tesseract

    assert find_tesseract() == str(fake)
