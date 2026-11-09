import { describe, expect, it } from "vitest";
import {
  LANGS,
  LANGUAGES,
  REQUIRED_GLYPHS,
  fill,
  fillParts,
  getStrings,
  pickLang,
  intlLocale,
  isLang,
  localeStatus,
  type Lang,
} from "@confam/i18n";

function leaves(obj: unknown, prefix = "", out: [string, string][] = []): [string, string][] {
  if (typeof obj === "string") out.push([prefix, obj]);
  else if (Array.isArray(obj)) obj.forEach((v, i) => leaves(v, `${prefix}[${i}]`, out));
  else if (obj && typeof obj === "object")
    for (const [k, v] of Object.entries(obj)) leaves(v, prefix ? `${prefix}.${k}` : k, out);
  return out;
}

const placeholders = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
const strings = (lang: Lang) => getStrings(lang).s;
const english = new Map(leaves(strings("en")));

describe("locales", () => {
  it("has exactly the five languages", () => {
    expect([...LANGS]).toEqual(["en", "pcm", "ha", "yo", "ig"]);
    expect(LANGUAGES.map((l) => l.code)).toEqual([...LANGS]);
  });

  it.each(LANGS.filter((l) => l !== "en"))("%s has exactly the same keys as English", (lang) => {
    const keys = leaves(strings(lang)).map(([k]) => k);
    expect(keys).toEqual([...english.keys()]);
  });

  it.each(LANGS)("%s: every string is non-empty and keeps the same {placeholders} as English", (lang) => {
    for (const [key, value] of leaves(strings(lang))) {
      expect(value.trim().length, `${lang} ${key} is empty`).toBeGreaterThan(0);
      expect(placeholders(value), `${lang} ${key}`).toEqual(placeholders(english.get(key)!));
    }
  });

  it.each(LANGS)("%s: every string is NFC-normalised, so letters and tone marks survive", (lang) => {
    for (const [key, value] of leaves(strings(lang))) {
      expect(value.normalize("NFC") === value, `${lang} ${key}`).toBe(true);
    }
  });

  it.each(LANGS)("%s: no percentages, grades, scores or confidence (rule 4)", (lang) => {
    for (const [key, value] of leaves(strings(lang))) {
      expect(value, `${lang} ${key}`).not.toMatch(/%|percent|confidence|score|grade|probab/i);
    }
  });

  it.each(["pcm", "ha", "yo", "ig"] as const)("%s is an unreviewed draft, never 'reviewed'", (lang) => {
    expect(localeStatus[lang]).toBe("draft");
    expect(getStrings(lang).draft).toBe(true);
  });

  it("English is the source and is not a draft", () => {
    expect(localeStatus.en).toBe("source");
    expect(getStrings("en").draft).toBe(false);
  });

  it("the independence line is translated for every language and names INEC (rule 10)", () => {
    for (const lang of LANGS) expect(strings(lang).independence).toContain("INEC");
    expect(strings("en").independence).toBe("Independent checker. Not INEC or any party.");
  });

  it("official names are never translated", () => {
    for (const lang of LANGS) {
      expect(strings(lang).home.samplesNote).toContain("Simulated Electoral Commission");
    }
  });
});

describe("required letters are really in the drafts (they must render)", () => {
  // lower-cased: a capital Ṅ / Ɓ / Ị is the same letter and must render just as well
  const all = (lang: Lang) =>
    leaves(strings(lang))
      .map(([, v]) => v)
      .join("\n")
      .toLowerCase();

  it.each(["ɓ", "ɗ", "ƙ"])("Hausa uses %s", (ch) => {
    expect(all("ha")).toContain(ch);
  });
  it.each(["ẹ", "ọ", "ṣ"])("Yoruba uses %s", (ch) => {
    expect(all("yo")).toContain(ch);
  });
  it("Yoruba uses tone marks: grave, acute and the dot-below letters combined", () => {
    const text = all("yo").normalize("NFD");
    expect(text).toMatch(/̀/); // grave
    expect(text).toMatch(/́/); // acute
    expect(text).toMatch(/[eo]̣[̀́]/); // dotted letter + tone mark
  });
  it.each(["ị", "ọ", "ụ", "ṅ"])("Igbo uses %s", (ch) => {
    expect(all("ig")).toContain(ch);
  });

  it("REQUIRED_GLYPHS lists them, and every one is present in its language", () => {
    for (const lang of ["ha", "yo", "ig"] as const) {
      for (const ch of REQUIRED_GLYPHS[lang]) expect(all(lang), `${lang} ${ch}`).toContain(ch);
    }
  });
});

describe("helpers", () => {
  it("isLang accepts only the five codes", () => {
    for (const l of LANGS) expect(isLang(l)).toBe(true);
    for (const bad of ["fr", "EN", "", undefined, null, "en-GB", "pcm "]) expect(isLang(bad)).toBe(false);
  });

  it("pickLang: ?lang beats the cookie, junk is ignored, default is English", () => {
    expect(pickLang("ha", "yo")).toBe("ha");
    expect(pickLang(null, "yo")).toBe("yo");
    expect(pickLang("xx", "yo")).toBe("yo");
    expect(pickLang("xx", "zz")).toBe("en");
    expect(pickLang(undefined, undefined)).toBe("en");
  });

  it("fillParts marks which pieces are quoted values", () => {
    expect(fillParts("Says “{copy}” not “{official}”.", { copy: "15th", official: "14th" })).toEqual([
      { text: "Says “", value: false },
      { text: "15th", value: true },
      { text: "” not “", value: false },
      { text: "14th", value: true },
      { text: "”.", value: false },
    ]);
  });

  it("fill replaces placeholders and leaves nothing behind", () => {
    expect(fill("{copy} → {official}", { copy: "14th", official: "28th" })).toBe("14th → 28th");
  });

  it("each language has a Intl locale that formats a date", () => {
    for (const lang of LANGS) {
      const out = new Intl.DateTimeFormat(intlLocale(lang), { dateStyle: "medium", timeZone: "UTC" }).format(
        new Date("2026-10-09T00:00:00Z"),
      );
      expect(out).toMatch(/2026/);
    }
  });
});
