"""Confam verification engine.

STUB. The tested engine will be ported here later (CLAUDE.md: "keep its behaviour").
Until then this package covers two branches so the rule-1 and rule-2 regression
tests have something to run against: an exact match (confirmed, with
superseded_by when the notice was replaced) and everything else
(cannot_confirm / not_in_record, never not_official).

See docs/ARCHITECTURE.md for the pipeline (cache, OCR, find notice, compare,
meaning rules, allow-list, supersession, explain, render); only supersession and
a minimal match exist here.
"""

from .check import OfficialNotice, Replacement, check_notice, new_check_code

__all__ = ["OfficialNotice", "Replacement", "check_notice", "new_check_code"]
