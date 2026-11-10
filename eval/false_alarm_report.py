"""Honest pictures that are still called `altered` at a given confidence gate: what the two passes
read, what the official word is, and how sure the reader was. Optionally tries candidate
look-alike pairs WITHOUT applying them (nothing in the engine is changed by this script).

    uv run python eval/false_alarm_report.py            # gate 90 (the lowest where 6 survive)
    uv run python eval/false_alarm_report.py --gate 80

SYNTHETIC fictional pictures only: see docs/EVAL.md.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.cases import IMAGE_SUITES, RECORD_JSON, build, render_image  # noqa: E402
from eval.corpus import load_record  # noqa: E402

from confam_engine.compare import lookalike as LA  # noqa: E402
from confam_engine.ocr import agree  # noqa: E402
from confam_engine.ocr.agree import _per_reading, _visible, evaluate_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, tesseract_available  # noqa: E402


def char_ops(copy: str, official: str) -> list[str]:
    """Character substitutions between what was read and the official text, e.g. ['N>M']."""
    out = []
    sm = difflib.SequenceMatcher(None, copy, official, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            out.append(f"{copy[i1:i2] or '-'}>{official[j1:j2] or '-'}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", type=float, default=90)
    args = ap.parse_args()
    if not tesseract_available():
        print("Tesseract is not installed")
        return 1
    record, _ = load_record(RECORD_JSON)
    cases = [c for c in build(include_images=True) if c.suite == "honest_image"]
    readers = default_readers()
    cache = [(c, [r.read(load_image(render_image(c))) for r in readers]) for c in cases]

    hits = []
    for c, rd in cache:
        out = evaluate_readings(rd, record, args.gate)
        if out.verdict == "altered":
            hits.append((c, rd, out))
    print(f"honest pictures: {len(cases)}; still called altered at gate {args.gate:g}: {len(hits)}\n")

    for n, (c, rd, out) in enumerate(hits, 1):
        ta, ba, ca, ma = _per_reading(rd[0], record)
        tb, bb, cb, mb = _per_reading(rd[1], record)
        da, _ = _visible(ta, ba, ca, ma, record)
        db, _ = _visible(tb, bb, cb, mb, record)
        print(f"{n}. {c.id}  ({c.kind})")
        for d in out.changes:
            key = (d.op, d.kind, d.official, d.copy)
            a = next((x for x in da if (x.op, x.kind, x.official, x.copy) == key), None)
            b = next((x for x in db if (x.op, x.kind, x.official, x.copy) == key), None)
            ca_, cb_ = (a.conf if a else None), (b.conf if b else None)
            print(f"     official: {d.official!r:<26} pass 1 read: {(a.copy if a else None)!r:<22} (conf {ca_}) pass 2 read: {(b.copy if b else None)!r:<22} (conf {cb_})")
            print(f"     kind {d.kind}/{d.op}; character differences vs official: {char_ops(d.copy or '', d.official or '')}")
        print()

    # ----- hypothetical: would an extended look-alike set fix them, and is it safe? (not applied)
    cands = {
        "M/N": ({"m": "n"}, ()),
        "rn/m + cl/d (already in)": ({}, ()),
        "u/v": ({"v": "u"}, ()),
        "e/c": ({"e": "c"}, ()),
        "a/o": ({"a": "o"}, ()),
        "h/b": ({"h": "b"}, ()),
    }
    print("Candidate additions to the reading-slip rule (NOT applied): effect on all picture suites at gate", f"{args.gate:g}")
    all_cases = [c for c in build(include_images=True) if c.suite in IMAGE_SUITES]
    all_cache = cache + [(c, [r.read(load_image(render_image(c))) for r in readers]) for c in all_cases if c.suite != "honest_image"]
    base_single, base_multi = LA._SINGLE, LA._MULTI
    try:
        for name, (extra, _) in cands.items():
            LA._SINGLE = {**base_single, **{ord(k): v for k, v in extra.items()}} if extra else base_single
            LA._MULTI = base_multi
            alarms = forged = caught = 0
            for c, rd in all_cache:
                v = evaluate_readings(rd, record, args.gate).verdict
                if c.suite == "honest_image" and v in {"altered", "not_official"}:
                    alarms += 1
                if c.suite == "edits_image":
                    forged += v == "confirmed"
                    caught += v in c.expected
            print(f"  {name:<26} honest false alarms {alarms}   edited pictures altered {caught}/92   FORGED CONFIRMED {forged}")
    finally:
        LA._SINGLE, LA._MULTI = base_single, base_multi

    # ----- hypothetical: a separate (lower) confidence floor for web addresses and phone numbers.
    # At gate 95 Tesseract's confidence for these (about 84-91) can never pass, so a changed address
    # or phone number on a photo is never called altered. NOT applied; measured here only.
    print("\nProposal (NOT applied): gate 95 for everything, but a lower floor for web addresses and phone numbers")
    base_low = agree._low
    try:
        for floor in (None, 90, 85, 80, 75):
            def _low(d, min_conf, floor=floor):
                f = floor if (d.kind in {"link", "phone"} and floor is not None) else min_conf
                return f is not None and d.conf is not None and d.conf < f
            agree._low = _low
            alarms = forged = caught = link_phone = 0
            alarm_kinds = Counter()
            for c, rd in all_cache:
                out = evaluate_readings(rd, record, 95.0)
                v = out.verdict
                if c.suite == "honest_image" and v in {"altered", "not_official"}:
                    alarms += 1
                    alarm_kinds.update({d.kind for d in out.changes})
                if c.suite == "edits_image":
                    forged += v == "confirmed"
                    caught += v in c.expected
                    if c.kind.split("@")[0] in {"link_host", "phone"}:
                        link_phone += v == "altered"
            label = "no separate floor (the default)" if floor is None else f"link/phone floor {floor}"
            print(f"  {label:<32} honest false alarms {alarms} {dict(alarm_kinds) if alarms else ''}   edited pictures altered {caught}/92 (link+phone edits caught {link_phone}/24)   FORGED CONFIRMED {forged}")
    finally:
        agree._low = base_low
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
