"""Smoke test for a running Confam: the API, and optionally the web app in front of it.

    python scripts/smoke.py --api https://confam-api.onrender.com --web https://confam.vercel.app
    python scripts/smoke.py --api http://localhost:8000 --web http://localhost:3000

Standard library only. Exit code 1 if anything FAILS. Steps that cannot apply (photo checks off,
no --web) are reported as SKIPPED, never as passed. The first request to a free Render service
can take a minute while it wakes up, so timeouts are generous.

It uses the fictional sample record (fixtures/sec-sim) and the demo pictures
(fixtures/sec-sim/demo), so run it from the repository root against a deployment that loaded that
record. It creates a few checks (nothing personal) that expire on their own.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "fixtures" / "sec-sim" / "demo"
NOTICE_140 = next(n for n in json.loads((ROOT / "fixtures/sec-sim/notices.json").read_text(encoding="utf-8"))["notices"] if n["id"] == "SEC-2026-140")

results: list[tuple[str, str, str]] = []  # (status, name, detail)


def record(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))
    print(f"  {status:<8} {name}" + (f"  ({detail})" if detail else ""))


def call(method: str, url: str, *, body: bytes | None = None, headers: dict | None = None, timeout: int = 120):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read(), time.time() - t0
    except Exception as e:  # connection refused, DNS, timeout
        return 0, {}, str(e).encode(), time.time() - t0


def jget(url: str, **kw):
    status, headers, body, secs = call("GET", url, **kw)
    try:
        return status, headers, json.loads(body or b"null"), secs
    except json.JSONDecodeError:
        return status, headers, None, secs


def check(name: str, ok: bool, detail: str = "") -> bool:
    record("PASS" if ok else "FAIL", name, detail)
    return ok


def photo_check(api: str, path: Path, expect: str, name: str) -> None:
    status, _, body, _ = call("POST", f"{api}/v1/checks?lang=en", body=path.read_bytes(), headers={"Content-Type": "image/png"})
    if not check(f"{name}: upload accepted", status == 202, f"HTTP {status}"):
        return
    job_id = json.loads(body)["job_id"]
    for _ in range(120):
        _, _, job, _ = jget(f"{api}/v1/checks/{job_id}")
        if job and job["status"] != "working":
            break
        time.sleep(1)
    if not check(f"{name}: job finished", bool(job) and job["status"] == "done", f"{job}"):
        return
    _, _, verdict, _ = jget(f"{api}/v1/verdicts/{job['code']}")
    check(f"{name}: verdict is {expect}", bool(verdict) and verdict["verdict"] == expect, f"got {verdict and verdict['verdict']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Smoke test a Confam deployment")
    ap.add_argument("--api", required=True, help="API base URL, e.g. https://confam-api.onrender.com")
    ap.add_argument("--web", help="web app base URL (also checks CORS and the web-to-API link)")
    args = ap.parse_args()
    api, web = args.api.rstrip("/"), (args.web or "").rstrip("/")

    print(f"API {api}" + (f"  WEB {web}" if web else ""))
    print("\nAPI")
    status, _, health, secs = jget(f"{api}/health")
    if not check("health answers", status == 200 and bool(health) and health.get("status") == "ok", f"HTTP {status}, {secs:.1f}s (a first call to a sleeping free service can be slow)"):
        print("\nThe API is not answering: nothing else can be checked.")
        return 1
    photos = bool(health.get("photo_checks"))
    record("INFO", "photo checks", "available" if photos else "OFF (Tesseract not found on the server)")

    status, _, raw, secs = call("POST", f"{api}/v1/checks", body=json.dumps({"text": NOTICE_140["text"], "lang": "en"}).encode(), headers={"Content-Type": "application/json"})
    v = json.loads(raw) if status == 200 else None
    check("text check: the genuine notice is Confirmed", status == 200 and v["verdict"] == "confirmed" and v["notice"]["id"] == "SEC-2026-140", f"HTTP {status}, {secs:.1f}s")
    check("text check: carries no score", v is not None and not any(k in json.dumps(v).lower() for k in ("confidence", "score", "percent")))
    code = v["code"] if v else None

    edited = NOTICE_140["text"].replace("28th November", "29th November")
    status, _, raw, _ = call("POST", f"{api}/v1/checks", body=json.dumps({"text": edited}).encode(), headers={"Content-Type": "application/json"})
    check("text check: a changed date is Altered", status == 200 and json.loads(raw)["verdict"] == "altered")

    status, _, raw, _ = call("POST", f"{api}/v1/checks", body=json.dumps({"text": "Collect your new ballot cards at the market square on Sunday."}).encode(), headers={"Content-Type": "application/json"})
    vv = json.loads(raw) if status == 200 else {}
    check("text check: an unknown rumour is Cannot confirm / not in record, never fake", vv.get("verdict") == "cannot_confirm" and vv.get("reason") == "not_in_record")

    if code:
        status, _, again, _ = jget(f"{api}/v1/verdicts/{code}")
        check("public verdict page data: the check can be opened by its code", status == 200 and again and again["code"] == code)
    status, _, _, _ = jget(f"{api}/v1/verdicts/ZZZZZZZZ")
    check("a forged code is a 404", status == 404)
    status, _, rec, _ = jget(f"{api}/v1/record")
    check("the public record lists SEC-2026-140", status == 200 and any(n["id"] == "SEC-2026-140" for n in (rec or {}).get("notices", [])))
    status, _, ent, _ = jget(f"{api}/v1/record/SEC-2026-140")
    check("the record shows the exact signed text and two signatures", status == 200 and ent["text"] == NOTICE_140["text"] and len(ent["signatures"]) == 2)
    status, _, _, _ = jget(f"{api}/v1/record/SEC-0000-000")
    check("an unknown notice is a 404", status == 404)

    if web:
        status, hdr, _, _ = call("OPTIONS", f"{api}/v1/checks", headers={"Origin": web, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"})
        check("CORS: the web origin may upload photos", hdr.get("access-control-allow-origin") == web, f"HTTP {status}, allow-origin={hdr.get('access-control-allow-origin')!r}; set CONFAM_CORS_ORIGINS={web} on the API")
        status, hdr, _, _ = call("OPTIONS", f"{api}/v1/checks", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
        check("CORS: another origin is refused", hdr.get("access-control-allow-origin") in (None, ""))

    print("\nPHOTO CHECKS (demo pictures)")
    if photos:
        photo_check(api, DEMO / "01_honest_confirmed.png", "confirmed", "honest picture")
        photo_check(api, DEMO / "02_altered_date.png", "altered", "changed date")
        photo_check(api, DEMO / "04_not_official.png", "not_official", "invented notice")
        photo_check(api, DEMO / "05_partial_crop.png", "partial", "cropped picture")
        photo_check(api, DEMO / "06_cannot_confirm_blurry.png", "cannot_confirm", "blurry picture")
        status, _, _, _ = call("POST", f"{api}/v1/checks?lang=en", body=b"not a picture", headers={"Content-Type": "image/png"})
        check("a file that is not a picture is refused (415)", status == 415, f"HTTP {status}")
    else:
        record("SKIPPED", "photo checks", "the API reports photo_checks=false")

    print("\nWEB")
    if web:
        status, _, body, secs = call("GET", f"{web}/")
        page = body.decode("utf-8", "replace")
        check("home page loads", status == 200 and "Is this notice real?" in page, f"HTTP {status}, {secs:.1f}s")
        check("home page: the independence line", "Independent checker. Not INEC or any party." in page)
        check("home page: photo checks are labelled Beta", "Beta" in page)
        status, _, body, _ = call("GET", f"{web}/record")
        check("record page loads (web reaches the API)", status == 200 and "SEC-2026-140" in body.decode("utf-8", "replace"), f"HTTP {status}; the web app's API_URL must point at the API")
        if code:
            status, _, body, _ = call("GET", f"{web}/v/{code}")
            check("verdict page shows the check (web reaches the API)", status == 200 and "Confirmed" in body.decode("utf-8", "replace"), f"HTTP {status}")
        status, _, body, _ = call("GET", f"{web}/v/ZZZZZZZZ")
        check("a forged code shows a plain 'no check' page", status == 404 and "No check with that code" in body.decode("utf-8", "replace"))
        status, _, body, _ = call("GET", f"{web}/?lang=ha")
        check("a language can be chosen (Hausa draft)", status == 200 and "Fassarar gwaji" in body.decode("utf-8", "replace"))
    else:
        record("SKIPPED", "web checks", "no --web given")

    fails = [r for r in results if r[0] == "FAIL"]
    passed = [r for r in results if r[0] == "PASS"]
    skipped = [r for r in results if r[0] == "SKIPPED"]
    print(f"\n{len(passed)} passed, {len(fails)} FAILED, {len(skipped)} skipped")
    for _, name, detail in fails:
        print(f"  FAILED: {name}  {detail}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
