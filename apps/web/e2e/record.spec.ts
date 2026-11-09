import { expect, test } from "@playwright/test";

const OLD_TEXT =
  "The Simulated Electoral Commission announces that voter registration closes on 14th November. Register only at https://register.sec.example. Registration is free.";
const NEW_TEXT =
  "The Simulated Electoral Commission announces that voter registration now closes on 28th November. Register only at https://register.sec.example. Registration is free.";

test("'Open the original' never breaks: it opens the signed text on our own record page", async ({ page }) => {
  await page.goto("/v/A7T3R4ED");
  await page.getByRole("link", { name: "Open the original" }).click();
  await expect(page).toHaveURL(/\/record\/SEC-2026-140$/);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("revised voter registration deadline");
  await expect(page.locator(".record-text")).toHaveText(NEW_TEXT);
  await expect(page.locator(".record-text")).toHaveAttribute("lang", "en");
});

test("the record page shows who signed and when, two different people", async ({ page }) => {
  await page.goto("/record/SEC-2026-114");
  const sigs = page.locator(".signatures li");
  await expect(sigs).toHaveCount(2);
  await expect(sigs.nth(0)).toContainText("First signature");
  await expect(sigs.nth(0)).toContainText("Reviewer A (sample)");
  await expect(sigs.nth(1)).toContainText("Second signature");
  await expect(sigs.nth(1)).toContainText("Reviewer B (sample)");
  await expect(sigs.nth(0)).toContainText("WAT");
  await expect(page.locator(".record-text")).toHaveText(OLD_TEXT);
});

test("fictional notices show no 'View source' link (their addresses are not real)", async ({ page }) => {
  for (const url of ["/record/SEC-2026-114", "/v/C4NF7RM2"]) {
    await page.goto(url);
    await expect(page.getByRole("link", { name: "View source" })).toHaveCount(0);
  }
});

test("the index lists every notice and says in words which is replaced", async ({ page }) => {
  await page.goto("/record");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("The official record");
  await expect(page.getByRole("link", { name: /revised voter registration deadline/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /^Simulated Electoral Commission: voter registration deadline$/ })).toBeVisible();
  await expect(page.getByText(/Replaced by SEC-2026-140/)).toBeVisible();
  await expect(page.getByText(/Current notice/)).toBeVisible();
  await page.getByRole("link", { name: /^Simulated Electoral Commission: voter registration deadline$/ }).click();
  await expect(page).toHaveURL(/\/record\/SEC-2026-114$/);
});

test("a replaced notice links forward to the notice that replaced it", async ({ page }) => {
  await page.goto("/record/SEC-2026-114");
  await page.getByRole("link", { name: /Replaced by SEC-2026-140/ }).click();
  await expect(page).toHaveURL(/\/record\/SEC-2026-140$/);
  await expect(page.getByText("Current notice")).toBeVisible();
});

test("from 'Real, but replaced', the receipt link reaches the replacing notice", async ({ page }) => {
  await page.goto("/v/R3P7ACED");
  await page.getByRole("link", { name: "SEC-2026-140, published 9 Oct 2026" }).click();
  await expect(page).toHaveURL(/\/record\/SEC-2026-140$/);
  await expect(page.locator(".record-text")).toHaveText(NEW_TEXT);
});

test("a notice number that is not in the record says so plainly, with a 404", async ({ page }) => {
  const res = await page.goto("/record/SEC-0000-000");
  expect(res!.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("No such notice");
  await page.getByRole("link", { name: "All notices" }).click();
  await expect(page).toHaveURL(/\/record$/);
});

test("record pages fit a 360px phone without horizontal scroll", async ({ page }) => {
  for (const url of ["/record", "/record/SEC-2026-140"]) {
    await page.goto(url);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow, url).toBeLessThanOrEqual(0);
  }
});

test("the independence line and the record link are in the footer of record pages", async ({ page }) => {
  await page.goto("/record");
  await expect(page.getByText("Independent checker. Not INEC or any party.")).toBeVisible();
  await expect(page.locator("footer").getByRole("link", { name: "Official record" })).toHaveAttribute("href", "/record");
});
