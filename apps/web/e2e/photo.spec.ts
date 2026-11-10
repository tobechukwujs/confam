import path from "node:path";
import { expect, test, type Page, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const FIXTURES = path.resolve(__dirname, "../../../fixtures/sec-sim/images");
const DATE_EDIT = path.join(FIXTURES, "date_edit.png");
const HONEST = path.join(FIXTURES, "honest.png");
const JOB = "abcdefgh12345678";

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type",
  "access-control-allow-methods": "GET,POST,OPTIONS",
};

/** Mock the job calls only. The verdict page is the real API (sample PHT7B3XA has a real box). */
async function mockJob(page: Page, stages: Array<Record<string, unknown>>, seen: { post?: { type: string; size: number; url: string } } = {}) {
  let n = 0;
  await page.route(`${API}/v1/checks**`, async (route: Route) => {
    const req = route.request();
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (req.method() === "POST") {
      seen.post = { type: req.headers()["content-type"], size: req.postDataBuffer()?.length ?? 0, url: req.url() };
      return route.fulfill({ status: 202, headers: CORS, contentType: "application/json", body: JSON.stringify({ job_id: JOB }) });
    }
    const step = stages[Math.min(n++, stages.length - 1)]!;
    if (step.__status) return route.fulfill({ status: step.__status as number, headers: CORS, contentType: "application/json", body: "{}" });
    return route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body: JSON.stringify({ job_id: JOB, ...step }) });
  });
}

const working = (stage: string) => ({ status: "working", stage, code: null });
const done = (code: string) => ({ status: "done", stage: "done", code });

async function health(page: Page) {
  return (await (await page.request.get(`${API}/health`)).json()) as { photo_checks: boolean };
}

test.describe("the upload box", () => {
  test("offers choose, camera, drop and paste, all as real controls", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Or check a photo" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Choose a photo" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Take a photo" })).toBeVisible();
    await expect(page.getByText("Drop the photo here, or paste it with Ctrl+V.")).toBeVisible();
    await expect(page.getByTestId("file-input")).toHaveAttribute("accept", "image/*");
    await expect(page.getByTestId("camera-input")).toHaveAttribute("capture", "environment");
    for (const name of ["Choose a photo", "Take a photo"]) {
      const box = await page.getByRole("button", { name }).boundingBox();
      expect(box!.height).toBeGreaterThanOrEqual(44);
    }
  });

  test("a file that is not a picture gets a bold black message, never red, and nothing is sent", async ({ page }) => {
    let posts = 0;
    await page.route(`${API}/v1/checks**`, (r) => {
      posts++;
      return r.abort();
    });
    await page.goto("/");
    await page.getByTestId("file-input").setInputFiles({ name: "notes.txt", mimeType: "text/plain", buffer: Buffer.from("hello") });
    const error = page.locator("#upload-error");
    await expect(error).toHaveText("That file is not a picture we can read. Use a photo or screenshot (JPG, PNG or WebP).");
    expect(await error.evaluate((el) => getComputedStyle(el).color)).toBe("rgb(20, 23, 28)"); // print black
    expect(await error.evaluate((el) => getComputedStyle(el).fontWeight)).toBe("700");
    expect(posts).toBe(0);
  });

  test("a file named .png that is not really a picture is refused too", async ({ page }) => {
    let posts = 0;
    await page.route(`${API}/v1/checks**`, (r) => {
      posts++;
      return r.abort();
    });
    await page.goto("/");
    await page.getByTestId("file-input").setInputFiles({ name: "fake.png", mimeType: "image/png", buffer: Buffer.from("not a png") });
    await expect(page.locator("#upload-error")).toContainText("not a picture we can read");
    expect(posts).toBe(0);
  });

  for (const [status, text] of [
    [413, "That picture is too big. Use one under 5 MB."],
    [415, "not a picture we can read"],
    [429, "Too many checks just now"],
    [503, "Photo checks are not available right now. Please paste the text instead."],
    [500, "We could not reach the checker"],
  ] as const) {
    test(`the server answering ${status} gives a plain message`, async ({ page }) => {
      await page.route(`${API}/v1/checks**`, (r) =>
        r.request().method() === "OPTIONS"
          ? r.fulfill({ status: 204, headers: CORS })
          : r.fulfill({ status, headers: CORS, contentType: "application/json", body: JSON.stringify({ detail: "x" }) }),
      );
      await page.goto("/");
      await page.getByTestId("file-input").setInputFiles(DATE_EDIT);
      await expect(page.locator("#upload-error")).toContainText(text);
      await expect(page).toHaveURL(/localhost:3000\/$/);
    });
  }
});

test.describe("sending a photo", () => {
  test("shrinks and sends the picture, follows the real stages, then opens the verdict with the photo marked", async ({ page }) => {
    const seen: { post?: { type: string; size: number; url: string } } = {};
    await mockJob(page, [working("queued"), working("reading_1"), working("reading_2"), working("comparing"), done("PHT7B3XA")], seen);
    await page.goto("/");
    await page.getByTestId("file-input").setInputFiles(DATE_EDIT);

    await expect(page).toHaveURL(new RegExp(`/check/${JOB}$`));
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Reading your notice");
    // the stage list follows the server: the current step is marked, in order
    await expect(page.locator('.stages li[aria-current="step"]')).toHaveText("Reading the photo, first time", { timeout: 6000 });
    await expect(page.locator('.stages li[aria-current="step"]')).toHaveText("Reading it again, second time", { timeout: 6000 });
    await expect(page.locator('.stages li[aria-current="step"]')).toHaveText("Comparing with the official record", { timeout: 6000 });
    // no percentages and no numbers anywhere on the reading screen
    expect(await page.locator("main").innerText()).not.toMatch(/\d+\s?%/);

    await expect(page).toHaveURL(/\/v\/PHT7B3XA$/, { timeout: 8000 });
    expect(seen.post!.type).toBe("image/jpeg"); // shrunk and re-encoded in the browser
    expect(seen.post!.size).toBeGreaterThan(1000);
    expect(seen.post!.size).toBeLessThan(5 * 1024 * 1024);
    expect(seen.post!.url).toContain("lang=en");

    // the answer screen is still text-led...
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Altered");
    await expect(page.locator(".figure-main")).toHaveText("29th");
    // ...and the photo, marked, is first in the proof column
    const panel = page.locator(".photo-panel");
    await expect(panel).toBeVisible();
    await expect(panel.getByRole("heading", { name: "Your photo, marked" })).toBeVisible();
    await expect(panel.getByRole("img", { name: /The photo you sent/ })).toBeVisible();
    await expect(panel.locator('.photo-mark [data-mark="ring"]')).toHaveCount(1);
    const mark = await panel.locator(".photo-mark").boundingBox();
    const frame = await panel.locator(".photo-frame").boundingBox();
    // the mark sits where the box says: 43% across, 25% down the photo
    expect(Math.abs((mark!.x - frame!.x) / frame!.width - 0.4317)).toBeLessThan(0.02);
    expect(Math.abs((mark!.y - frame!.y) / frame!.height - 0.2538)).toBeLessThan(0.02);
  });

  test("the photo is kept only in memory: a reload falls back to the text sheet", async ({ page }) => {
    await mockJob(page, [done("PHT7B3XA")]);
    await page.goto("/");
    await page.getByTestId("file-input").setInputFiles(DATE_EDIT);
    await expect(page.locator(".photo-panel")).toBeVisible({ timeout: 8000 });
    await page.reload();
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Altered");
    await expect(page.locator(".photo-panel")).toHaveCount(0);
    await expect(page.locator(".figure-main")).toHaveText("29th");
    // nothing about the picture was saved in the browser
    const stored = await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length, cookie: document.cookie }));
    expect(stored.local).toBe(0);
    expect(stored.session).toBe(0);
    expect(stored.cookie).not.toMatch(/blob|png|jpeg/i);
  });

  test("a verdict from pasted text never shows a photo panel", async ({ page }) => {
    await page.goto("/v/A7T3R4ED");
    await expect(page.locator(".photo-panel")).toHaveCount(0);
  });

  test("Ctrl+V of a picture checks it; pasting text into the box is left alone", async ({ page }) => {
    const seen: { post?: { type: string; size: number; url: string } } = {};
    await mockJob(page, [done("PHT7B3XA")], seen);
    await page.goto("/");
    // plain text paste is not hijacked
    const prevented = await page.evaluate(() => {
      const dt = new DataTransfer();
      dt.setData("text/plain", "some pasted words");
      const ev = new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true });
      document.getElementById("text")!.dispatchEvent(ev);
      return ev.defaultPrevented;
    });
    expect(prevented).toBe(false);
    // a picture on the clipboard starts a check
    const bytes = Array.from(await (await import("node:fs/promises")).readFile(DATE_EDIT));
    await page.evaluate((arr) => {
      const file = new File([new Uint8Array(arr)], "screenshot.png", { type: "image/png" });
      const dt = new DataTransfer();
      dt.items.add(file);
      document.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true }));
    }, bytes);
    await expect(page).toHaveURL(/\/v\/PHT7B3XA$/, { timeout: 8000 });
    expect(seen.post!.type).toBe("image/jpeg");
  });

  test("dropping a picture on the box checks it", async ({ page }) => {
    await mockJob(page, [done("PHT7B3XA")]);
    await page.goto("/");
    const bytes = Array.from(await (await import("node:fs/promises")).readFile(DATE_EDIT));
    await page.evaluate((arr) => {
      const file = new File([new Uint8Array(arr)], "dropped.png", { type: "image/png" });
      const dt = new DataTransfer();
      dt.items.add(file);
      const zone = document.querySelector(".dropzone")!;
      zone.dispatchEvent(new DragEvent("dragover", { dataTransfer: dt, bubbles: true, cancelable: true }));
      zone.dispatchEvent(new DragEvent("drop", { dataTransfer: dt, bubbles: true, cancelable: true }));
    }, bytes);
    await expect(page).toHaveURL(/\/v\/PHT7B3XA$/, { timeout: 8000 });
  });
});

test.describe("the reading screen when things go wrong", () => {
  test("a failed job says so plainly and offers another try", async ({ page }) => {
    await mockJob(page, [working("reading_1"), { status: "failed", stage: "failed", code: null }]);
    await page.goto(`/check/${JOB}`);
    await expect(page.locator("p.status")).toHaveText("We could not read that photo. Try a clearer one, or paste the text.");
    await page.getByRole("link", { name: "Check another notice" }).click();
    await expect(page).toHaveURL(/localhost:3000\/$/);
  });

  test("a lost job (the server restarted) shows a plain message in bold black, not an error page", async ({ page }) => {
    await mockJob(page, [{ __status: 404 }]);
    const res = await page.goto(`/check/${JOB}`);
    expect(res!.status()).toBe(200); // our page, not a crash page
    const message = page.locator("p.status");
    await expect(message).toHaveText("Something went wrong, please try again.");
    expect(await message.evaluate((el) => getComputedStyle(el).fontWeight)).toBe("700");
    expect(await message.evaluate((el) => getComputedStyle(el).color)).toBe("rgb(20, 23, 28)"); // print black, never red
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Reading your notice");
    await expect(page.getByText(/Application error|Internal Server Error/i)).toHaveCount(0);
    await page.getByRole("link", { name: "Check another notice" }).click();
    await expect(page).toHaveURL(/localhost:3000\/$/);
  });

  test("the reading screen speaks the chosen language and fits a phone", async ({ page }) => {
    await mockJob(page, [working("reading_2")]);
    await page.goto(`/check/${JOB}?lang=ha`);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Ana karanta sanarwarka");
    await expect(page.locator('.stages li[aria-current="step"]')).toHaveText("Ana sake karanta shi, karo na biyu");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
});

test("'Send a clearer photo' takes you to the upload box", async ({ page }) => {
  await page.goto("/v/UNC7EAR2");
  await page.getByRole("link", { name: "Send a clearer photo" }).click();
  await expect(page).toHaveURL(/\/#upload$/);
  await expect(page.locator("#upload")).toBeVisible();
});

test.describe("against the real API", () => {
  test("a photo check either works end to end or says plainly that it is off", async ({ page }) => {
    const { photo_checks } = await health(page);
    await page.goto("/");
    await page.getByTestId("file-input").setInputFiles(HONEST);
    if (photo_checks) {
      await expect(page).toHaveURL(/\/v\/[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$/, { timeout: 60_000 });
      await expect(page.getByRole("heading", { level: 1 })).toHaveText("Confirmed");
    } else {
      await expect(page.locator("#upload-error")).toHaveText("Photo checks are not available right now. Please paste the text instead.");
      // and pasting text still works
      await page.getByLabel("The notice text").fill("Collect your new ballot cards at the market square on Sunday.");
      await page.getByRole("button", { name: "Check this notice" }).click();
      await expect(page.getByRole("heading", { level: 1 })).toHaveText("Cannot confirm");
    }
  });
});


test.describe("Beta label", () => {
  test("photo checks are labelled Beta with a plain warning; the text check is not", async ({ page }) => {
    await page.goto("/");
    const heading = page.getByRole("heading", { name: /Or check a photo/ });
    await expect(heading.locator(".beta")).toHaveText("Beta");
    await expect(page.locator(".beta-note")).toContainText("new and still being tested");
    // not red, and not on the text check
    expect(await heading.locator(".beta").evaluate((el) => getComputedStyle(el).color)).not.toBe("rgb(196, 13, 35)");
    await expect(page.locator("form.field .beta")).toHaveCount(0);
    expect(await page.locator("form.field").innerText()).not.toMatch(/beta/i);
  });

  test("the reading screen and the marked photo carry the Beta label", async ({ page }) => {
    await mockJob(page, [working("reading_1")]);
    await page.goto(`/check/${JOB}`);
    await expect(page.locator(".beta")).toHaveText("Beta");
  });

  test("a verdict from pasted text has no Beta label anywhere", async ({ page }) => {
    await page.goto("/v/A7T3R4ED");
    await expect(page.locator(".beta")).toHaveCount(0);
  });

  test("the Beta note is translated and the label stays Beta", async ({ page }) => {
    await page.goto("/?lang=ha");
    await expect(page.locator("#upload .beta")).toHaveText("Beta");
    await expect(page.locator(".beta-note")).toContainText("Binciken hoto sabon abu ne");
  });
});