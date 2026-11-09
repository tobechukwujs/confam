"""One-detail edits of a notice: the changes a forger makes. Every kind of fact gets changed in
turn, plus structural edits. Deterministic.

Each edit says what verdict set is correct:
  altered           a definite change inside the notice
  cannot_confirm    a look-alike character (cannot be called an edit or a reading slip)
  partial/altered   the last sentence was dropped (a cut-off ending and an edit look alike)
Nothing here is ever correct as `confirmed`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from confam_engine.compare import tokenize

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SWAPS = {
    "free": "paid", "open": "closed", "closes": "opens", "announces": "denies", "returned": "kept",
    "accepted": "required", "within": "after", "confirms": "denies", "collected": "discarded",
    "published": "withheld", "costs": "pays",
}
LOOKALIKE = {"0": "O", "8": "B", "1": "l", "5": "S", "2": "Z", "6": "G"}


@dataclass(frozen=True)
class Edit:
    kind: str
    text: str
    expected: frozenset[str]


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def _replace(text: str, start: int, end: int, new: str) -> str:
    return text[:start] + new + text[end:]


def _bump_digits(s: str) -> str:
    """Change the last digit (up, wrapping 9 to 8) so the value really changes."""
    for i in range(len(s) - 1, -1, -1):
        if s[i].isdigit():
            d = int(s[i])
            return s[:i] + str(d + 1 if d < 9 else 8) + s[i + 1 :]
    return s


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def edits_for(text: str) -> list[Edit]:
    out: list[Edit] = []
    altered = frozenset({"altered"})
    tokens = tokenize(text)

    for t in tokens:
        raw = text[t.start : t.end]
        if t.kind == "date":
            m = re.match(r"(\d{1,2})(?:st|nd|rd|th)?(\s+(?:of\s+)?)([A-Za-z]+)", raw)
            if m:
                day = int(m[1])
                out.append(Edit("date_day", _replace(text, t.start, t.end, raw.replace(m[0], f"{_ordinal(day % 28 + 1)}{m[2]}{m[3]}", 1)), altered))
                nxt = MONTHS[(MONTHS.index(m[3]) + 1) % 12] if m[3] in MONTHS else None
                if nxt:
                    out.append(Edit("date_month", _replace(text, t.start, t.end, raw.replace(m[3], nxt, 1)), altered))
        elif t.kind == "time":
            m = re.match(r"(\d{1,2})(:\d{2})?(\s?(?:am|pm))?", raw, re.I)
            if m:
                hour = int(m[1]) % 12 + 1
                out.append(Edit("time", _replace(text, t.start, t.end, f"{hour}{m[2] or ''}{m[3] or ''}"), altered))
        elif t.kind == "weekday":
            if raw in WEEKDAYS:
                out.append(Edit("weekday", _replace(text, t.start, t.end, WEEKDAYS[(WEEKDAYS.index(raw) + 1) % 7]), altered))
        elif t.kind == "number":
            out.append(Edit("number", _replace(text, t.start, t.end, _bump_digits(raw)), altered))
        elif t.kind == "money":
            out.append(Edit("money", _replace(text, t.start, t.end, _bump_digits(raw)), altered))
        elif t.kind == "phone":
            out.append(Edit("phone", _replace(text, t.start, t.end, _bump_digits(raw)), altered))
        elif t.kind == "link":
            out.append(Edit("link_host", _replace(text, t.start, t.end, raw.replace(".sec.", "-sec.", 1)), altered))
            if raw.startswith("https://"):
                out.append(Edit("link_scheme", _replace(text, t.start, t.end, "http://" + raw[8:]), altered))
            out.append(Edit("link_path", _replace(text, t.start, t.end, raw + "/claim"), altered))
        elif t.kind == "negation":
            out.append(Edit("negation_removed", _replace(text, t.start, t.end, "").replace("  ", " "), altered))

        # look-alike swap inside any fact that has a digit or a letter we can confuse
        if t.kind in {"date", "number", "phone", "money", "time"}:
            for i, ch in enumerate(raw):
                if ch in LOOKALIKE:
                    out.append(Edit("lookalike_digit", _replace(text, t.start + i, t.start + i + 1, LOOKALIKE[ch]), frozenset({"cannot_confirm"})))
                    break
        if t.kind == "link":
            host = raw.split("//", 1)[-1]
            for i, ch in enumerate(host):
                if ch == "i" or ch == "l":
                    pos = t.end - len(host) + i
                    out.append(Edit("lookalike_link", _replace(text, pos, pos + 1, "1"), frozenset({"cannot_confirm"})))
                    break

    # ordinary words: swap a meaningful word for its opposite
    for word, other in SWAPS.items():
        m = re.search(rf"\b{word}\b", text)
        if m:
            out.append(Edit(f"word_{word}", _replace(text, m.start(), m.end(), other), altered))

    # structure
    sentences = _sentences(text)
    if len(sentences) >= 2:
        extra = "Pay N500 to your ward officer first."
        out.append(Edit("inserted_sentence_money", " ".join([sentences[0], extra] + sentences[1:]), altered))
        out.append(Edit("inserted_sentence_words", " ".join([sentences[0], "Registration may be refused without notice."] + sentences[1:]), altered))
        out.append(Edit("dropped_last_sentence", " ".join(sentences[:-1]), frozenset({"partial", "altered"})))
    if len(sentences) >= 3:
        out.append(Edit("dropped_middle_sentence", " ".join([sentences[0]] + sentences[2:]), altered))
    out.append(Edit("appended_link", text + " Register faster at https://fast-register.example", altered))
    out.append(Edit("appended_phone", text + " Call 08031234567 to complete this.", altered))

    # drop any edit that is not actually different from the original (an ordinal suffix, for example)
    key = lambda s: [t.cmp_key for t in tokenize(s)]
    return [e for e in out if key(e.text) != key(text)]
