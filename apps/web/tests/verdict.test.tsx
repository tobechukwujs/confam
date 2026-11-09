import { render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { Verdict } from "@confam/contract";
import { getStrings, type Strings } from "@confam/i18n";
import { VerdictLayout } from "@/components/verdict/VerdictLayout";
import { formatCode, viewKey } from "@/lib/format";

const raw = JSON.parse(
  readFileSync(path.resolve(__dirname, "../../../fixtures/sec-sim/sample-verdicts.json"), "utf8"),
) as Record<string, unknown>;
const samples = Object.entries(raw).filter(([k]) => !k.startsWith("_")) as [string, Verdict][];
const { s } = getStrings("en");

function renderSample(v: Verdict) {
  return render(<VerdictLayout verdict={v} s={s} />);
}
const sample = (name: string) => samples.find(([k]) => k === name)![1];

function allStrings(obj: unknown, out: string[] = []): string[] {
  if (typeof obj === "string") out.push(obj);
  else if (Array.isArray(obj)) obj.forEach((o) => allStrings(o, out));
  else if (obj && typeof obj === "object") Object.values(obj).forEach((o) => allStrings(o, out));
  return out;
}

describe("verdict views", () => {
  it.each(samples)("%s renders its verdict word, an h1, and the receipt", (_name, v) => {
    renderSample(v);
    const key = viewKey(v);
    const expected =
      key === "cannot_confirm"
        ? s.verdict.cannot_confirm[v.reason ?? "not_in_record"].word
        : s.verdict[key].word;
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(expected);
    expect(screen.getByText(formatCode(v.code))).toBeInTheDocument();
    expect(screen.getByRole("link", { name: s.receipt.verify })).toHaveAttribute("href", `/v/${v.code}`);
  });

  it.each(samples)("%s: every change has a row in the list, and pins never outnumber rows", (_n, v) => {
    const { container } = renderSample(v);
    const rows = container.querySelectorAll("ol.changes li");
    expect(rows.length).toBe(v.changes.length + v.conflicts.length + (v.superseded_by?.changes.length ?? 0));
    const stagePins = container.querySelectorAll(".stage [data-pin]");
    expect(stagePins.length).toBeLessThanOrEqual(rows.length);
  });

  it("confirmed shows a green tick", () => {
    const { container } = renderSample(sample("confirmed"));
    expect(container.querySelector('[data-mark="tick"]')).toHaveClass("tone-green");
  });

  it("a replaced notice never gets a plain green tick (rule 2)", () => {
    const { container } = renderSample(sample("replaced"));
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Real, but replaced");
    expect(screen.getByRole("heading", { level: 1 })).not.toHaveTextContent(/^Confirmed$/);
    expect(container.querySelector('[data-mark="tick"]')).toBeNull();
    expect(container.querySelector(".tone-green")).toBeNull();
    expect(container.querySelector('[data-mark="bracket"]')).toHaveClass("tone-pencil");
  });

  it("replaced shows the changed fact, not notice ids: old value bracketed, new value handwritten", () => {
    const { container } = renderSample(sample("replaced"));
    const stage = container.querySelector(".stage") as HTMLElement;
    expect(stage.textContent).not.toMatch(/SEC-/);
    // old value from the copy, in pencil brackets, day big and month small
    expect(stage.querySelector(".figure-main")).toHaveTextContent("14th");
    expect(stage.querySelector(".figure-sub")).toHaveTextContent("November");
    expect(stage.querySelector('[data-mark="bracket"]')).toHaveClass("tone-pencil");
    // new value in the pencil hand, with "now" as interface text outside the hand font
    expect(stage.querySelector(".hand")).toHaveTextContent("28th November");
    expect(stage.querySelector(".hand")).toHaveClass("tone-pencil");
    expect(stage.querySelector(".hand")).toHaveAttribute("lang", "en");
    expect(stage.querySelector(".now-label")).toHaveTextContent("now");
    expect(stage.querySelector(".hand")?.textContent).not.toMatch(/now/);
    expect(stage.querySelector(".tone-red")).toBeNull();
  });

  it("replaced: the list says the copy matches an older notice, then lists each difference", () => {
    const { container } = renderSample(sample("replaced"));
    expect(screen.getByText(/Your copy matches an older official notice word for word/)).toBeInTheDocument();
    expect(screen.queryByText(/No differences found/)).toBeNull();
    const rows = container.querySelectorAll("ol.changes li");
    expect(rows).toHaveLength(2);
    expect(container.querySelector("ol.changes")?.textContent).toContain("Date: 14th November → 28th November");
    expect(container.querySelector("ol.changes")?.textContent).toContain("Added in the newer notice: “now”");
    // the stage pin pairs with the date row (row 2)
    expect(container.querySelector(".stage [data-pin]")).toHaveAttribute("data-pin", "2");
    expect(rows[1]!.querySelector("[data-pin]")).toHaveAttribute("data-pin", "2");
  });

  it("replaced: the receipt names the replacing notice and links to its record page", () => {
    renderSample(sample("replaced"));
    expect(screen.getByText("Replaced by")).toBeInTheDocument();
    const link = screen.getByRole("link", { name: "SEC-2026-140, published 9 Oct 2026" });
    expect(link).toHaveAttribute("href", "/record/SEC-2026-140");
  });

  it("replaced with no expressible changes shows no ids and says a newer notice replaced it", () => {
    const v = structuredClone(sample("replaced"));
    v.superseded_by!.changes = [];
    const { container } = renderSample(v);
    expect((container.querySelector(".stage") as HTMLElement).textContent).not.toMatch(/SEC-2026-140/);
    expect(screen.getByText(/A newer notice has replaced it/)).toBeInTheDocument();
    expect(container.querySelectorAll("ol.changes li")).toHaveLength(0);
  });

  it("altered replace rings the copy figure in red, with the official value above", () => {
    const { container } = renderSample(sample("altered_replace"));
    expect(container.querySelector('[data-mark="ring"]')).toHaveClass("tone-red");
    expect(container.querySelector(".figure")).toHaveTextContent("29th");
    expect(container.querySelector(".hand")).toHaveTextContent("28th");
  });

  it("altered insert strikes the added words; delete shows a caret", () => {
    const ins = renderSample(sample("altered_insert"));
    expect(ins.container.querySelector('[data-mark="strike"]')).toHaveClass("tone-red");
    ins.unmount();
    const del = renderSample(sample("altered_delete"));
    expect(del.container.querySelector('[data-mark="caret"]')).toHaveClass("tone-red");
    expect(del.container.querySelector(".hand")).toHaveTextContent("only");
  });

  it("not official crosses the sheet and writes the official fact", () => {
    const { container } = renderSample(sample("not_official"));
    expect(container.querySelector('[data-mark="cross"]')).toHaveClass("tone-red");
    expect(container.querySelector(".claim")).toHaveTextContent("https://sec-register.example.net");
    expect(container.querySelector(".hand")).toHaveTextContent("https://register.sec.example");
  });

  it("partial uses a pencil bracket; cannot confirm a pencil question mark, with no red", () => {
    const partial = renderSample(sample("partial"));
    expect(partial.container.querySelector('[data-mark="bracket"]')).toHaveClass("tone-pencil");
    partial.unmount();
    const unsure = renderSample(sample("not_in_record"));
    expect(unsure.container.querySelector('[data-mark="unsure"]')).toHaveClass("tone-pencil");
    expect(unsure.container.querySelector(".tone-red")).toBeNull();
    expect(screen.getByText(/does not mean it is fake/i)).toBeInTheDocument();
  });

  it("red appears only when a copy differs (quarantine rule)", () => {
    for (const [name, v] of samples) {
      const { container, unmount } = renderSample(v);
      const hasRed = container.querySelector(".tone-red") !== null;
      expect(hasRed, name).toBe(v.verdict === "altered" || v.verdict === "not_official");
      unmount();
    }
  });

  it("samples are labelled as fictional", () => {
    renderSample(sample("confirmed"));
    expect(screen.getByText(/fictional Simulated Electoral Commission/i)).toBeInTheDocument();
  });

  it("quoted notice words carry a lang attribute", () => {
    const { container } = renderSample(sample("altered_replace"));
    expect(container.querySelector(".figure")).toHaveAttribute("lang", "en");
    expect(container.querySelector(".hand")).toHaveAttribute("lang", "en");
  });

  it("the main action is a real button or link", () => {
    for (const [name, v] of samples) {
      const { container, unmount } = renderSample(v);
      const actions = container.querySelector(".actions") as HTMLElement;
      expect(actions.querySelector("button, a"), name).not.toBeNull();
      unmount();
    }
  });
});

describe("strings (rule 4: no scores)", () => {
  it("contains no percentages, grades, scores or confidence", () => {
    for (const str of allStrings(s as Strings)) {
      expect(str).not.toMatch(/%|percent|confidence|score|grade|probab/i);
    }
  });

  it("never calls an unknown notice fake as a verdict word", () => {
    const words = Object.values(s.verdict.cannot_confirm).map((c) => c.word);
    for (const w of words) expect(w.toLowerCase()).not.toMatch(/fake|not official/);
  });
});

describe("format", () => {
  it("formats the stored code as XXXX-XXXX (display only)", () => {
    expect(formatCode("K7Q2M9XA")).toBe("K7Q2-M9XA");
  });
});
