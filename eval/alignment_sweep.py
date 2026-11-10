"""How much of a notice must a copy line up with before it can be called altered?

Sweeps the threshold over the TEXT suites (fast) and, with --images, the picture suites (reads each
picture once). For each value it reports where the cases land, so a threshold can be chosen.

    uv run python eval/alignment_sweep.py
    uv run python eval/alignment_sweep.py --images

SYNTHETIC fictional fixtures only: see docs/EVAL.md. The chosen value lives in
confam_engine.evaluate.MIN_ALIGNMENT_FOR_ALTERED.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.cases import IMAGE_SUITES, RECORD_JSON, build, render_image  # noqa: E402
from eval.corpus import load_record  # noqa: E402

from confam_engine.compare import tokenize  # noqa: E402
from confam_engine.compare.match import find_notice  # noqa: E402
from confam_engine.evaluate import evaluate  # noqa: E402
from confam_engine.ocr.agree import evaluate_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, tesseract_available  # noqa: E402

THRESHOLDS = [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]


def verdict_of(out) -> str:
    return out.verdict + (f"/{out.reason}" if out.reason else "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", action="store_true")
    args = ap.parse_args()
    record, _ = load_record(RECORD_JSON)
    cases = build(include_images=False)

    # how much of its notice does each kind of case line up with?
    cover: dict[str, list[float]] = {}
    for c in cases:
        m = find_notice(tokenize(c.text), record)
        if m is not None and (c.role == "edit" or c.suite in {"paraphrases", "modified_real", "pidgin_rumours", "invented"}):
            cover.setdefault(c.suite if c.suite not in {"edits_text", "edits_text_wrapped"} else "edits", []).append(m.notice_coverage)
    print("share of the notice's words the copy lines up with (matched cases only):")
    for k, v in cover.items():
        print(f"  {k:<16} n={len(v):<4} min={min(v):.2f} median={statistics.median(v):.2f} max={max(v):.2f}")

    rows = []
    for t in THRESHOLDS:
        row = Counter()
        wrong_edits = []
        for c in cases:
            out = evaluate(c.text, record, t)
            v = out.verdict
            if c.suite in {"edits_text", "edits_text_wrapped"}:
                row["edits"] += 1
                row["edits_ok"] += v in c.expected or (v == "cannot_confirm" and out.reason == "unclear" and "cannot_confirm" in c.expected)
                if v not in c.expected:
                    wrong_edits.append((c.id, verdict_of(out)))
            elif c.suite == "modified_real":
                row["rewrites"] += 1
                row["rewrites_ok"] += v in c.expected
            elif c.suite == "paraphrases":
                row["paraphrases"] += 1
                row["paraphrases_not_altered"] += v != "altered"
                row["paraphrases_ok"] += v in c.expected
            elif c.suite in {"invented", "pidgin_rumours"}:
                row["invented"] += 1
                row["invented_ok"] += v in c.expected
            elif c.suite == "crops_text":
                row["crops"] += 1
                row["crops_partial"] += v == "partial"
            elif c.suite == "honest_text":
                row["honest"] += 1
                row["honest_confirmed"] += v == "confirmed"
            if c.role in {"edit", "invented"} and v == "confirmed":
                row["forged_confirmed"] += 1
        rows.append((t, row, wrong_edits))

    print("\nTEXT suites by alignment threshold")
    print(f"{'T':>5} | edits ok | rewrites ok | paraphrases not altered | crops partial | honest confirmed | forged confirmed")
    for t, r, _ in rows:
        print(f"{t:>5} | {r['edits_ok']:>3}/{r['edits']:<3}  | {r['rewrites_ok']:>3}/{r['rewrites']:<3}     | {r['paraphrases_not_altered']:>5}/{r['paraphrases']:<3}                | {r['crops_partial']:>3}/{r['crops']:<3}       | {r['honest_confirmed']:>4}/{r['honest']:<4}       | {r['forged_confirmed']}")
    print("\nedits that stop being 'altered' as the threshold rises (id -> verdict):")
    seen = set()
    for t, r, wrong in rows:
        new = [w for w in wrong if w[0] not in seen]
        seen |= {w[0] for w in wrong}
        if new and t:
            print(f"  at {t}: {len(new)} more, e.g. {new[:3]}")

    if args.images:
        if not tesseract_available():
            print("Tesseract is not installed")
            return 1
        icases = [c for c in build(include_images=True) if c.suite in IMAGE_SUITES]
        readers = default_readers()
        readings = [[r.read(load_image(render_image(c))) for r in readers] for c in icases]
        print("\nPICTURE suites by alignment threshold (confidence gate off)")
        print(f"{'T':>5} | honest: confirmed/false alarm/withheld | edits: altered/withheld/FORGED | crops partial")
        for t in THRESHOLDS:
            h, e, cr = Counter(), Counter(), Counter()
            for c, rd in zip(icases, readings):
                out = evaluate_readings(rd, record, None, t)
                if c.suite == "honest_image":
                    h["confirmed" if out.verdict == "confirmed" else "alarm" if out.verdict in {"altered", "not_official"} else "withheld"] += 1
                elif c.suite == "edits_image":
                    e["altered" if out.verdict in c.expected else "forged" if out.verdict == "confirmed" else "withheld"] += 1
                else:
                    cr["partial" if out.verdict == "partial" else "other"] += 1
            print(f"{t:>5} | {h['confirmed']:>9}/{h['alarm']:>11}/{h['withheld']:>8} | {e['altered']:>7}/{e['withheld']:>8}/{e['forged']:>5} | {cr['partial']:>3}/16")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
