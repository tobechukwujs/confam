"""Look-alike characters. A difference that is only a look-alike swap (0/O, 1/l/I/i, 5/S, 8/B,
2/Z, 6/G, rn/m, vv/w, cl/d) cannot be called a real edit or a reading slip, so the engine
reports cannot_confirm / unclear for it. It is never confirmed and never called altered.

The set is deliberately generous: wrongly saying "unclear" only withholds a verdict, while
wrongly saying "confirmed" would let a forged copy through."""

from __future__ import annotations

import re
import unicodedata

_SINGLE = str.maketrans({"0": "o", "1": "l", "i": "l", "|": "l", "5": "s", "8": "b", "2": "z", "6": "g"})
_MULTI = (("rn", "m"), ("vv", "w"), ("cl", "d"))


def fold(text: str) -> str:
    """Collapse look-alike characters to one form. Spaces are ignored."""
    s = unicodedata.normalize("NFC", text).replace("I", "l")  # capital i looks like a lowercase L
    s = re.sub(r"\s+", "", s).casefold().translate(_SINGLE)
    for a, b in _MULTI:
        s = s.replace(a, b)
    return s


def is_lookalike(copy_text: str, official_text: str) -> bool:
    """True when the two differ, but only by look-alike characters."""
    a = re.sub(r"\s+", "", copy_text).casefold()
    b = re.sub(r"\s+", "", official_text).casefold()
    return a != b and fold(copy_text) == fold(official_text)
