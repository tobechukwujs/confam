"""Load an uploaded image safely, in memory only (rule 7).

The type is decided by the bytes, never by the file name. Nothing is written to disk. A tiny
file that expands to a huge picture is refused by pixel count before it is decoded.
"""

from __future__ import annotations

import io

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 5 * 1024 * 1024  # about 5 MB
MAX_PIXELS = 25_000_000  # refuses decompression bombs
OCR_MAX_SIDE = 1600  # long side we read at; bigger pictures are shrunk first (keeps memory low on a 512 MB host)


class ImageError(ValueError):
    """kind: type (not PNG/JPEG/WebP), size (too many bytes), pixels (too big), unreadable."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


def sniff_type(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def probe_image(data: bytes) -> None:
    """Cheap checks done before accepting a picture: size, real type, and pixel count read from
    the header only (nothing is decoded). Raises ImageError."""
    if len(data) > MAX_BYTES:
        raise ImageError("size", "That picture is too big.")
    if sniff_type(data) is None:
        raise ImageError("type", "That file is not a PNG, JPEG or WebP picture.")
    try:
        with Image.open(io.BytesIO(data)) as probe:
            if probe.width * probe.height > MAX_PIXELS:
                raise ImageError("pixels", "That picture has too many pixels.")
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ImageError("unreadable", "That picture could not be read.") from exc


def load_image(data: bytes) -> Image.Image:
    probe_image(data)
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ImageError("unreadable", "That picture could not be read.") from exc
    img = ImageOps.exif_transpose(img).convert("RGB")
    longest = max(img.size)
    if longest > OCR_MAX_SIDE:
        scale = OCR_MAX_SIDE / longest
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    return img