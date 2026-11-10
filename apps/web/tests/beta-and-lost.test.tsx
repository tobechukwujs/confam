import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LANGS, getStrings } from "@confam/i18n";
import { CheckForm } from "@/components/CheckForm";
import { PhotoPanel } from "@/components/photo/PhotoPanel";
import { ReadingScreen } from "@/components/photo/ReadingScreen";
import { UploadZone } from "@/components/photo/UploadZone";
import { forgetAllImages, imageForCode, moveToCode, rememberForJob } from "@/lib/pending-image";

const replace = vi.fn();
vi.mock("@/app/(public)/actions", () => ({ checkNotice: vi.fn() })); // the real one imports server-only code
const router = { replace, push: vi.fn() }; // stable, like the real Next router (a new object each render would re-run the polling effect)
vi.mock("next/navigation", () => ({ useRouter: () => router }));

const { s } = getStrings("en");

describe("Beta label: photo checks only", () => {
  it("the upload box is labelled Beta and warns that it may not confirm a real notice", () => {
    const { container } = render(<UploadZone s={s.upload} lang="en" />);
    expect(container.querySelector("h2 .beta")).toHaveTextContent("Beta");
    expect(container.querySelector(".beta-note")).toHaveTextContent(/new and still being tested/);
    expect(container.querySelector(".beta-note")).toHaveTextContent(/Pasting the text is more reliable/);
  });

  it("the text check has no Beta label at all", () => {
    const { container } = render(<CheckForm s={s.home} lang="en" />);
    expect(container.textContent).not.toMatch(/beta/i);
  });

  it("the marked-photo panel is labelled Beta", async () => {
    forgetAllImages();
    rememberForJob("j", "blob:x");
    moveToCode("j", "K7Q2M9XA");
    expect(imageForCode("K7Q2M9XA")).toBe("blob:x");
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={[]} s={s.photo} />);
    await act(async () => {});
    expect(container.querySelector("h2 .beta")).toHaveTextContent("Beta");
  });

  it("the label is plain text in print colour: no red, no pill", () => {
    const { container } = render(<UploadZone s={s.upload} lang="en" />);
    const beta = container.querySelector(".beta") as HTMLElement;
    expect(beta.className).toBe("beta");
    expect(beta.closest(".tone-red")).toBeNull();
  });

  it.each(LANGS)("%s has a Beta label and a note (the four non-English notes are drafts)", (lang) => {
    const t = getStrings(lang).s;
    expect(t.upload.beta).toBe("Beta");
    expect(t.reading.beta).toBe("Beta");
    expect(t.photo.beta).toBe("Beta");
    expect(t.upload.betaNote.length).toBeGreaterThan(20);
  });
});

describe("a lost job shows a plain message, not an error page", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    replace.mockClear();
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  const reply = (status: number, body: unknown = {}) => ({ ok: status >= 200 && status < 300, status, json: async () => body });

  it("a 404 (the server restarted and lost the job) says: Something went wrong, please try again.", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => reply(404)));
    const { container } = render(<ReadingScreen jobId="abcdefgh12345678" s={s.reading} />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10);
    });
    const message = container.querySelector("p.status") as HTMLElement;
    expect(message).toHaveTextContent("Something went wrong, please try again.");
    expect(message).toHaveAttribute("role", "alert");
    expect(screen.getByRole("link", { name: "Check another notice" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Reading your notice");
    expect(container.querySelector(".beta")).toHaveTextContent("Beta");
  });

  it("a server that stops answering gives the same message after a few tries", async () => {
    const fetchMock = vi.fn(async () => {
      throw new Error("connection refused");
    });
    vi.stubGlobal("fetch", fetchMock);
    const { container } = render(<ReadingScreen jobId="abcdefgh12345678" s={s.reading} />);
    for (let i = 0; i < 12; i++) {
      await act(async () => {
        await vi.advanceTimersByTimeAsync(800);
      });
    }
    expect(container.querySelector("p.status")).toHaveTextContent("Something went wrong, please try again.");
    expect(fetchMock.mock.calls.length).toBeGreaterThanOrEqual(8);
  });

  it("a photo that could not be read keeps its own, specific message", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => reply(200, { status: "failed", stage: "failed", code: null })));
    const { container } = render(<ReadingScreen jobId="abcdefgh12345678" s={s.reading} />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10);
    });
    expect(container.querySelector("p.status")).toHaveTextContent("We could not read that photo.");
  });

  it("a finished check opens the verdict", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => reply(200, { status: "done", stage: "done", code: "K7Q2M9XA" })));
    render(<ReadingScreen jobId="abcdefgh12345678" s={s.reading} />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10);
    });
    expect(replace).toHaveBeenCalledWith("/v/K7Q2M9XA");
  });

  it("the lost-job message is the same plain sentence in every language (drafts outside English)", () => {
    for (const lang of LANGS) expect(getStrings(lang).s.reading.expired.length).toBeGreaterThan(10);
    expect(getStrings("en").s.reading.expired).toBe("Something went wrong, please try again.");
  });
});
