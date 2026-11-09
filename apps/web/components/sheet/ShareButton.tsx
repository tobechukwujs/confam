"use client";

import { useState } from "react";

type Props = {
  label: string;
  text: string;
  /** Leave empty to share the current page. A path starting with "/" is made absolute. */
  url?: string;
  copiedText: string;
  failedText: string;
  /** Pages we link to carry ?lang= so the person who receives the link sees the same language. */
  lang: string;
};

export function ShareButton({ label, text, url, copiedText, failedText, lang }: Props) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");

  async function onClick() {
    let shareUrl: string;
    if (url && !url.startsWith("/")) {
      shareUrl = url; // an official outside address: leave it exactly as given
    } else {
      const own = new URL(url || window.location.href, window.location.origin);
      own.searchParams.set("lang", lang);
      shareUrl = own.toString();
    }
    try {
      if (typeof navigator.share === "function") {
        await navigator.share({ text, url: shareUrl });
        return;
      }
      await navigator.clipboard.writeText(`${text} ${shareUrl}`.trim());
      setState("copied");
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;
      setState("failed");
    }
  }

  return (
    <>
      <button type="button" className="btn btn-primary" onClick={onClick}>
        {label}
      </button>
      <p role="status" className="status">
        {state === "copied" ? copiedText : state === "failed" ? failedText : ""}
      </p>
    </>
  );
}
