"""Word lists per language. English only for now.

TODO: pcm, ha, yo, ig. Notices are quoted in their own language, so the engine needs
month, weekday and negation words for each language a notice may be written in.
"""

from __future__ import annotations

MONTHS: dict[str, int] = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sept": 9, "sep": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}

# Negations always change meaning (CLAUDE.md meaning rules). Apostrophes are straightened first.
NEGATIONS = {
    "not", "no", "never", "cannot", "cant", "can't", "dont", "don't", "wont", "won't",
    "without", "none", "nobody", "nothing", "neither", "nor", "isnt", "isn't", "arent",
    "aren't", "doesnt", "doesn't", "didnt", "didn't", "wasnt", "wasn't", "shouldnt", "shouldn't",
}
