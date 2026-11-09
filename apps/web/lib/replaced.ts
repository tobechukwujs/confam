import type { RecordChange, Verdict } from "@confam/contract";

/**
 * The change shown as the big marked figure on a "Real, but replaced" screen: the
 * first meaningful one (a date, figure, link...) rather than a run of ordinary words.
 * `index` is its row number in the list, so its pin pairs with that row.
 */
export function pickReplacedChange(v: Verdict): { change: RecordChange; index: number } | null {
  const changes = v.superseded_by?.changes ?? [];
  if (changes.length === 0) return null;
  const meaningful = (c: RecordChange) => c.kind !== "text";
  const index =
    changes.findIndex((c) => meaningful(c) && c.op === "replace") >= 0
      ? changes.findIndex((c) => meaningful(c) && c.op === "replace")
      : changes.findIndex(meaningful) >= 0
        ? changes.findIndex(meaningful)
        : 0;
  return { change: changes[index]!, index };
}

/** "14th November" -> day big, month small. Anything else is shown as one piece. */
export function splitDate(value: string): { main: string; rest: string } | null {
  const m = /^(\d{1,2}(?:st|nd|rd|th)?)(\s+(?:of\s+)?[A-Za-z][A-Za-z.]*(?:,?\s+\d{4})?)$/.exec(value.trim());
  return m ? { main: m[1]!, rest: m[2]! } : null;
}
