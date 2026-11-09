"""Confam verification engine.

STUB for matching: an exact match confirms (with superseded_by when the notice was
replaced), everything else is cannot_confirm / not_in_record, never not_official.
The comparison primitives (compare/: tokenizer and diff) are real and are used to
describe what a replacing notice changed. Full comparison (altered, partial,
allow-list, conflicts) comes next. See docs/ARCHITECTURE.md for the pipeline.
"""

from .check import check_notice, new_check_code
from .model import OfficialNotice, RecordError, Replacement
from .supersession import latest_successor, supersession_for

__all__ = [
    "OfficialNotice",
    "RecordError",
    "Replacement",
    "check_notice",
    "latest_successor",
    "new_check_code",
    "supersession_for",
]
