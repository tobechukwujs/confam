from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Word:
    """One word read from a photo. The box is x, y, width, height, each 0 to 1 of the image.

    No confidence is kept here: reading confidence is never shown to a user (rule 4)."""

    text: str
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Reading:
    """What one reading pass saw: words in reading order."""

    words: list[Word] = field(default_factory=list)


class Reader(Protocol):
    """A reading pass. Two independent readers give the two readings that must agree.

    Tesseract with two different preparations is the first pair. A second engine (for example
    Azure AI Vision Read) can be the second reader later: implement `read` and pass it in.
    The image is a Pillow image held in memory; readers must not write it anywhere (rule 7)."""

    name: str

    def read(self, image) -> Reading: ...
