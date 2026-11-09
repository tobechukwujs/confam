/* GENERATED from packages/contract/verdict.schema.json by `pnpm contract:gen`. DO NOT EDIT. Shape only: cross-field rules are in the schema. */

/**
 * The result of one Confam check. Source of truth for the TypeScript and Pydantic types: edit here, then run `pnpm contract:gen`. There is deliberately no confidence, score, grade or percentage field (CLAUDE.md rule 4). Cross-field rules live in `allOf` below; the generated Pydantic and TypeScript types describe shape only, so validate against this schema for the full contract.
 */
export interface Verdict {
  /**
   * Check code: 8 characters from the alphabet 23456789ABCDEFGHJKMNPQRSTUVWXYZ (no 0, O, 1, I, L). Stored and sent as 8 characters; presentation inserts a hyphen as XXXX-XXXX.
   */
  code: string;
  verdict: "confirmed" | "altered" | "not_official" | "partial" | "cannot_confirm";
  /**
   * Why the engine cannot confirm. Non-null only when verdict is cannot_confirm, and required then.
   */
  reason: "unclear" | "not_in_record" | "no_fact" | "line_missing" | null;
  lang: "en" | "pcm" | "ha" | "yo" | "ig";
  checked_at: string;
  record_as_of: string;
  /**
   * The official notice the check was made against. Null only when verdict is cannot_confirm and reason is not_in_record or no_fact, or unclear because OCR read no usable text from a photo (the engine uses unclear with a null notice only then). Otherwise required.
   */
  notice: Notice | null;
  /**
   * Set when the matched notice has been replaced. Only on confirmed; null otherwise.
   */
  superseded_by: SupersededBy | null;
  changes: Change[];
  /**
   * Official facts the copy contradicts. Non-empty exactly when verdict is not_official; empty for every other verdict.
   */
  conflicts: Conflict[];
}
/**
 * This interface was referenced by `Verdict`'s JSON-Schema
 * via the `definition` "Notice".
 */
export interface Notice {
  id: string;
  title: string;
  published: string;
  url: string;
}
/**
 * The notice that replaced the matched one, and how it differs. In `changes`, `official` is the value in the NEW notice and `copy` is the value in the OLD (matched) notice, which is what the forwarded copy says.
 *
 * This interface was referenced by `Verdict`'s JSON-Schema
 * via the `definition` "SupersededBy".
 */
export interface SupersededBy {
  id: string;
  published: string;
  url: string;
  title: string;
  /**
   * Old notice versus the replacing notice. May be empty when the differences cannot be expressed as facts. No box: these come from record text, not a photo.
   */
  changes: RecordChange[];
}
/**
 * Same rules as Change, without `box`.
 *
 * This interface was referenced by `Verdict`'s JSON-Schema
 * via the `definition` "RecordChange".
 */
export interface RecordChange {
  op: "replace" | "insert" | "delete";
  kind: "date" | "time" | "weekday" | "number" | "money" | "link" | "phone" | "negation" | "text";
  official: string | null;
  copy: string | null;
}
/**
 * This interface was referenced by `Verdict`'s JSON-Schema
 * via the `definition` "Change".
 */
export interface Change {
  op: "replace" | "insert" | "delete";
  kind: "date" | "time" | "weekday" | "number" | "money" | "link" | "phone" | "negation" | "text";
  /**
   * The official wording. Null for insert (nothing in the record), a string otherwise.
   */
  official: string | null;
  /**
   * The forwarded copy's wording. Null for delete (nothing in the copy), a string otherwise.
   */
  copy: string | null;
  /**
   * Optional position on a photo from OCR: x, y, width, height, each 0 to 1. Absent for pasted text.
   *
   * @minItems 4
   * @maxItems 4
   */
  box?: [number, number, number, number];
}
/**
 * This interface was referenced by `Verdict`'s JSON-Schema
 * via the `definition` "Conflict".
 */
export interface Conflict {
  kind: "date" | "link" | "money";
  copy: string;
  official: string;
  quote: string;
}
