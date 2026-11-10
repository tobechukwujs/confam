"""The confidence-gate trade-off. Reads every picture in the photo suites ONCE with Tesseract, then
re-judges the same readings under a range of thresholds: a change resting on a word read below the
threshold (in either reading) is cannot_confirm / unclear, never altered.

    uv run python eval/confidence_table.py

Writes eval/results/confidence_table.json and .md. SYNTHETIC fictional pictures only: see docs/EVAL.md.
The threshold is the product owner's choice; nothing here sets it.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.cases import IMAGE_SUITES, RECORD_JSON, build, render_image  # noqa: E402
from eval.corpus import load_record  # noqa: E402

from confam_engine.ocr.agree import evaluate_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, tesseract_available  # noqa: E402

THRESHOLDS: list[float | None] = [None, 30, 40, 50, 60, 65, 70, 75, 80, 85, 90, 95]
DISCLAIMER = "SYNTHETIC fictional pictures only (eval/record.json). Says nothing about real photographs."


def main() -> int:
    if not tesseract_available():
        print("Tesseract is not installed")
        return 1
    record, _ = load_record(RECORD_JSON)
    cases = [c for c in build(include_images=True) if c.suite in IMAGE_SUITES]
    readers = default_readers()
    t0 = time.time()
    readings = []
    for i, c in enumerate(cases, 1):
        img = load_image(render_image(c))
        readings.append([r.read(img) for r in readers])
        if i % 40 == 0:
            print(f"  read {i}/{len(cases)}", file=sys.stderr)
    read_seconds = round(time.time() - t0, 1)

    table = []
    for t in THRESHOLDS:
        row = {"threshold": t, "honest": Counter(), "edits": Counter(), "crops": Counter()}
        for c, rd in zip(cases, readings):
            out = evaluate_readings(rd, record, t)
            got = out.verdict + (f"/{out.reason}" if out.reason else "")
            if c.suite == "honest_image":
                key = "confirmed" if out.verdict == "confirmed" else "false_alarm" if out.verdict in {"altered", "not_official"} else "withheld"
                row["honest"][key] += 1
            elif c.suite == "edits_image":
                key = "caught" if out.verdict in c.expected else "forged_confirmed" if out.verdict == "confirmed" else "withheld"
                row["edits"][key] += 1
            else:
                row["crops"]["partial" if out.verdict == "partial" else "other"] += 1
        table.append(row)

    # what the confidences look like: noise on honest pictures vs the real edit on edited ones
    noise, real = [], []
    for c, rd in zip(cases, readings):
        out = evaluate_readings(rd, record, None)
        if c.suite == "honest_image" and out.verdict == "altered":
            noise += [d.conf for d in out.changes if d.conf is not None]
        if c.suite == "edits_image" and out.verdict == "altered":
            want = c.kind.split("@")[0]
            hit = [d for d in out.changes if d.kind in {"date", "link", "time", "number", "money", "phone", "negation", "weekday"}]
            real += [min(d.conf for d in hit if d.conf is not None)] if any(d.conf is not None for d in hit) else []

    def stats(xs):
        xs = sorted(xs)
        return {"n": len(xs), "min": round(xs[0], 1), "median": round(statistics.median(xs), 1), "max": round(xs[-1], 1)} if xs else {"n": 0}

    n_h = sum(1 for c in cases if c.suite == "honest_image")
    n_e = sum(1 for c in cases if c.suite == "edits_image")
    n_c = sum(1 for c in cases if c.suite == "crops_image")
    meta = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "reading_seconds": read_seconds, "honest": n_h, "edits": n_e, "crops": n_c, "disclaimer": DISCLAIMER}

    lines = [f"{'threshold':>10} | honest: confirmed / false alarm / withheld | edits: caught / withheld / FORGED CONFIRMED | crops partial"]
    for r in table:
        t = "off" if r["threshold"] is None else r["threshold"]
        h, e, cr = r["honest"], r["edits"], r["crops"]
        lines.append(f"{str(t):>10} | {h['confirmed']:>9} / {h['false_alarm']:>11} / {h['withheld']:>8} | {e['caught']:>12} / {e['withheld']:>8} / {e['forged_confirmed']:>3} | {cr['partial']:>6}/{n_c}")
    print("\n" + DISCLAIMER)
    print(f"honest pictures {n_h}, edited pictures {n_e}, cropped pictures {n_c} (read once in {read_seconds}s)\n")
    print("\n".join(lines))
    print("\nconfidence of the changes reported on honest pictures that were called altered (noise):", stats(noise))
    print("lowest confidence among the real-fact changes reported on edited pictures called altered:", stats(real))

    out_dir = ROOT / "eval" / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "confidence_table.json").write_text(json.dumps({"meta": meta, "table": [{**r, "honest": dict(r["honest"]), "edits": dict(r["edits"]), "crops": dict(r["crops"])} for r in table], "noise_confidence": stats(noise), "real_change_confidence": stats(real)}, indent=1) + "\n", encoding="utf-8")
    md = ["# Confidence gate: trade-off", "", f"> {DISCLAIMER}", "", f"Run `{meta['date']}`. {n_h} honest pictures, {n_e} edited pictures, {n_c} crops.", "", "| threshold | honest confirmed | honest false alarms | honest withheld | edits caught (altered) | edits withheld | forged confirmed | crops partial |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in table:
        t = "off" if r["threshold"] is None else r["threshold"]
        h, e, cr = r["honest"], r["edits"], r["crops"]
        md.append(f"| {t} | {h['confirmed']} | {h['false_alarm']} | {h['withheld']} | {e['caught']} | {e['withheld']} | {e['forged_confirmed']} | {cr['partial']} |")
    md += ["", f"Confidence of changes reported on honest pictures called altered (noise): `{stats(noise)}`.", f"Lowest confidence among real-fact changes on edited pictures called altered: `{stats(real)}`."]
    (out_dir / "confidence_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
