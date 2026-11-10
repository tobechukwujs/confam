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
from .. import evaluate as _ev
from ..evaluate import Outcome, order_changes, visible_diffs
from ..explain import find_conflicts
from ..model import OfficialNotice
from ..supersession import supersession_for
from .boxed import Box, boxed_tokens_conf, union
from .types import Reading

MIN_TOKENS = 3  # fewer words than this is not a readable notice
NEAR = 0.03  # boxes within this distance (of the image) are "the same spot"

# Confidence gate: a change resting on a word read with LESS confidence than this (0-100) in either
# reading is cannot_confirm / unclear, never altered. None switches the gate off.
# 95 is the product owner's decision: a false "altered" on a genuine notice is the worst error we can
# make, and a missed edit only becomes cannot_confirm (never confirmed). The cost, measured on the
# fictional pictures in docs/EVAL.md: far fewer edited pictures are called altered.
# Confidence stays inside the engine: it is never returned, serialised or shown (rule 4).
DEFAULT_MIN_CONFIDENCE: float | None = 95.0
_USE_DEFAULT = object()


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


def _with_boxes(diffs: list[Diff], boxes: list[Box | None], confs: list[float | None]) -> list[Diff]:
    out = []
    for d in diffs:
        a, b = d.old_span
        if b > a:
            box = union([bx for bx in boxes[a:b] if bx is not None])
            known = [c for c in confs[a:b] if c is not None]
        else:  # something missing from the copy: point at the words around the gap
            idx = [i for i in (a - 1, a) if 0 <= i < len(boxes)]
            box = union([boxes[i] for i in idx if boxes[i] is not None])
            known = [confs[i] for i in idx if confs[i] is not None]
        out.append(replace(d, box=box, conf=min(known) if known else None))
    return out


def _per_reading(reading: Reading, record: Sequence[OfficialNotice]):
    tokens, boxes, confs = boxed_tokens_conf(reading)
    return tokens, boxes, confs, find_notice(tokens, record)


def _visible(tokens: list[Token], boxes: list[Box | None], confs: list[float | None], m: Match, record: Sequence[OfficialNotice]):
    # ocr=True: a reading slip (a look-alike mixed into a word) is not a change on a photo
    visible, cropped = visible_diffs(tokens, m, record, ocr=True)
    return _with_boxes(visible, boxes, confs), cropped


def _low(d: Diff, min_conf: float | None) -> bool:
    return min_conf is not None and d.conf is not None and d.conf < min_conf


def _no_match(ta: list[Token], tb: list[Token], record: Sequence[OfficialNotice]) -> Outcome:
    """Neither reading is a copy of a notice. A conflict counts only if BOTH readings find the same
    one; anything else is "not in our record" (never "fake", rule 1)."""
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


def evaluate_readings(
    readings: Sequence[Reading],
    record: Sequence[OfficialNotice],
    min_confidence: float | None | object = _USE_DEFAULT,
    min_alignment: float | None = None,
) -> Outcome:
    if len(readings) < 2:
        raise ValueError("an image needs two independent readings")
    min_conf = DEFAULT_MIN_CONFIDENCE if min_confidence is _USE_DEFAULT else min_confidence
    min_align = _ev.MIN_ALIGNMENT_FOR_ALTERED if min_alignment is None else min_alignment
    ra, rb = readings[0], readings[1]
    ta, ba, ca, ma = _per_reading(ra, record)
    tb, bb, cb, mb = _per_reading(rb, record)

    if len(ta) < MIN_TOKENS and len(tb) < MIN_TOKENS:
        # OCR read no usable text. The only case where unclear has no notice (approved contract change).
        return Outcome("cannot_confirm", reason="unclear")

    if ma is None and mb is None:
        return _no_match(ta, tb, record)

    if ma is None or mb is None or ma.notice.id != mb.notice.id:
        # only one reading found a notice (or they found different ones): not enough to decide
        found = ma or mb
        return Outcome("cannot_confirm", reason="unclear", notice=found.notice)

    da, crop_a = _visible(ta, ba, ca, ma, record)
    db, crop_b = _visible(tb, bb, cb, mb, record)

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
        if _low(d, min_conf) or _low(e, min_conf):
            uncertain = True  # a change on a low-confidence word is never called altered
            continue
        box = union([b for b in (d.box, e.box) if b is not None])
        agreed.append(replace(d, box=box))
    for j, e in enumerate(db):
        if j not in used:
            uncertain = uncertain or _is_fact(e)

    notice = ma.notice
    if agreed:
        # lines up with too little of the notice to be an edit of it: not a copy of it at all
        if min(ma.notice_coverage, mb.notice_coverage) < min_align:
            return _no_match(ta, tb, record)
        return Outcome("altered", notice=notice, changes=order_changes(agreed))
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
    min_confidence: float | None | object = _USE_DEFAULT,
) -> Verdict:
    return verdict_from_outcome(
        evaluate_readings(readings, record, min_confidence), lang=lang, record_as_of=record_as_of, now=now
    )
