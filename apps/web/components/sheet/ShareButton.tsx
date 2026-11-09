"use client";

import { useState } from "react";

type Props = {
  label: string;
  text: string;
  /** Leave empty to share the address of the current page. */
  url?: string;
  copiedText: string;
  failedText: string;
};

export function ShareButton({ label, text, url, copiedText, failedText }: Props) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");

  async function onClick() {
    const shareUrl = url || window.location.href;
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
