"""Step 3: find the notice a copy is a copy of.

A copy matches a notice when most of the copy is explained by it. The numbers below are
internal thresholds. They are never shown to a user and never appear in any output (rule 4).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher

from ..model import OfficialNotice
from .tokenize import Token, tokenize

MIN_MATCHED_TOKENS = 5  # a few shared words never make a match
MIN_COPY_COVERAGE = 0.7  # share of the copy that the notice explains


@dataclass(frozen=True)
class Match:
    notice: OfficialNotice
    tokens: list[Token]  # the notice's tokens
    matched: int
    first: int  # first official token the copy covers
    last: int  # one past the last official token the copy covers
    copy_coverage: float  # matched / copy tokens
    notice_coverage: float  # matched / notice tokens


def _score(copy: list[Token], notice: OfficialNotice) -> Match:
    tokens = tokenize(notice.text)
    sm = SequenceMatcher(None, [t.cmp_key for t in copy], [t.cmp_key for t in tokens], autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
    matched = sum(b.size for b in blocks)
    first = blocks[0].b if blocks else 0
    last = blocks[-1].b + blocks[-1].size if blocks else 0
    return Match(
        notice=notice,
        tokens=tokens,
        matched=matched,
        first=first,
        last=last,
        copy_coverage=matched / len(copy) if copy else 0.0,
        notice_coverage=matched / len(tokens) if tokens else 0.0,
    )


def find_notice(copy: list[Token], record: Sequence[OfficialNotice]) -> Match | None:
    """The best notice for this copy, or None. Ties go to the one the copy covers most."""
    best: Match | None = None
    for notice in record:
        m = _score(copy, notice)
        if m.matched < MIN_MATCHED_TOKENS or m.copy_coverage < MIN_COPY_COVERAGE:
            continue
        if best is None or (m.copy_coverage, m.notice_coverage) > (best.copy_coverage, best.notice_coverage):
            best = m
    return best
