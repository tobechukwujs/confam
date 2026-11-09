"""Split text into tokens with an entity kind and a normalised key.

Kinds: date, time, weekday, number, money, link, phone, negation, text. Two tokens
"say the same thing" when kind and key are equal, so "14th November" and
"November 14" match, and "N500" and "500 naira" match.

Offsets are into the NFC-normalised text (tone marks stay attached to their letters).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal

from .lexicon import MONTHS, NEGATIONS, WEEKDAYS

MEANINGFUL = {"date", "time", "weekday", "number", "money", "link", "phone", "negation"}

_MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec)\b\.?"
_DAY = r"\d{1,2}(?:st|nd|rd|th)?"

_LINK = r"(?:https?://|www\.)[^\s<>\"']+"
_PHONE = r"(?<![\d.])(?:\+?234|0)[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{4}(?!\d)"
_MONEY = (
    r"(?:(?:₦|NGN\s?|(?<![A-Za-z])N(?=\d))\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:million|billion|bn|m|k)\b)?"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:naira|kobo)\b)"
)
_DATE = (
    rf"(?:\b{_DAY}(?:\s+of)?\s+{_MONTH}(?:,?\s+\d{{4}}\b)?"
    rf"|\b{_MONTH}\s+{_DAY}\b(?:,?\s+\d{{4}}\b)?"
    r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b)"
)
_TIME = r"(?:\b\d{1,2}:\d{2}\s?(?:am|pm)?\b|\b\d{1,2}\s?(?:am|pm)\b)"
_NUMBER = r"\d[\d,]*(?:\.\d+)?(?:st|nd|rd|th)?"
# Letters plus combining marks, so Yoruba and Igbo tone marks never split a word.
_WORD = r"(?:[^\W\d_]|[̀-ͯ])+(?:['’](?:[^\W\d_]|[̀-ͯ])+)*"

_MASTER = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in (
            ("link", _LINK),
            ("phone", _PHONE),
            ("money", _MONEY),
            ("date", _DATE),
            ("time", _TIME),
            ("number", _NUMBER),
            ("word", _WORD),
        )
    ),
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Token:
    text: str
    kind: str
    key: str
    start: int
    end: int

    @property
    def meaningful(self) -> bool:
        return self.kind in MEANINGFUL

    @property
    def cmp_key(self) -> str:
        return f"{self.kind}:{self.key}"


def _straight(s: str) -> str:
    return s.replace("’", "'").replace("‘", "'")


def _date_key(text: str) -> str:
    t = text.casefold()
    num = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", t)
    if num:  # day/month/year, as written in Nigeria
        d, m, y = int(num[1]), int(num[2]), int(num[3])
        return f"{y + 2000 if y < 100 else y}-{m:02d}-{d:02d}"
    month = next((MONTHS[w] for w in re.findall(r"[a-z]+", t) if w in MONTHS), 0)
    digits = re.findall(r"\d+", t)
    day = next((int(d) for d in digits if len(d) <= 2), 0)
    year = next((d for d in digits if len(d) == 4), "")
    return f"{year + '-' if year else ''}{month:02d}-{day:02d}"


def _time_key(text: str) -> str:
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s?(am|pm)?", text.casefold())
    if not m:
        return text.casefold()
    hour, minute, ampm = int(m[1]), int(m[2] or 0), m[3]
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


_MULT = {"k": Decimal(1_000), "m": Decimal(1_000_000), "million": Decimal(1_000_000),
         "bn": Decimal(1_000_000_000), "billion": Decimal(1_000_000_000)}


def _money_key(text: str) -> str:
    t = text.casefold()
    m = re.search(r"\d[\d,]*(?:\.\d+)?", t)
    amount = Decimal(m[0].replace(",", "")) if m else Decimal(0)
    word = re.search(r"(million|billion|bn|k|m|kobo)\s*$", t)
    if word:
        amount = amount / 100 if word[1] == "kobo" else amount * _MULT[word[1]]
    return f"NGN{amount.normalize():f}"


def _phone_key(text: str) -> str:
    digits = re.sub(r"\D", "", text)
    return "0" + digits[3:] if digits.startswith("234") else digits


def _link_key(text: str) -> str:
    t = text.strip()
    scheme = "https"
    if t.lower().startswith("http://"):
        scheme, t = "http", t[7:]
    elif t.lower().startswith("https://"):
        t = t[8:]
    host, _, path = t.partition("/")
    host = host.lower().removeprefix("www.")
    return f"{scheme}://{host}/{path}".rstrip("/")


def _key(kind: str, text: str) -> str:
    if kind == "date":
        return _date_key(text)
    if kind == "time":
        return _time_key(text)
    if kind == "money":
        return _money_key(text)
    if kind == "phone":
        return _phone_key(text)
    if kind == "link":
        return _link_key(text)
    if kind == "number":
        return re.sub(r"(st|nd|rd|th)$", "", text.casefold().replace(",", ""))
    return _straight(text).casefold()


def tokenize(text: str) -> list[Token]:
    text = unicodedata.normalize("NFC", text)
    out: list[Token] = []
    for m in _MASTER.finditer(text):
        kind = m.lastgroup or "word"
        start, end = m.span()
        raw = m.group()
        if kind == "link":  # trailing sentence punctuation is not part of the address
            stripped = raw.rstrip(".,;:)!?")
            end -= len(raw) - len(stripped)
            raw = stripped
        elif kind in ("number", "money"):
            stripped = raw.rstrip(",")
            end -= len(raw) - len(stripped)
            raw = stripped
        elif kind == "date":
            stripped = raw.rstrip(".")
            end -= len(raw) - len(stripped)
            raw = stripped
        if kind == "word":
            low = _straight(raw).casefold()
            if low in WEEKDAYS:
                kind = "weekday"
            elif low in NEGATIONS:
                kind = "negation"
            else:
                kind = "text"
        out.append(Token(text=raw, kind=kind, key=_key(kind, raw), start=start, end=end))
    return out
