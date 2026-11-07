"""Confam verification engine.

STUB. The tested engine will be ported here later (CLAUDE.md: "keep its behaviour").
Until then this package covers exactly one branch, so the rule-1 regression test
has something to run against: no match and no conflicting official fact returns
cannot_confirm / not_in_record, never not_official.

TODO(ARCHITECTURE.md): pipeline order (cache, OCR, find notice, compare, meaning
rules, allow-list, supersession, explain, render) is not implemented here.
"""

from .check import OfficialNotice, check_notice, new_check_code

__all__ = ["OfficialNotice", "check_notice", "new_check_code"]
