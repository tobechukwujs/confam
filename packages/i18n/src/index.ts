import { en, type Strings, type VerdictCopy } from "./en";
import { ha } from "./ha";
import { ig } from "./ig";
import { pcm } from "./pcm";
import { yo } from "./yo";

export type { Strings, VerdictCopy };

export const LANGS = ["en", "pcm", "ha", "yo", "ig"] as const;
export type Lang = (typeof LANGS)[number];

/** Names are written in their own language, so a reader can always find theirs. */
export const LANGUAGES: { code: Lang; name: string }[] = [
  { code: "en", name: "English" },
  { code: "pcm", name: "Pidgin" },
  { code: "ha", name: "Hausa" },
  { code: "yo", name: "Yorùbá" },
  { code: "ig", name: "Igbo" },
];

/**
 * English is the source. Every other locale is an UNREVIEWED DRAFT until a native speaker
 * signs it off (CLAUDE.md). Change a locale to "reviewed" only after that sign-off.
 */
export const localeStatus: Record<Lang, "source" | "draft" | "reviewed"> = {
  en: "source",
  pcm: "draft",
  ha: "draft",
  yo: "draft",
  ig: "draft",
};

/** Letters each language must be able to show (Andika latin-ext; never the hand font). */
export const REQUIRED_GLYPHS = {
  ha: ["ɓ", "ɗ", "ƙ"],
  yo: ["ẹ", "ọ", "ṣ"],
  ig: ["ị", "ọ", "ụ", "ṅ"],
} as const;

const LOCALES: Record<Lang, Strings> = { en, pcm, ha, yo, ig };

export function isLang(value: unknown): value is Lang {
  return typeof value === "string" && (LANGS as readonly string[]).includes(value);
}

export function getStrings(lang: Lang): { s: Strings; draft: boolean } {
  return { s: LOCALES[lang], draft: localeStatus[lang] !== "reviewed" && localeStatus[lang] !== "source" };
}

/** Locale tag for Intl date formatting. English keeps en-GB (day month year). */
export function intlLocale(lang: Lang): string {
  const tag = lang === "en" ? "en-GB" : lang;
  return Intl.DateTimeFormat.supportedLocalesOf([tag]).length > 0 ? tag : "en-GB";
}

/**
 * Pick the interface language. An explicit ?lang= wins over the saved cookie; anything
 * that is not one of the five codes is ignored. Default English.
 */
export function pickLang(query: string | null | undefined, cookie: string | null | undefined): Lang {
  if (isLang(query)) return query;
  if (isLang(cookie)) return cookie;
  return "en";
}

/** Fill {placeholders} in a template. */
export function fill(template: string, values: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => values[key] ?? "");
}

/** Split a template into plain interface text and filled values, so values can be marked up. */
export function fillParts(
  template: string,
  values: Record<string, string>,
): { text: string; value: boolean }[] {
  const parts: { text: string; value: boolean }[] = [];
  let last = 0;
  for (const m of template.matchAll(/\{(\w+)\}/g)) {
    if (m.index! > last) parts.push({ text: template.slice(last, m.index), value: false });
    parts.push({ text: values[m[1]!] ?? "", value: true });
    last = m.index! + m[0].length;
  }
  if (last < template.length) parts.push({ text: template.slice(last), value: false });
  return parts;
}
