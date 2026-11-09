"""Step 8: the copy matched no notice. Look for an official fact it contradicts.

`not_official` needs a contradicted official fact: the copy shares the notice's subject and
states a DIFFERENT date, money amount or link for the SAME thing the notice talks about.
Anything weaker is `not_in_record`, which is never "fake" (rule 1).
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from .compare.tokenize import Token, normalize_space, tokenize
from .model import OfficialNotice

CONFLICT_KINDS = ("date", "money", "link")
MIN_SHARED_SUBJECT_WORDS = 2
CONTEXT_WORDS = 3

_STOP = {
    "a", "an", "the", "on", "at", "in", "of", "to", "is", "are", "be", "by", "for", "and", "or",
    "only", "now", "will", "must", "please", "your", "you", "this", "that", "with", "from", "as",
    "it", "its", "we", "our", "all", "any", "can", "has", "have", "before", "after", "new", "urgent",
    "citizens", "announces", "confirms",
}
_ORG = {"simulated", "electoral", "commission"}


def _stem(word: str) -> str:
    return word.casefold()[:6]


def _content_stems(tokens: list[Token], skip_org: bool = False) -> set[str]:
    out = set()
    for t in tokens:
        w = t.text.casefold()
        if t.kind == "text" and w not in _STOP and not (skip_org and w in _ORG):
            out.add(_stem(w))
    return out


def _context(tokens: list[Token], index: int) -> set[str]:
    """Stems of the few ordinary words just before a token: what the fact is about."""
    words: list[str] = []
    for t in reversed(tokens[:index]):
        if t.kind == "text":
            if t.text.casefold() not in _STOP:
                words.append(_stem(t.text))
            if len(words) == CONTEXT_WORDS:
                break
        elif t.kind in CONFLICT_KINDS:
            break
    return set(words)


def _sentence(text: str, start: int) -> str:
    """The sentence of `text` that contains character offset `start`, trimmed.

    A full stop ends a sentence only when whitespace or the end follows it, so the dots
    inside a web address ("register.sec.example") never split a quote."""
    begin = 0
    for m in re.finditer(r"[.!?](?=\s|$)", text):
        if start < m.end():
            return text[begin : m.end()].strip()
        begin = m.end()
    return text[begin:].strip()


def find_conflicts(copy: list[Token], record: Sequence[OfficialNotice]) -> tuple[OfficialNotice, list[dict]] | None:
    """(notice, conflicts) for the first current notice the copy contradicts, else None."""
    copy_stems = _content_stems(copy)
    for notice in record:
        if notice.superseded_by is not None:
            continue  # a replaced notice is no longer the truth
        official = tokenize(notice.text)
        subject = _content_stems(tokenize(notice.title), skip_org=True)
        if len(copy_stems & subject) < MIN_SHARED_SUBJECT_WORDS:
            continue
        conflicts: list[dict] = []
        for kind in CONFLICT_KINDS:
            official_of_kind = [(i, t) for i, t in enumerate(official) if t.kind == kind]
            if not official_of_kind:
                continue
            known = {t.key for _, t in official_of_kind}
            for ci, c in enumerate(copy):
                if c.kind != kind or c.key in known:
                    continue
                c_ctx = _context(copy, ci)
                for oi, o in official_of_kind:
                    if c_ctx & _context(official, oi):  # same thing, different value
                        conflicts.append(
                            {
                                "kind": kind,
                                "copy": c.text,
                                "official": o.text,
                                "quote": _sentence(normalize_space(notice.text), o.start),
                            }
                        )
                        break
                if conflicts and conflicts[-1]["kind"] == kind:
                    break  # one conflict per kind is enough to say what differs
        if conflicts:
            return notice, conflicts
    return None
