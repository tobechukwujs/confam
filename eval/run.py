"""The evaluation. Runs the fictional-commission suites through the real engine (and, for pictures,
through Tesseract) and reports, per suite and overall:

  correct verdicts                         the verdict is one of the accepted answers for the case
  forged copies confirmed as genuine       an edited or invented copy that came out `confirmed` (MUST BE 0)
  false alarms on honest copies            an honest copy called altered or not_official
  honest copies not confirmed              an honest copy answered cannot_confirm or partial (safe, but unhelpful)

    uv run python eval/run.py                  # everything (pictures need Tesseract)
    uv run python eval/run.py --no-images      # text suites only (fast)
    uv run python eval/run.py --suite honest_text edits_text

Exit code 1 if any forged or invented copy is confirmed. Results are written to eval/results/.

SYNTHETIC: every case is built from the fictional Simulated Electoral Commission record in
eval/record.json. These numbers say nothing about real notices, real letterheads or stamps,
or real photographs. See docs/EVAL.md.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eval.cases import IMAGE_SUITES, RECORD_JSON, Case, build, render_image  # noqa: E402
from eval.corpus import load_record  # noqa: E402

from confam_engine import check_notice  # noqa: E402
from confam_engine.ocr import check_readings  # noqa: E402
from confam_engine.ocr.imageio import load_image  # noqa: E402
from confam_engine.ocr.tesseract import default_readers, find_tesseract, tesseract_available  # noqa: E402

RESULTS = ROOT / "eval" / "results"
DISCLAIMER = (
    "SYNTHETIC. Every case is built from the fictional Simulated Electoral Commission record in "
    "eval/record.json. These numbers say nothing about real notices, real letterheads or stamps, or real photographs."
)


def run_case(case: Case, record, now, readers) -> dict:
    t0 = time.time()
    if case.degrade is None:
        v = check_notice(case.text, record, record_as_of=now, lang="en", now=now)
    else:
        img = load_image(render_image(case))
        v = check_readings([r.read(img) for r in readers], record, record_as_of=now, lang="en", now=now)
    verdict = v.verdict.value
    got = verdict + (f"/{v.reason.value}" if v.reason else "")
    return {
        "id": case.id, "suite": case.suite, "role": case.role, "kind": case.kind,
        "expected": sorted(case.expected), "verdict": verdict, "got": got,
        "correct": verdict in case.expected,
        "notice": v.notice.id if v.notice else None,
        "superseded_by": v.superseded_by.id if v.superseded_by else None,
        "changes": [f"{c.op.value} {c.kind.value} {c.copy_!r}->{c.official!r}" for c in v.changes][:4],
        "text": case.text[:140], "notice_id": case.notice_id, "note": case.note,
        "seconds": round(time.time() - t0, 2),
    }


def summarise(rows: list[dict]) -> dict:
    s = Counter()
    for r in rows:
        s["n"] += 1
        s["correct"] += r["correct"]
        if r["role"] in {"edit", "invented"} and r["verdict"] == "confirmed":
            s["forged_confirmed"] += 1
        if r["role"] == "crop" and r["verdict"] == "confirmed":
            s["crops_confirmed_as_complete"] += 1
        if r["role"] == "honest":
            if r["verdict"] in {"altered", "not_official"}:
                s["honest_false_alarms"] += 1
            elif r["verdict"] != "confirmed":
                s["honest_not_confirmed"] += 1
            if r["verdict"] == "confirmed" and r["notice"] == "SEC-E-001" and not r["superseded_by"]:
                s["replaced_notice_not_flagged"] += 1
        if r["role"] == "edit":
            s["edits"] += 1
            if r["verdict"] in {"altered", "partial"} or r["got"] == "cannot_confirm/unclear":
                s["edits_caught_or_withheld"] += 1
    return dict(s)


def git_commit() -> str:
    """Short commit hash, plus +uncommitted changes if the working tree is not clean."""
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        return (head or "unknown") + (" + uncommitted changes" if dirty else "")
    except Exception:
        return "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-images", action="store_true", help="skip the picture suites")
    ap.add_argument("--suite", nargs="*", help="only these suites")
    ap.add_argument("--no-write", action="store_true", help="do not write eval/results/")
    args = ap.parse_args(argv)

    images_ok = tesseract_available() and not args.no_images
    cases = build(include_images=images_ok)
    if args.suite:
        cases = [c for c in cases if c.suite in args.suite]
    skipped = sorted({c.suite for c in build(include_images=True)} & IMAGE_SUITES) if not images_ok else []
    record, _ = load_record(RECORD_JSON)
    readers = default_readers() if images_ok else None
    now = datetime.now(timezone.utc)

    rows = []
    t0 = time.time()
    for i, case in enumerate(cases, 1):
        rows.append(run_case(case, record, now, readers))
        if i % 100 == 0:
            print(f"  ... {i}/{len(cases)}", file=sys.stderr)
    elapsed = time.time() - t0

    by_suite: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_suite[r["suite"]].append(r)
    suites = {name: summarise(rs) for name, rs in by_suite.items()}
    total = summarise(rows)

    meta = {
        "date": now.isoformat(timespec="seconds"), "git_commit": git_commit(),
        "python": platform.python_version(), "tesseract": find_tesseract() if images_ok else None,
        "seconds": round(elapsed, 1), "cases": len(rows), "skipped_suites": skipped,
        "record": "eval/record.json (fictional)", "disclaimer": DISCLAIMER,
    }
    print_report(meta, suites, total)
    if not args.no_write:
        write_results(meta, suites, total, rows)
    return 1 if total.get("forged_confirmed", 0) > 0 else 0


def print_report(meta, suites, total) -> None:
    print(f"\nConfam evaluation, {meta['date']} (commit {meta['git_commit']})")
    print(DISCLAIMER)
    if meta["skipped_suites"]:
        print(f"SKIPPED (no Tesseract or --no-images): {', '.join(meta['skipped_suites'])}")
    print(f"\n{'suite':<22}{'cases':>6}{'correct':>9}{'forged confirmed':>18}{'false alarms':>14}{'honest not confirmed':>22}")
    for name, s in suites.items():
        honest = name.startswith("honest")
        print(f"{name:<22}{s['n']:>6}{s['correct']:>9}{s.get('forged_confirmed', 0):>18}{(s.get('honest_false_alarms', 0) if honest else '-'):>14}{(s.get('honest_not_confirmed', 0) if honest else '-'):>22}")
    print(f"{'TOTAL':<22}{total['n']:>6}{total['correct']:>9}{total.get('forged_confirmed', 0):>18}{total.get('honest_false_alarms', 0):>14}{total.get('honest_not_confirmed', 0):>22}")
    print(f"\nforged or invented copies confirmed as genuine: {total.get('forged_confirmed', 0)}  (must be 0)")
    print(f"crops confirmed as complete: {total.get('crops_confirmed_as_complete', 0)}  (should be 0)")
    print(f"replaced notice confirmed without superseded_by: {total.get('replaced_notice_not_flagged', 0)}  (must be 0)")


def write_results(meta, suites, total, rows) -> None:
    RESULTS.mkdir(exist_ok=True)
    wrong = [r for r in rows if not r["correct"]]
    (RESULTS / "latest.json").write_text(
        json.dumps({"meta": meta, "total": total, "suites": suites, "wrong": wrong, "cases": rows}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Evaluation results", "",
        f"Run `{meta['date']}` on commit `{meta['git_commit']}` by `uv run python eval/run.py`.", "",
        f"> {DISCLAIMER}", "",
        "| suite | cases | correct | forged confirmed | false alarms | honest not confirmed |", "|---|---:|---:|---:|---:|---:|",
    ]
    for name, s in suites.items():
        honest = name.startswith("honest")
        lines.append(f"| {name} | {s['n']} | {s['correct']} | {s.get('forged_confirmed', 0)} | {s.get('honest_false_alarms', 0) if honest else '-'} | {s.get('honest_not_confirmed', 0) if honest else '-'} |")
    lines += [
        f"| **total** | {total['n']} | {total['correct']} | {total.get('forged_confirmed', 0)} | {total.get('honest_false_alarms', 0)} | {total.get('honest_not_confirmed', 0)} |", "",
        f"- Forged or invented copies confirmed as genuine: **{total.get('forged_confirmed', 0)}** (must be 0).",
        f"- Crops confirmed as complete: {total.get('crops_confirmed_as_complete', 0)}.",
        f"- Replaced notice confirmed without `superseded_by`: {total.get('replaced_notice_not_flagged', 0)}.",
    ]
    if meta["skipped_suites"]:
        lines.append(f"- Skipped (no Tesseract): {', '.join(meta['skipped_suites'])}.")
    lines += ["", "## Cases that did not get an accepted verdict", "", "| case | expected | got | changes |", "|---|---|---|---|"]
    for r in wrong[:150]:
        lines.append(f"| `{r['id']}` | {'/'.join(r['expected'])} | {r['got']} | {'; '.join(r['changes']) or '-'} |")
    if len(wrong) > 150:
        lines.append(f"| ... {len(wrong) - 150} more in latest.json | | | |")
    (RESULTS / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
