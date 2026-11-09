import { render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { Verdict } from "@confam/contract";
import { LANGS, LANGUAGES, REQUIRED_GLYPHS, getStrings, type Lang } from "@confam/i18n";
import { LangSwitch } from "@/components/LangSwitch";
import { RecordEntryView } from "@/components/record/RecordViews";
import { VerdictLayout } from "@/components/verdict/VerdictLayout";
import type { RecordEntry } from "@/lib/record-types";

const fixtures = (name: string) =>
  JSON.parse(readFileSync(path.resolve(__dirname, "../../../fixtures/sec-sim", name), "utf8"));
const samples = fixtures("sample-verdicts.json") as Record<string, Verdict>;
const notices = fixtures("notices.json").notices as RecordEntry[];

const view = (name: string, lang: Lang) =>
  render(<VerdictLayout verdict={samples[name]!} s={getStrings(lang).s} lang={lang} />);

describe("LangSwitch", () => {
  const props = { current: "yo" as Lang, path: "/v/A7T3R4ED", search: "", label: "Èdè" };

  it("wide screens: all five languages are links, in their own names, keeping the page", () => {
    const { container } = render(<LangSwitch {...props} />);
    const nav = container.querySelector("nav.lang-wide") as HTMLElement;
    const links = within(nav).getAllByRole("link");
    expect(links.map((a) => a.textContent)).toEqual(LANGUAGES.map((l) => l.name));
    expect(links.map((a) => a.getAttribute("href"))).toEqual(LANGS.map((l) => `/v/A7T3R4ED?lang=${l}`));
    expect(links.map((a) => a.getAttribute("lang"))).toEqual([...LANGS]);
  });

  it("marks the current language", () => {
    const { container } = render(<LangSwitch {...props} />);
    const current = container.querySelectorAll('nav.lang-wide a[aria-current="true"]');
    expect(current).toHaveLength(1);
    expect(current[0]).toHaveTextContent("Yorùbá");
  });

  it("phones: the current language is a summary that opens a row of all five", () => {
    const { container } = render(<LangSwitch {...props} />);
    const details = container.querySelector("details.lang-narrow") as HTMLDetailsElement;
    expect(details.querySelector("summary")).toHaveTextContent("Yorùbá");
    expect(details.open).toBe(false);
    expect(details.querySelectorAll("nav a")).toHaveLength(5);
  });

  it("keeps other query parameters and replaces ?lang", () => {
    const { container } = render(<LangSwitch {...props} path="/record" search="a=1&b=2" />);
    const first = container.querySelector("nav.lang-wide a") as HTMLAnchorElement;
    expect(first.getAttribute("href")).toBe("/record?a=1&b=2&lang=en");
  });
});

describe.each(LANGS)("interface in %s, official words untouched", (lang) => {
  const { s } = getStrings(lang);

  it("the verdict word, sentence and action are in the language", () => {
    const { container } = view("altered_replace", lang);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(s.verdict.altered.word);
    expect(container.querySelector(".answer")).toHaveTextContent(s.verdict.altered.sentence);
    expect(container.querySelector(".actions")).toHaveTextContent(s.verdict.altered.action);
  });

  it("the changed figure and the handwritten correction stay word for word, marked lang=en", () => {
    const { container } = view("altered_replace", lang);
    expect(container.querySelector(".figure")).toHaveTextContent("29th");
    expect(container.querySelector(".figure")).toHaveAttribute("lang", "en");
    expect(container.querySelector(".hand")).toHaveTextContent("28th");
    expect(container.querySelector(".hand")).toHaveAttribute("lang", "en");
  });

  it("quoted values in the list are lang=en spans inside interface words", () => {
    const { container } = view("altered_replace", lang);
    const row = container.querySelector("ol.changes li p") as HTMLElement;
    const quoted = [...row.querySelectorAll("span[lang]")].filter((n) => !n.classList.contains("kind"));
    expect(quoted.map((n) => n.textContent)).toEqual(["29th", "28th"]);
    expect(quoted.every((n) => n.getAttribute("lang") === "en")).toBe(true);
    // and the paragraph itself is NOT forced to English
    expect(row.getAttribute("lang")).toBeNull();
  });

  it("a not-official claim and the official link are never translated", () => {
    const { container } = view("not_official", lang);
    expect(container.querySelector(".claim")).toHaveTextContent("https://register-sec.example");
    expect(container.querySelector(".hand")).toHaveTextContent("https://register.sec.example");
  });

  it("the replaced screen keeps both dates in English; 'now' is interface text outside the hand", () => {
    const { container } = view("replaced", lang);
    expect(container.querySelector(".figure-main")).toHaveTextContent("14th");
    expect(container.querySelector(".hand")).toHaveTextContent("28th November");
    expect(container.querySelector(".hand")).toHaveAttribute("lang", "en");
    expect(container.querySelector(".now-label")).toHaveTextContent(s.changes.now);
    expect(container.querySelector(".hand")?.textContent).not.toContain(s.changes.now);
  });

  it("the signed record text is quoted exactly, in the notice's own language", () => {
    const notice = notices.find((n) => n.id === "SEC-2026-140")!;
    const { container } = render(<RecordEntryView entry={notice} s={s} lang={lang} />);
    const block = container.querySelector(".record-text") as HTMLElement;
    expect(block.textContent).toBe(notice.text);
    expect(block).toHaveAttribute("lang", "en");
    expect(screen.getByText(s.record.textHeading)).toBeInTheDocument();
  });

  it("every rendered character survives, already NFC", () => {
    const { container } = view("replaced", lang);
    const text = container.textContent ?? "";
    expect(text.normalize("NFC")).toBe(text);
    expect(text).toContain(s.verdict.replaced.word);
    expect(text).toContain(s.receipt.heading);
  });
});

describe("letters survive rendering", () => {
  // Several screens per language, so the dotted and hooked letters are really on the page.
  const SCREENS = ["confirmed", "replaced", "altered_replace", "not_official", "partial", "not_in_record"];

  it.each(["ha", "yo", "ig"] as const)("%s: its required letters appear in rendered screens", (lang) => {
    let all = "";
    for (const name of SCREENS) {
      const { container, unmount } = view(name, lang);
      all += container.textContent;
      unmount();
    }
    all = all.toLowerCase();
    for (const ch of REQUIRED_GLYPHS[lang]) {
      // ṅ is only in the home form's message, so check it there instead
      if (lang === "ig" && ch === "ṅ") continue;
      expect(all, `${lang} ${ch}`).toContain(ch);
    }
  });

  it("Yoruba tone marks survive as combining sequences", () => {
    const { container } = view("replaced", "yo");
    const nfd = (container.textContent ?? "").normalize("NFD");
    expect(nfd).toMatch(/[eo]̣[̀́]/);
    expect(nfd).toMatch(/́/);
    expect(nfd).toMatch(/̀/);
  });
});

describe("dates follow the page language; official ids do not", () => {
  it("receipt dates are formatted for each language without breaking", () => {
    for (const lang of LANGS) {
      const { container, unmount } = view("replaced", lang);
      const receipt = container.querySelector(".receipt") as HTMLElement;
      expect(receipt.textContent).toMatch(/2026/);
      expect(receipt.textContent).toContain("SEC-2026-114");
      expect(receipt.textContent).toContain("SEC-2026-140");
      unmount();
    }
  });
});
