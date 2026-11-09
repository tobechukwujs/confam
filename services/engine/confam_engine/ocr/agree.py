"""Two readings, one verdict.

We never judge whether a photo "looks fake". We read its text twice and send it through the same
comparison as pasted text. A difference counts only if BOTH readings show it at the same spot.
A disagreement on a fact (digit, date, money, link, phone, negation) or a look-alike character
is cannot_confirm / unclear: never confirmed and never called altered. A disagreement about an
ordinary word is reading noise and is ignored.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from confam_contract.verdict import Verdict

from ..check import verdict_from_outcome
from ..compare.diff import Diff, diff_tokens
from ..compare.match import Match, find_notice
from ..compare.tokenize import Token
from ..evaluate import Outcome, _outside_the_visible_slice, _unlisted, _allow_list
from ..explain import find_conflicts
from ..model import OfficialNotice
from ..supersession import supersession_for
from .boxed import Box, boxed_tokens, union
from .types import Reading

MIN_TOKENS = 3  # fewer words than this is not a readable notice
NEAR = 0.03  # boxes within this distance (of the image) are "the same spot"


def _near(a: Box | None, b: Box | None) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return not (
        a[0] > b[0] + b[2] + NEAR
        or b[0] > a[0] + a[2] + NEAR
        or a[1] > b[1] + b[3] + NEAR
        or b[1] > a[1] + a[3] + NEAR
    )


def _norm(s: str | None) -> str:
    return re.sub(r"\s+", " ", s or "").strip().casefold()


def _is_fact(d: Diff) -> bool:
    return d.kind != "text" or bool(re.search(r"\d", (d.copy or "") + (d.official or "")))


def _with_boxes(diffs: list[Diff], boxes: list[Box | None]) -> list[Diff]:
    out = []
    for d in diffs:
        a, b = d.old_span
        if b > a:
            box = union([bx for bx in boxes[a:b] if bx is not None])
        else:  # something missing from the copy: point at the words around the gap
            near = [bx for bx in (boxes[a - 1] if a - 1 >= 0 else None, boxes[a] if a < len(boxes) else None) if bx]
            box = union(near)
        out.append(replace(d, box=box))
    return out


def _per_reading(reading: Reading, record: Sequence[OfficialNotice]):
    tokens, boxes = boxed_tokens(reading)
    return tokens, boxes, find_notice(tokens, record)


def _visible(tokens: list[Token], boxes: list[Box | None], m: Match, allowed: set[str]):
    diffs = diff_tokens(tokens, m.tokens)
    cropped = [d for d in diffs if _outside_the_visible_slice(d, m)]
    visible = [d for d in diffs if d not in cropped]
    visible = _with_boxes(visible, boxes)
    extra = _with_boxes(_unlisted(tokens, allowed, visible), boxes)
    return visible + extra, bool(cropped)


def evaluate_readings(readings: Sequence[Reading], record: Sequence[OfficialNotice]) -> Outcome:
    if len(readings) < 2:
        raise ValueError("an image needs two independent readings")
    ra, rb = readings[0], readings[1]
    ta, ba, ma = _per_reading(ra, record)
    tb, bb, mb = _per_reading(rb, record)

    if len(ta) < MIN_TOKENS and len(tb) < MIN_TOKENS:
        return Outcome("cannot_confirm", reason="no_fact")  # nothing readable to check

    if ma is None and mb is None:
        # no notice in either reading: a conflict counts only if both readings find the same one
        fa, fb = find_conflicts(ta, record), find_conflicts(tb, record)
        if fa and fb and fa[0].id == fb[0].id:
            key = lambda cs: {(c["kind"], c["copy"].casefold(), c["official"].casefold()) for c in cs}
            shared = key(fa[1]) & key(fb[1])
            kept = [c for c in fa[1] if (c["kind"], c["copy"].casefold(), c["official"].casefold()) in shared]
            if kept:
                return Outcome("not_official", notice=fa[0], conflicts=kept)
        if not any(t.meaningful for t in ta + tb):
            return Outcome("cannot_confirm", reason="no_fact")
        return Outcome("cannot_confirm", reason="not_in_record")

    if ma is None or mb is None or ma.notice.id != mb.notice.id:
        # only one reading found a notice (or they found different ones): not enough to decide
        found = ma or mb
        return Outcome("cannot_confirm", reason="unclear", notice=found.notice)

    allowed = _allow_list(record)
    da, crop_a = _visible(ta, ba, ma, allowed)
    db, crop_b = _visible(tb, bb, mb, allowed)

    agreed: list[Diff] = []
    uncertain = False
    used: set[int] = set()
    for d in da:
        hit = next(
            (
                j
                for j, e in enumerate(db)
                if j not in used
                and (e.op, e.kind, _norm(e.official), _norm(e.copy)) == (d.op, d.kind, _norm(d.official), _norm(d.copy))
                and _near(d.box, e.box)
            ),
            None,
        )
        if hit is None:
            uncertain = uncertain or _is_fact(d)  # an ordinary-word slip is noise, even a look-alike one
            continue
        used.add(hit)
        e = db[hit]
        if d.lookalike or e.lookalike:
            uncertain = True
            continue
        box = union([b for b in (d.box, e.box) if b is not None])
        agreed.append(replace(d, box=box))
    for j, e in enumerate(db):
        if j not in used:
            uncertain = uncertain or _is_fact(e)

    notice = ma.notice
    if agreed:
        agreed.sort(key=lambda x: (x.old_span[0], x.new_span[0]))
        return Outcome("altered", notice=notice, changes=agreed)
    if uncertain:
        return Outcome("cannot_confirm", reason="unclear", notice=notice)
    if crop_a and crop_b:
        return Outcome("partial", notice=notice)
    return Outcome("confirmed", notice=notice, superseded_by=supersession_for(notice, record))


def check_readings(
    readings: Sequence[Reading],
    record: Sequence[OfficialNotice],
    *,
    record_as_of: datetime,
    lang: str = "en",
    now: datetime | None = None,
) -> Verdict:
    return verdict_from_outcome(
        evaluate_readings(readings, record), lang=lang, record_as_of=record_as_of, now=now
    )
