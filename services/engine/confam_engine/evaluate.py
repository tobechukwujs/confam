"""Steps 3-8 of the pipeline for text: find the notice, compare, apply the meaning rules,
check links and numbers against the record, and explain when nothing matches.

Rules decide the verdict (rule 3). Nothing here returns a score (rule 4). The order of
precedence when a copy matches a notice:

    altered    a definite difference in the visible text
    unclear    only look-alike differences (never confirmed, never called altered)
    partial    the visible part matches but the head or tail of the notice is missing
    confirmed  nothing differs
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .compare.diff import Diff, diff_tokens
from .compare.match import Match, find_notice
from .compare.tokenize import Token, tokenize
from .explain import find_conflicts
from .model import OfficialNotice
from .supersession import supersession_for


@dataclass
class Outcome:
    verdict: str  # confirmed | altered | not_official | partial | cannot_confirm
    reason: str | None = None  # unclear | not_in_record | no_fact | line_missing
    notice: OfficialNotice | None = None
    changes: list[Diff] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    superseded_by: dict | None = None


def _allow_list(record: Sequence[OfficialNotice]) -> set[str]:
    """Every web address and phone number that appears in the signed record."""
    return {
        t.key
        for n in record
        for t in tokenize(n.text)
        if t.kind in ("link", "phone")
    }


def _outside_the_visible_slice(d: Diff, m: Match) -> bool:
    """A missing run of the official text at the very start or end: the copy is cropped."""
    if d.op != "delete":
        return False
    a, b = d.new_span
    return b <= m.first or a >= m.last


def _unlisted(copy: list[Token], allowed: set[str], diffs: list[Diff]) -> list[Diff]:
    """Links and phone numbers in the copy that are not in the record and not already reported."""
    reported = {d.copy for d in diffs if d.copy}
    out = []
    for i, t in enumerate(copy):
        if t.kind in ("link", "phone") and t.key not in allowed and t.text not in reported:
            out.append(Diff("insert", t.kind, None, t.text, (i, i + 1), (0, 0)))
    return out


def _compare(copy: list[Token], m: Match, record: Sequence[OfficialNotice]) -> Outcome:
    diffs = diff_tokens(copy, m.tokens)
    cropped = [d for d in diffs if _outside_the_visible_slice(d, m)]
    visible = [d for d in diffs if d not in cropped]

    definite = [d for d in visible if not d.lookalike]
    uncertain = [d for d in visible if d.lookalike]
    definite += _unlisted(copy, _allow_list(record), definite + uncertain)

    if definite:
        definite.sort(key=lambda d: (d.old_span[0], d.new_span[0]))
        return Outcome("altered", notice=m.notice, changes=definite)
    if uncertain:
        return Outcome("cannot_confirm", reason="unclear", notice=m.notice)
    if cropped:
        return Outcome("partial", notice=m.notice)
    return Outcome("confirmed", notice=m.notice, superseded_by=supersession_for(m.notice, record))


def evaluate(text: str, record: Sequence[OfficialNotice]) -> Outcome:
    copy = tokenize(text)
    if not copy:
        return Outcome("cannot_confirm", reason="no_fact")

    match = find_notice(copy, record)
    if match is not None:
        return _compare(copy, match, record)

    # Nothing matched. A contradicted official fact is `not_official`; anything else is
    # "not in our record", which is never "fake" (rule 1).
    found = find_conflicts(copy, record)
    if found is not None:
        notice, conflicts = found
        return Outcome("not_official", notice=notice, conflicts=conflicts)
    if not any(t.meaningful for t in copy):
        return Outcome("cannot_confirm", reason="no_fact")
    return Outcome("cannot_confirm", reason="not_in_record")
