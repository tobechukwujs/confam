"""Generate TypeScript and Pydantic types from the contract JSON Schemas.

    uv run python packages/contract/scripts/gen.py          # write generated files
    uv run python packages/contract/scripts/gen.py --check  # fail if they are stale or hand-edited

Never hand-edit the outputs. Change a schema and re-run.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


@dataclass(frozen=True)
class Target:
    schema: Path
    ts_out: Path
    py_out: Path
    class_name: str


TARGETS = [
    Target(ROOT / "verdict.schema.json", ROOT / "ts" / "verdict.ts", ROOT / "py" / "confam_contract" / "verdict.py", "Verdict"),
    Target(ROOT / "job.schema.json", ROOT / "ts" / "job.ts", ROOT / "py" / "confam_contract" / "job.py", "Job"),
]


def banner(t: Target) -> str:
    return f"GENERATED from packages/contract/{t.schema.name} by `pnpm contract:gen`. DO NOT EDIT."


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


def gen_ts(t: Target, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    shape = strip_allof(json.loads(t.schema.read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as tmp:
        shape_path = Path(tmp) / f"{t.schema.stem}.shape.json"
        shape_path.write_text(json.dumps(shape), encoding="utf-8")
        run(
            [
                "pnpm", "exec", "json2ts",
                "--input", str(shape_path),
                "--output", str(out),
                "--bannerComment", f"/* {banner(t)} Shape only: cross-field rules are in the schema. */",
                "--unreachableDefinitions",
            ]
        )


def gen_py(t: Target, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "datamodel-codegen",
            "--input", str(t.schema),
            "--input-file-type", "jsonschema",
            "--output", str(out),
            "--output-model-type", "pydantic_v2.BaseModel",
            "--class-name", t.class_name,
            "--use-standard-collections",
            "--field-constraints",
            "--disable-timestamp",
            "--custom-file-header", f"# {banner(t)}",
        ]
    )
    # Ensure the package is importable.
    init = out.parent / "__init__.py"
    if not init.exists():
        init.write_text("", encoding="utf-8")


def same(a: Path, b: Path) -> bool:
    return b.exists() and a.read_bytes().replace(b"\r\n", b"\n") == b.read_bytes().replace(b"\r\n", b"\n")


def main() -> int:
    check = "--check" in sys.argv[1:]
    if not check:
        for t in TARGETS:
            gen_ts(t, t.ts_out)
            gen_py(t, t.py_out)
            print("generated:", t.ts_out.relative_to(REPO), t.py_out.relative_to(REPO))
        return 0

    stale: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for t in TARGETS:
            tmp_ts = Path(tmp) / t.ts_out.name
            tmp_py = Path(tmp) / t.py_out.name
            gen_ts(t, tmp_ts)
            gen_py(t, tmp_py)
            stale += [str(dst.relative_to(REPO)) for fresh, dst in ((tmp_ts, t.ts_out), (tmp_py, t.py_out)) if not same(fresh, dst)]
    if stale:
        print("stale or hand-edited generated files:", *stale, sep="\n  ")
        print("run `pnpm contract:gen`")
        return 1
    print("generated files are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
