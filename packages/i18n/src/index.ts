import { en, type Strings, type VerdictCopy } from "./en";

export type Lang = "en" | "pcm" | "ha" | "yo" | "ig";
export type { Strings, VerdictCopy };

/**
 * Returns the strings for a language. Only English exists today, so other
 * languages get English with `draft: true` (the UI shows a "Draft translation"
 * label). TODO: pcm, ha, yo, ig strings, then native-speaker review.
 */
export function getStrings(lang: Lang): { s: Strings; draft: boolean } {
  return { s: en, draft: lang !== "en" };
}

/** Fill {placeholders} in a template. */
export function fill(template: string, values: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? "");
}
