"""Tesseract readers: two passes with different preparations of the same picture.

Pass 1: grey, stretched contrast, hard black-and-white threshold.
Pass 2: grey, enlarged 2x, sharpened. No threshold, so faint strokes survive.

A change counts only if both passes show it (see agree.py). Reading confidence is used by
nothing and returned by nothing (rule 4). Nothing is written to disk (rule 7): Tesseract is
given the in-memory image.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from .types import Reading, Word

WINDOWS_DEFAULT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
MAX_OCR_SIDE = 2400  # the most pixels on the long side Tesseract is ever given


class OcrUnavailable(RuntimeError):
    """Tesseract is not installed on this machine."""


def find_tesseract() -> str | None:
    env = os.environ.get("TESSERACT_CMD")
    if env and Path(env).exists():
        return env
    found = shutil.which("tesseract")
    if found:
        return found
    if os.name == "nt" and Path(WINDOWS_DEFAULT).exists():
        return WINDOWS_DEFAULT
    return None


def tesseract_available() -> bool:
    return find_tesseract() is not None


def _pytesseract():
    import pytesseract

    path = find_tesseract()
    if path:
        pytesseract.pytesseract.tesseract_cmd = path
    return pytesseract


def _otsu(gray: Image.Image) -> int:
    """Pick the black/white cut-off that best separates ink from paper (Otsu), pure Python."""
    hist = gray.histogram()
    total = sum(hist)
    sum_all = sum(i * h for i, h in enumerate(hist))
    best, best_t, w0, sum0 = -1.0, 128, 0, 0.0
    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break
        sum0 += t * hist[t]
        m0, m1 = sum0 / w0, (sum_all - sum0) / w1
        between = w0 * w1 * (m0 - m1) ** 2
        if between > best:
            best, best_t = between, t
    return best_t


def prepare_threshold(img: Image.Image) -> Image.Image:
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    cut = _otsu(gray)
    return gray.point(lambda v: 255 if v > cut else 0)


def prepare_upscale(img: Image.Image) -> Image.Image:
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    factor = min(2.0, MAX_OCR_SIDE / max(gray.size))  # 2x, but never more than MAX_OCR_SIDE px (memory)
    big = gray.resize((round(gray.width * factor), round(gray.height * factor)), Image.LANCZOS)
    return big.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))


class TesseractReader:
    def __init__(self, name: str, prepare: Callable[[Image.Image], Image.Image]) -> None:
        self.name = name
        self.prepare = prepare

    def read(self, image: Image.Image) -> Reading:
        if not tesseract_available():
            raise OcrUnavailable("Tesseract is not installed")
        prepared = self.prepare(image)
        width, height = prepared.size
        data = _pytesseract().image_to_data(
            prepared, lang="eng", config="--psm 6", output_type="dict"
        )
        words: list[Word] = []
        for i, text in enumerate(data["text"]):
            if not str(text).strip():
                continue
            if str(data["conf"][i]) == "-1":
                continue
            x0 = max(0.0, data["left"][i] / width)
            y0 = max(0.0, data["top"][i] / height)
            x1 = min(1.0, (data["left"][i] + data["width"][i]) / width)
            y1 = min(1.0, (data["top"][i] + data["height"][i]) / height)
            words.append(Word(str(text).strip(), x0, y0, max(0.0, x1 - x0), max(0.0, y1 - y0)))
        return Reading(words)


def default_readers() -> tuple[TesseractReader, TesseractReader]:
    """Two independent readings. A second engine (Azure AI Vision Read) can replace either."""
    return (
        TesseractReader("tesseract-threshold", prepare_threshold),
        TesseractReader("tesseract-upscale", prepare_upscale),
    )
