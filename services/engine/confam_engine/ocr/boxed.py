"""Turn a reading into tokens that know where they sit on the photo."""

from __future__ import annotations

from ..compare.tokenize import Token, tokenize
from .types import Reading

Box = tuple[float, float, float, float]


def union(boxes: list[Box]) -> Box | None:
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    x0, y0 = max(0.0, x0), max(0.0, y0)
    x1, y1 = min(1.0, x1), min(1.0, y1)
    return (x0, y0, max(0.0, x1 - x0), max(0.0, y1 - y0))


def boxed_tokens(reading: Reading) -> tuple[list[Token], list[Box | None]]:
    """Tokens of the reading's text, and for each token the box of the word(s) it came from."""
    text_parts: list[str] = []
    spans: list[tuple[int, int, Box]] = []
    pos = 0
    for word in reading.words:
        if not word.text.strip():
            continue
        start = pos
        text_parts.append(word.text)
        pos += len(word.text)
        spans.append((start, pos, (word.x, word.y, word.w, word.h)))
        text_parts.append(" ")
        pos += 1
    text = "".join(text_parts)
    tokens = tokenize(text)
    boxes: list[Box | None] = []
    for t in tokens:
        hits = [b for a, z, b in spans if a < t.end and z > t.start]
        boxes.append(union(hits))
    return tokens, boxes
