"""Hand-written helper (not generated). Serialise a Verdict exactly as the contract says.

Two traps in the generated model: `copy` is stored as `copy_` (alias `copy`), and an
absent optional `box` would dump as null, which the schema rejects. Always use this
function for anything that leaves the process.
"""

from __future__ import annotations

from typing import Any

from .verdict import Verdict


def verdict_to_json(verdict: Verdict) -> dict[str, Any]:
    payload = verdict.model_dump(mode="json", by_alias=True)
    for change in payload["changes"]:
        for optional in ("box", "placement"):
            if change.get(optional) is None:
                change.pop(optional, None)
    return payload
