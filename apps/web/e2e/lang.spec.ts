import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";
const LANGS = ["en", "pcm", "ha", "yo", "ig"] as const;
const VIEWPORT_HEIGHT = 640;

// Codes match fixtures/sec-sim/sample-verdicts.json (fictional notices).
const SAMPLES: [string, string][] = [
  ["confirmed", "C4NF7RM2"],
  ["replaced", "R3P7ACED"],
  ["altered replace", "A7T3R4ED"],
  ["altered insert", "A2NS3RTX"],
  ["altered delete", "DX7K9PQA"],
  ["not official", "N9T6FFC7"],
  ["partial", "P4RT7A2K"],
  ["cannot confirm: not in record", "U5KN7WN3"],
  ["cannot confirm: unclear", "UNC7EAR2"],
];

const htmlLang = (page: Page) => page.locator("html").getAttribute("lang");

test.describe("choosing a language", () => {
  test("?lang= switches the whole screen, sets <html lang> and shows the draft label", async ({ page }) => {
    await page.goto("/?lang=ha");
    expect(await htmlLang(page)).toBe("ha");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Wannan sanarwar gaskiya ce?");
    await expect(page.locator(".draft-label")).toHaveText("Fassarar gwaji");
    await expect(page.getByText("Mai bincike mai zaman kansa. Ba INEC ko wata jam'iyya ba ce.")).toBeVisible();
  });

  test("English has no draft label and says the independence line in English", async ({ page }) => {
    await page.goto("/?lang=en");
    expect(await htmlLang(page)).toBe("en");
    await expect(page.locator(".draft-label")).toHaveCount(0);
    await expect(page.getByText("Independent checker. Not INEC or any party.")).toBeVisible();
  });

  test("the choice is remembered in a cookie across pages, and ?lang= overrides it", async ({ page }) => {
    await page.goto("/?lang=yo");
    await page.goto("/record"); // no ?lang=
    expect(await htmlLang(page)).toBe("yo");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Ìwé àkọsílẹ̀ àṣẹ");
    await page.goto("/record?lang=ig"); // explicit choice wins and is remembered
    expect(await htmlLang(page)).toBe("ig");
    await page.goto("/");
    expect(await htmlLang(page)).toBe("ig");
    await page.goto("/?lang=en");
    await page.goto("/record");
    expect(await htmlLang(page)).toBe("en");
  });

  test("an unknown ?lang= is ignored", async ({ page }) => {
    await page.goto("/?lang=fr");
    expect(await htmlLang(page)).toBe("en");
    await page.goto("/?lang=ha");
    await page.goto("/?lang=fr"); // junk does not wipe a saved choice
    expect(await htmlLang(page)).toBe("ha");
  });

  test("the cookie holds only the language code", async ({ page, context }) => {
    await page.goto("/?lang=pcm");
    const cookies = await context.cookies();
    const c = cookies.find((x) => x.name === "confam_lang")!;
    expect(c.value).toBe("pcm");
    expect(c.sameSite).toBe("Lax");
    expect(cookies.map((x) => x.name)).toEqual(["confam_lang"]);
  });
});

test.describe("the language switch", () => {
  test("phones: the current language opens a row of all five", async ({ page }) => {
    await page.goto("/?lang=ha");
    const summary = page.locator("details.lang-narrow summary");
    await expect(summary).toBeVisible();
    await expect(summary).toContainText("Hausa");
    await expect(page.locator("nav.lang-wide")).toBeHidden();
    await expect(page.locator("details.lang-narrow nav a")).toHaveCount(5);
    await expect(page.locator("details.lang-narrow nav a").first()).toBeHidden(); // closed
    await summary.click();
    for (const name of ["English", "Pidgin", "Hausa", "Yorùbá", "Igbo"]) {
      await expect(page.locator("details.lang-narrow nav").getByRole("link", { name })).toBeVisible();
    }
    await page.locator("details.lang-narrow nav").getByRole("link", { name: "Igbo" }).click();
    await expect(page).toHaveURL(/lang=ig/);
    expect(await htmlLang(page)).toBe("ig");
  });

  test("the switch tap targets are at least 44px", async ({ page }) => {
    await page.goto("/");
    await page.locator("details.lang-narrow summary").click();
    const boxes = await page.locator("details.lang-narrow nav a").evaluateAll((els) =>
      els.map((e) => e.getBoundingClientRect().height),
    );
    for (const h of boxes) expect(h).toBeGreaterThanOrEqual(44);
  });

  test("the language links keep the page you are on", async ({ page }) => {
    await page.goto("/v/A7T3R4ED");
    await page.locator("details.lang-narrow summary").click();
    await page.locator("details.lang-narrow nav").getByRole("link", { name: "Yorùbá" }).click();
    await expect(page).toHaveURL(/\/v\/A7T3R4ED\?lang=yo$/);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("A ti yí i padà");
  });
});

test.describe("wide screens", () => {
  test.use({ viewport: { width: 1100, height: 700 }, isMobile: false });

  test("all five languages are visible in the header", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("details.lang-narrow")).toBeHidden();
    const nav = page.locator("nav.lang-wide");
    for (const name of ["English", "Pidgin", "Hausa", "Yorùbá", "Igbo"]) {
      await expect(nav.getByRole("link", { name })).toBeVisible();
    }
    await nav.getByRole("link", { name: "Hausa" }).click();
    expect(await htmlLang(page)).toBe("ha");
    await expect(nav.getByRole("link", { name: "Hausa" })).toHaveAttribute("aria-current", "true");
  });
});

test.describe("official words are never translated", () => {
  for (const lang of LANGS) {
    test(`${lang}: quotes stay word for word and carry lang=en`, async ({ page }) => {
      await page.goto(`/v/A7T3R4ED?lang=${lang}`);
      expect(await htmlLang(page)).toBe(lang);
      await expect(page.locator(".figure")).toHaveText("29th");
      await expect(page.locator(".figure")).toHaveAttribute("lang", "en");
      await expect(page.locator(".hand")).toHaveText("28th");
      await expect(page.locator(".hand")).toHaveAttribute("lang", "en");
      const quoted = page.locator("ol.changes li p span[lang=en]");
      await expect(quoted.first()).toHaveText("29th");
      await expect(quoted.nth(1)).toHaveText("28th");
    });
  }

  test("the signed record text is identical in every language", async ({ page }) => {
    const texts = new Set<string>();
    for (const lang of LANGS) {
      await page.goto(`/record/SEC-2026-140?lang=${lang}`);
      await expect(page.locator(".record-text")).toHaveAttribute("lang", "en");
      texts.add((await page.locator(".record-text").textContent()) ?? "");
    }
    expect(texts.size).toBe(1);
    expect([...texts][0]).toContain("now closes on 28th November");
  });

  test("the replaced screen keeps both dates in English in Hausa", async ({ page }) => {
    await page.goto("/v/R3P7ACED?lang=ha");
    await expect(page.locator(".figure-main")).toHaveText("14th");
    await expect(page.locator(".hand")).toHaveText("28th November");
    await expect(page.locator(".now-label")).toHaveText("yanzu");
  });
});

test("the check carries the language the person is reading in", async ({ page, request }) => {
  await page.goto("/?lang=ha");
  await page.getByLabel("Rubutun sanarwar").fill("Collect your new ballot cards at the market square on Sunday.");
  await page.getByRole("button", { name: "Duba wannan sanarwar" }).click();
  await expect(page).toHaveURL(/\/v\/[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$/);
  const code = page.url().split("/v/")[1]!;
  const verdict = await (await request.get(`${API}/v1/verdicts/${code}`)).json();
  expect(verdict.lang).toBe("ha");
  expect(verdict.verdict).toBe("cannot_confirm");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Ba mu iya tabbatarwa ba");
});

test("the share link carries ?lang= so the receiver sees the same language", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]).catch(() => {});
  await page.addInitScript(() => {
    // force the clipboard path (no native share sheet in a test)
    Object.defineProperty(navigator, "share", { value: undefined });
    (window as unknown as { __copied: string }).__copied = "";
    navigator.clipboard.writeText = async (t: string) => {
      (window as unknown as { __copied: string }).__copied = t;
    };
  });
  await page.goto("/v/C4NF7RM2?lang=yo");
  await page.getByRole("button", { name: "Pín in pẹ̀lú àyẹ̀wò yìí" }).click();
  await expect(page.getByRole("status")).toContainText("A ti dà á kọ");
  const copied = await page.evaluate(() => (window as unknown as { __copied: string }).__copied);
  expect(copied).toContain("/v/C4NF7RM2");
  expect(copied).toContain("lang=yo");
});

test.describe("letters render in the interface font, not a fallback", () => {
  // Ask Chrome which fonts actually drew the text. A glyph Andika lacks would fall to a
  // system font (isCustomFont false). The hand font is custom too but is only used for values.
  async function fontsFor(page: Page, selector: string) {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("DOM.enable");
    await cdp.send("CSS.enable");
    const { root } = await cdp.send("DOM.getDocument", { depth: 0 });
    const { nodeIds } = await cdp.send("DOM.querySelectorAll", { nodeId: root.nodeId, selector });
    const used: { familyName: string; isCustomFont: boolean; glyphCount: number }[] = [];
    for (const nodeId of nodeIds) {
      const { fonts } = await cdp.send("CSS.getPlatformFontsForNode", { nodeId });
      used.push(...fonts);
    }
    return used;
  }

  for (const [lang, selector] of [
    ["ha", ".answer p, .answer h1, ol.changes li p, .receipt dt"],
    ["yo", ".answer p, .answer h1, ol.changes li p, .receipt dt"],
    ["ig", ".answer p, .answer h1, ol.changes li p, .receipt dt"],
  ] as const) {
    test(`${lang}: every glyph is drawn by Andika`, async ({ page }) => {
      await page.goto(`/v/R3P7ACED?lang=${lang}`);
      await page.evaluate(() => document.fonts.ready);
      const used = await fontsFor(page, selector);
      expect(used.length).toBeGreaterThan(0);
      const fallbacks = used.filter((f) => !f.isCustomFont);
      expect(fallbacks, `system fallback fonts drew ${JSON.stringify(fallbacks)}`).toEqual([]);
      expect(used.every((f) => /andika/i.test(f.familyName)), JSON.stringify(used)).toBe(true);
    });
  }

  test("Hausa, Yoruba and Igbo home screens also use only Andika", async ({ page }) => {
    for (const lang of ["ha", "yo", "ig"]) {
      await page.goto(`/?lang=${lang}`);
      await page.evaluate(() => document.fonts.ready);
      const used = await fontsFor(page, "h1, p, label, button, .error, .cover, footer");
      const bad = used.filter((f) => !f.isCustomFont || !/andika/i.test(f.familyName));
      expect(bad, `${lang}: ${JSON.stringify(bad)}`).toEqual([]);
    }
  });
});

test.describe("One Screen Rule at 360x640, in every language", () => {
  for (const lang of LANGS) {
    for (const [name, code] of SAMPLES) {
      test(`${lang} / ${name}`, async ({ page }) => {
        await page.goto(`/v/${code}?lang=${lang}`);
        await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

        for (const selector of [
          "h1",
          ".stage, .stage-tick",
          ".answer > p:nth-of-type(1)",
          ".answer > p:nth-of-type(2)",
          ".actions .btn",
        ]) {
          const box = await page.locator(selector).first().boundingBox();
          expect(box, selector).not.toBeNull();
          expect(box!.y + box!.height, `${selector} must end above ${VIEWPORT_HEIGHT}px`).toBeLessThanOrEqual(
            VIEWPORT_HEIGHT,
          );
        }
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
        );
        expect(overflow, "no horizontal scroll").toBeLessThanOrEqual(0);

        // the cover (with the draft label and language menu) never grows past two lines
        const cover = await page.locator(".cover").boundingBox();
        expect(cover!.height).toBeLessThanOrEqual(64);
        // the draft label fits inside the cover
        if (lang !== "en") {
          const label = await page.locator(".draft-label").boundingBox();
          expect(label!.y + label!.height).toBeLessThanOrEqual(cover!.y + cover!.height);
        }
      });
    }
  }
});

test.describe("Scale Rule in every language", () => {
  for (const lang of LANGS) {
    test(`${lang}: the changed figure is still the largest text`, async ({ page }) => {
      await page.goto(`/v/A7T3R4ED?lang=${lang}`);
      const largest = await page.evaluate(() => {
        let max = { size: 0, text: "" };
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode;
          if (!node.textContent?.trim() || !node.parentElement) continue;
          const style = getComputedStyle(node.parentElement);
          if (style.display === "none" || style.visibility === "hidden") continue;
          const size = parseFloat(style.fontSize);
          if (size > max.size) max = { size, text: node.textContent.trim() };
        }
        return max;
      });
      expect(largest.text).toBe("29th");
    });
  }
});
