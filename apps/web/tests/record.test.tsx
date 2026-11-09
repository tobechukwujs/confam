import { render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { Verdict } from "@confam/contract";
import { getStrings } from "@confam/i18n";
import { RecordEntryView, RecordIndexView } from "@/components/record/RecordViews";
import { Receipt } from "@/components/sheet/Receipt";
import { isRealSourceUrl } from "@/lib/format";
import type { RecordEntry, RecordList } from "@/lib/record-types";

const { s } = getStrings("en");
const fixtures = (name: string) =>
  JSON.parse(readFileSync(path.resolve(__dirname, "../../../fixtures/sec-sim", name), "utf8"));
const notices = fixtures("notices.json").notices as Array<
  RecordEntry & { superseded_by: { id: string; published: string } | null }
>;
const samples = fixtures("sample-verdicts.json") as Record<string, Verdict>;

const entry = (id: string): RecordEntry => notices.find((n) => n.id === id)!;
const list: RecordList = {
  record_as_of: fixtures("notices.json").record_as_of,
  notices: notices.map(({ id, title, published, lang, superseded_by }) => ({ id, title, published, lang, superseded_by })),
};

describe("isRealSourceUrl", () => {
  it.each([
    "https://newspaper.com.ng/notice",
    "https://www.somewhere.com.ng/page",
    "http://news.site.ng/a",
  ])("%s is a plausible real URL only when https", (url) => {
    expect(isRealSourceUrl(url)).toBe(url.startsWith("https://"));
  });

  it.each([
    "https://sec.example/notices/SEC-2026-114",
    "https://register.sec.example",
    "https://thing.test/x",
    "https://a.invalid/",
    "https://localhost:3000/x",
    "https://printer.local/x",
    "https://example.com/x",
    "https://www.example.org/x",
    "https://sub.example.net/x",
    "http://127.0.0.1/x",
    "not a url",
    "",
    "javascript:alert(1)",
    "ftp://files.somewhere.com/x",
  ])("%s is not shown as a source link", (url) => {
    expect(isRealSourceUrl(url)).toBe(false);
  });
});

describe("Receipt links", () => {
  it("'Open the original' goes to the record page in the same tab, so it never breaks", () => {
    render(<Receipt verdict={samples.confirmed!} s={s} lang="en" />);
    const link = screen.getByRole("link", { name: "Open the original" });
    expect(link).toHaveAttribute("href", "/record/SEC-2026-140");
    expect(link).not.toHaveAttribute("target");
  });

  it("no 'View source' link for a fictional .example address", () => {
    render(<Receipt verdict={samples.confirmed!} s={s} lang="en" />);
    expect(screen.queryByRole("link", { name: "View source" })).toBeNull();
  });

  it("'View source' appears, as a secondary link, only for a real https address", () => {
    const v = structuredClone(samples.confirmed!);
    v.notice!.url = "https://newspaper.com.ng/notice/1";
    render(<Receipt verdict={v} s={s} lang="en" />);
    const link = screen.getByRole("link", { name: "View source" });
    expect(link).toHaveAttribute("href", "https://newspaper.com.ng/notice/1");
    expect(link).toHaveAttribute("rel", expect.stringContaining("noopener"));
  });
});

describe("record index", () => {
  it("lists every notice, linked to its page, with replacement said in words", () => {
    render(<RecordIndexView list={list} s={s} lang="en" />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("The official record");
    for (const n of notices) {
      const link = screen.getByRole("link", { name: n.title });
      expect(link).toHaveAttribute("href", `/record/${n.id}`);
    }
    expect(screen.getByText(/Replaced by SEC-2026-140/)).toBeInTheDocument();
    expect(screen.getAllByText(/Current notice/)).toHaveLength(1);
  });

  it("has no badge or pill elements", () => {
    const { container } = render(<RecordIndexView list={list} s={s} lang="en" />);
    expect(container.querySelector('[class*="pill"], [class*="badge"]')).toBeNull();
  });

  it("is labelled as fictional sample content", () => {
    render(<RecordIndexView list={list} s={s} lang="en" />);
    expect(screen.getByText(/fictional Simulated Electoral Commission/i)).toBeInTheDocument();
  });
});

describe("record entry", () => {
  it("shows the exact signed text, word for word, in its own language", () => {
    const n = entry("SEC-2026-140");
    const { container } = render(<RecordEntryView entry={n} s={s} lang="en" />);
    const block = container.querySelector(".record-text") as HTMLElement;
    expect(block.textContent).toBe(n.text);
    expect(block).toHaveAttribute("lang", n.lang);
  });

  it("shows title, id, published date, and who signed it and when", () => {
    const n = entry("SEC-2026-114");
    const { container } = render(<RecordEntryView entry={n} s={s} lang="en" />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(n.title);
    expect(container.textContent).toContain("SEC-2026-114");
    expect(container.textContent).toMatch(/3 Sep\w* 2026/);
    const sigs = container.querySelectorAll(".signatures li");
    expect(sigs).toHaveLength(2);
    expect(sigs[0]).toHaveTextContent("First signature");
    expect(sigs[0]).toHaveTextContent("Reviewer A (sample)");
    expect(sigs[1]).toHaveTextContent("Second signature");
    expect(sigs[1]).toHaveTextContent("Reviewer B (sample)");
    expect(sigs[0]).toHaveTextContent(/4 Sep\w* 2026, 10:15 WAT/);
  });

  it("a replaced notice links to the notice that replaced it", () => {
    render(<RecordEntryView entry={entry("SEC-2026-114")} s={s} lang="en" />);
    const link = screen.getByRole("link", { name: /SEC-2026-140/ });
    expect(link).toHaveAttribute("href", "/record/SEC-2026-140");
  });

  it("a current notice says so and has no replacement link", () => {
    const { container } = render(<RecordEntryView entry={entry("SEC-2026-140")} s={s} lang="en" />);
    expect(screen.getByText("Current notice")).toBeInTheDocument();
    expect(within(container).queryByRole("link", { name: /Replaced by/ })).toBeNull();
  });

  it("'View source' is absent for a fictional address and present for a real one", () => {
    const fake = render(<RecordEntryView entry={entry("SEC-2026-140")} s={s} lang="en" />);
    expect(screen.queryByRole("link", { name: "View source" })).toBeNull();
    fake.unmount();
    render(<RecordEntryView entry={{ ...entry("SEC-2026-140"), url: "https://newspaper.com.ng/n/1" }} s={s} lang="en" />);
    expect(screen.getByRole("link", { name: "View source" })).toHaveAttribute(
      "href",
      "https://newspaper.com.ng/n/1",
    );
  });
});
