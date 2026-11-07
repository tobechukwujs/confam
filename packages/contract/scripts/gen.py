"""Generate TypeScript and Pydantic types from verdict.schema.json.

    uv run python packages/contract/scripts/gen.py          # write generated files
    uv run python packages/contract/scripts/gen.py --check  # fail if they are stale or hand-edited

Never hand-edit the outputs. Change the schema and re-run.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SCHEMA = ROOT / "verdict.schema.json"
TS_OUT = ROOT / "ts" / "verdict.ts"
PY_OUT = ROOT / "py" / "confam_contract" / "verdict.py"

BANNER = "GENERATED from packages/contract/verdict.schema.json by `pnpm contract:gen`. DO NOT EDIT."


def run(cmd: list[str]) -> None:
    # shell=False; on Windows pnpm is a .cmd shim, so resolve it with shutil.which.
    resolved = shutil.which(cmd[0])
    if resolved is None:
        sys.exit(f"gen: '{cmd[0]}' not found on PATH")
    subprocess.run([resolved, *cmd[1:]], check=True, cwd=REPO)


def strip_allof(node):
    """Shape-only copy of the schema: drop every allOf (the cross-field rules).

    allOf makes json-schema-to-typescript emit `[k: string]: unknown` intersections,
    which defeats typo checks. additionalProperties: false is kept. The full schema
    with allOf stays the source of truth for validation.
    """
    if isinstance(node, dict):
        return {k: strip_allof(v) for k, v in node.items() if k != "allOf"}
    if isinstance(node, list):
        return [strip_allof(v) for v in node]
    return node


def gen_ts(out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    shape = strip_allof(json.loads(SCHEMA.read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as tmp:
        shape_path = Path(tmp) / "verdict.shape.json"
        shape_path.write_text(json.dumps(shape), encoding="utf-8")
        run(
            [
                "pnpm", "exec", "json2ts",
                "--input", str(shape_path),
                "--output", str(out),
                "--bannerComment", f"/* {BANNER} Shape only: cross-field rules are in the schema. */",
                "--unreachableDefinitions",
            ]
        )


def gen_py(out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "datamodel-codegen",
            "--input", str(SCHEMA),
            "--input-file-type", "jsonschema",
            "--output", str(out),
            "--output-model-type", "pydantic_v2.BaseModel",
            "--class-name", "Verdict",
            "--use-standard-collections",
            "--field-constraints",
            "--disable-timestamp",
            "--custom-file-header", f"# {BANNER}",
        ]
    )
    # Ensure the package is importable.
    init = out.parent / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")


def main() -> int:
    check = "--check" in sys.argv[1:]
    if not check:
        gen_ts(TS_OUT)
        gen_py(PY_OUT)
        print("generated:", TS_OUT.relative_to(REPO), PY_OUT.relative_to(REPO))
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_ts = Path(tmp) / "verdict.ts"
        tmp_py = Path(tmp) / "verdict.py"
        gen_ts(tmp_ts)
        gen_py(tmp_py)
        stale = [
            str(dst.relative_to(REPO))
            for fresh, dst in ((tmp_ts, TS_OUT), (tmp_py, PY_OUT))
            if not dst.exists() or fresh.read_bytes().replace(b"\r\n", b"\n") != dst.read_bytes().replace(b"\r\n", b"\n")
        ]
    if stale:
        print("stale or hand-edited generated files:", *stale, sep="\n  ")
        print("run `pnpm contract:gen`")
        return 1
    print("generated files are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
