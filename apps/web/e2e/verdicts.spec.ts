import { expect, test, type Page } from "@playwright/test";

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

async function bottomOf(page: Page, selector: string): Promise<number> {
  const box = await page.locator(selector).first().boundingBox();
  if (!box) throw new Error(`no box for ${selector}`);
  return box.y + box.height;
}

test.describe("One Screen Rule at 360x640", () => {
  for (const [name, code] of SAMPLES) {
    test(`${name}: word, marked figure, sentence, instruction and action fit without scrolling`, async ({ page }) => {
      await page.goto(`/v/${code}`);
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

      for (const selector of [
        "h1",
        ".stage, .stage-tick",
        ".answer > p:nth-of-type(1)",
        ".answer > p:nth-of-type(2)",
        ".actions .btn",
      ]) {
        const bottom = await bottomOf(page, selector);
        expect(bottom, `${selector} must end above ${VIEWPORT_HEIGHT}px`).toBeLessThanOrEqual(VIEWPORT_HEIGHT);
      }

      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow, "no horizontal scroll").toBeLessThanOrEqual(0);

      // tap targets at least 44px
      const action = await page.locator(".actions .btn").first().boundingBox();
      expect(action!.height).toBeGreaterThanOrEqual(44);
    });
  }
});

test("Scale Rule: the changed figure is the largest text on the altered screen", async ({ page }) => {
  await page.goto("/v/A7T3R4ED");
  const result = await page.evaluate(() => {
    let max = { size: 0, text: "", cls: "" };
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.textContent?.trim() || !node.parentElement) continue;
      const style = getComputedStyle(node.parentElement);
      if (style.display === "none" || style.visibility === "hidden") continue;
      const size = parseFloat(style.fontSize);
      if (size > max.size) max = { size, text: node.textContent.trim(), cls: node.parentElement.className };
    }
    return max;
  });
  expect(result.text).toBe("29th");
  expect(result.cls).toContain("figure");
});

test("the independence line is on every public page", async ({ page }) => {
  for (const url of ["/", "/v/C4NF7RM2", "/v/ZZZZZZZZ"]) {
    await page.goto(url);
    await expect(page.getByText("Independent checker. Not INEC or any party.")).toBeVisible();
  }
});

test("an unknown code says so plainly (a forged reply proves nothing)", async ({ page }) => {
  const res = await page.goto("/v/ZZZZZZZZ");
  expect(res!.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("No check with that code");
});

test("pasting the current notice gives Confirmed; the old one gives Real, but replaced", async ({ page }) => {
  const current =
    "The Simulated Electoral Commission announces that voter registration now closes on 28th November. Register only at https://register.sec.example. Registration is free.";
  const old =
    "The Simulated Electoral Commission announces that voter registration closes on 14th November. Register only at https://register.sec.example. Registration is free.";

  await page.goto("/");
  await page.getByLabel("The notice text").fill(current);
  await page.getByRole("button", { name: "Check this notice" }).click();
  await expect(page).toHaveURL(/\/v\/[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Confirmed");

  await page.goto("/");
  await page.getByLabel("The notice text").fill(old);
  await page.getByRole("button", { name: "Check this notice" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Real, but replaced");
});

test("text that is not in the record is Cannot confirm, never fake (rule 1)", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("The notice text").fill("Collect your new ballot cards at the market square on Sunday.");
  await page.getByRole("button", { name: "Check this notice" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Cannot confirm");
  await expect(page.getByText(/does not mean it is fake/i)).toBeVisible();
  await expect(page.getByText("Not official")).toHaveCount(0);
});

test("an empty paste shows a bold black message, not red", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Check this notice" }).click();
  const error = page.locator("#text-error");
  await expect(error).toHaveText("Paste the notice text first.");
  const color = await error.evaluate((el) => getComputedStyle(el).color);
  expect(color).toBe("rgb(20, 23, 28)"); // print-black #14171c, never red
  expect(await error.evaluate((el) => getComputedStyle(el).fontWeight)).toBe("700");
});
