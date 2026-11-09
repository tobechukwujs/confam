import { render, screen } from "@testing-library/react";
import { act } from "react";
import { beforeEach, describe, expect, it } from "vitest";
import type { Change } from "@confam/contract";
import { getStrings } from "@confam/i18n";
import { PhotoPanel } from "@/components/photo/PhotoPanel";
import { forgetAllImages, imageForCode, moveToCode, rememberForJob } from "@/lib/pending-image";
import {
  ACCEPTED_TYPES,
  MAX_BYTES,
  MAX_SIDE,
  checkFileType,
  fitSize,
  imageFromClipboard,
  problemFor,
} from "@/lib/upload";

const { s } = getStrings("en");

describe("upload checks", () => {
  it.each(["image/jpeg", "image/png", "image/webp"])("accepts %s", (type) => {
    expect(checkFileType({ type, name: "x" })).toBeNull();
  });

  it.each([
    ["image/svg+xml", "a.svg"],
    ["image/gif", "a.gif"],
    ["image/heic", "a.heic"],
    ["application/pdf", "a.pdf"],
    ["text/plain", "a.txt"],
    ["video/mp4", "a.mp4"],
    ["", "a.txt"],
    ["", "noextension"],
  ])("rejects %s (%s)", (type, name) => {
    expect(checkFileType({ type, name })).toBe("type");
  });

  it("when the browser gives no type, a known picture extension is accepted", () => {
    for (const name of ["a.jpg", "a.JPEG", "a.png", "a.webp"]) expect(checkFileType({ type: "", name })).toBeNull();
  });

  it("the limits match the server", () => {
    expect(MAX_BYTES).toBe(5 * 1024 * 1024);
    expect(MAX_SIDE).toBe(2400);
    expect([...ACCEPTED_TYPES]).toEqual(["image/jpeg", "image/png", "image/webp"]);
  });

  it("fitSize only shrinks, and keeps the shape", () => {
    expect(fitSize(1000, 500)).toEqual({ width: 1000, height: 500 });
    expect(fitSize(4800, 2400)).toEqual({ width: 2400, height: 1200 });
    expect(fitSize(3000, 6000)).toEqual({ width: 1200, height: 2400 });
    expect(fitSize(1, 1)).toEqual({ width: 1, height: 1 });
  });

  it("maps server answers to plain problems", () => {
    expect(problemFor(413)).toBe("size");
    expect(problemFor(415)).toBe("type");
    expect(problemFor(429)).toBe("busy");
    expect(problemFor(503)).toBe("off");
    expect(problemFor(500)).toBe("down");
    expect(problemFor(0)).toBe("down");
  });

  it("takes a picture from the clipboard, and ignores plain text", () => {
    const file = new File(["x"], "shot.png", { type: "image/png" });
    const items = [
      { kind: "string", type: "text/plain", getAsFile: () => null },
      { kind: "file", type: "image/png", getAsFile: () => file },
    ];
    expect(imageFromClipboard(items as unknown as DataTransferItemList)).toBe(file);
    expect(imageFromClipboard([{ kind: "string", type: "text/plain", getAsFile: () => null }] as unknown as DataTransferItemList)).toBeNull();
    expect(imageFromClipboard(undefined)).toBeNull();
  });
});

describe("the picture is held in browser memory only", () => {
  beforeEach(() => forgetAllImages());

  it("is remembered by job, then moves to the check code", () => {
    rememberForJob("job1", "blob:abc");
    expect(imageForCode("K7Q2M9XA")).toBeUndefined();
    moveToCode("job1", "K7Q2M9XA");
    expect(imageForCode("K7Q2M9XA")).toBe("blob:abc");
    expect(imageForCode("k7q2-m9xa")).toBe("blob:abc"); // any spelling of the code
  });

  it("an unknown job moves nothing, and forgetting clears everything", () => {
    moveToCode("nope", "K7Q2M9XA");
    expect(imageForCode("K7Q2M9XA")).toBeUndefined();
    rememberForJob("j", "blob:1");
    moveToCode("j", "AAAA2222");
    forgetAllImages();
    expect(imageForCode("AAAA2222")).toBeUndefined();
  });

  it("never touches localStorage, sessionStorage or cookies", () => {
    rememberForJob("j", "blob:1");
    moveToCode("j", "AAAA2222");
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
    expect(document.cookie).toBe("");
  });
});

const CHANGES: Change[] = [
  { op: "replace", kind: "date", official: "28th November", copy: "29th November", box: [0.43, 0.25, 0.23, 0.06] },
  { op: "insert", kind: "money", official: null, copy: "N500", box: [0.1, 0.5, 0.1, 0.05] },
  { op: "delete", kind: "negation", official: "not", copy: null, box: [0.5, 0.7, 0.04, 0.05] },
  { op: "replace", kind: "text", official: "a", copy: "b" }, // typed text: no box
];

describe("PhotoPanel: the user's photo with the marks drawn over it", () => {
  beforeEach(() => forgetAllImages());

  it("shows nothing when the photo is gone (reload, shared link)", () => {
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={CHANGES} s={s.photo} />);
    expect(container.innerHTML).toBe("");
  });

  it("shows the photo with a mark at every box: ring, strike, caret, in red", async () => {
    rememberForJob("job1", "blob:photo");
    moveToCode("job1", "K7Q2M9XA");
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={CHANGES} s={s.photo} />);
    await act(async () => {});
    const img = screen.getByRole("img", { name: s.photo.alt });
    expect(img).toHaveAttribute("src", "blob:photo");
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("Your photo, marked");
    expect(screen.getByText("Only you can see this photo. It is not kept.")).toBeInTheDocument();
    const marks = container.querySelectorAll(".photo-mark");
    expect(marks).toHaveLength(3); // the change without a box is not drawn
    expect([...marks].map((m) => m.querySelector("[data-mark]")?.getAttribute("data-mark"))).toEqual(["ring", "strike", "caret"]);
    for (const m of marks) expect(m.querySelector("[data-mark]")).toHaveClass("tone-red");
  });

  it("places each mark by its box, as a share of the picture", async () => {
    rememberForJob("job1", "blob:photo");
    moveToCode("job1", "K7Q2M9XA");
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={CHANGES} s={s.photo} />);
    await act(async () => {});
    const first = container.querySelector(".photo-mark") as HTMLElement;
    expect(first.style.left).toBe("43%");
    expect(first.style.top).toBe("25%");
    expect(first.style.width).toBe("23%");
    expect(first.style.height).toBe("6%");
  });

  it("numbers each mark so it pairs with its row in the list", async () => {
    rememberForJob("job1", "blob:photo");
    moveToCode("job1", "K7Q2M9XA");
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={CHANGES} s={s.photo} />);
    await act(async () => {});
    const pins = [...container.querySelectorAll(".photo-mark [data-pin]")].map((p) => p.getAttribute("data-pin"));
    expect(pins).toEqual(["1", "2", "3"]);
  });

  it("uses no red when nothing differs", async () => {
    rememberForJob("job1", "blob:photo");
    moveToCode("job1", "K7Q2M9XA");
    const { container } = render(<PhotoPanel code="K7Q2M9XA" changes={[]} s={s.photo} />);
    await act(async () => {});
    expect(container.querySelector(".tone-red")).toBeNull();
    expect(container.querySelector("img")).not.toBeNull();
  });
});
