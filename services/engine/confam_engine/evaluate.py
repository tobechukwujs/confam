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


# What a forger adds around a genuine notice. A wrapper (text outside the aligned notice) is
# ignored EXCEPT for these: a web address or money amount that is not in the record, and, after
# the notice, a phone number that is not in the record. A sender's number sits at the head of a
# forward, so a phone at the head is not a payload.
_PAYLOAD_HEAD = {"link", "money"}
_PAYLOAD_TAIL = {"link", "money", "phone"}


def _payload_keys(m: Match, record: Sequence[OfficialNotice]) -> set[str]:
    """Links, phones and money amounts that belong to this notice or to the signed record."""
    keys = {t.cmp_key for t in m.tokens if t.kind in ("link", "phone", "money")}
    for n in record:
        keys |= {t.cmp_key for t in tokenize(n.text) if t.kind in ("link", "phone")}
    return keys


def _is_wrapper_noise(d: Diff, allowed: set[str]) -> bool:
    """True for copy-only text at the very start or end of the copy that is not a payload."""
    if d.edge is None:
        return False
    payload = _PAYLOAD_HEAD if d.edge == "head" else _PAYLOAD_TAIL
    if d.kind not in payload:
        return True
    tokens = tokenize(d.copy or "")
    if len(tokens) == 1 and tokens[0].kind == d.kind and tokens[0].cmp_key in allowed:
        return True  # a link the record already has is not new
    return False


def _unlisted(copy: list[Token], allowed: set[str], diffs: list[Diff], skip: set[int]) -> list[Diff]:
    """Links and phone numbers in the copy that are not in the record and not already reported.
    Phone numbers in the head wrapper (`skip`) are a sender's number, not a claim."""
    reported = {d.copy for d in diffs if d.copy}
    out = []
    for i, t in enumerate(copy):
        if t.kind == "phone" and i in skip:
            continue
        if t.kind in ("link", "phone") and t.key not in allowed and t.text not in reported:
            out.append(Diff("insert", t.kind, None, t.text, (i, i + 1), (0, 0)))
    return out


def visible_diffs(copy: list[Token], m: Match, record: Sequence[OfficialNotice]) -> tuple[list[Diff], bool]:
    """Differences between the copy and the matched notice that COUNT, and whether the copy is
    cropped. The copy is aligned to the notice: wrapper text outside it is ignored, a missing head
    or tail of the notice means cropped, and everything inside the notice counts."""
    diffs = diff_tokens(copy, m.tokens)
    cropped = [d for d in diffs if _outside_the_visible_slice(d, m)]
    inside = [d for d in diffs if d not in cropped]
    head = {i for d in inside if d.edge == "head" for i in range(*d.old_span)}
    allowed = _payload_keys(m, record)
    kept = [d for d in inside if not _is_wrapper_noise(d, allowed)]
    kept += _unlisted(copy, _allow_list(record), kept, head)
    return kept, bool(cropped)


def _compare(copy: list[Token], m: Match, record: Sequence[OfficialNotice]) -> Outcome:
    visible, cropped = visible_diffs(copy, m, record)
    definite = [d for d in visible if not d.lookalike]
    uncertain = [d for d in visible if d.lookalike]

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
