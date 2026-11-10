"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import type { Lang, Strings } from "@confam/i18n";
import { rememberForJob } from "@/lib/pending-image";
import {
  MAX_BYTES,
  apiBase,
  checkFileType,
  imageFromClipboard,
  problemFor,
  shrink,
  type Problem,
} from "@/lib/upload";

/**
 * Check a photo: Ctrl+V paste, a file picker, drag-and-drop, or the phone camera. The browser
 * shrinks the picture, sends it straight to the API, and keeps its own copy in memory only so the
 * marks can be drawn on it later. Errors are bold black, never red.
 */
export function UploadZone({ s, lang }: { s: Strings["upload"]; lang: Lang }) {
  const router = useRouter();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [busy, setBusy] = useState(false);
  const [over, setOver] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const cameraInput = useRef<HTMLInputElement>(null);

  const send = useCallback(
    async (file: File) => {
      setProblem(null);
      if (checkFileType(file)) return setProblem("type");
      setBusy(true);
      try {
        let blob: Blob;
        try {
          blob = await shrink(file); // also proves the browser can read it as a picture
        } catch {
          return setProblem("type");
        }
        if (blob.size > MAX_BYTES) return setProblem("size");
        const res = await fetch(`${apiBase()}/v1/checks?lang=${lang}`, {
          method: "POST",
          headers: { "Content-Type": blob.type },
          body: blob,
        });
        if (res.status !== 202) return setProblem(problemFor(res.status));
        const { job_id: jobId } = (await res.json()) as { job_id: string };
        rememberForJob(jobId, URL.createObjectURL(blob));
        router.push(`/check/${jobId}`);
      } catch {
        setProblem("down");
      } finally {
        setBusy(false);
      }
    },
    [lang, router],
  );

  // Ctrl+V anywhere on the page: a pasted picture is checked; pasted text is left alone.
  useEffect(() => {
    const onPaste = (event: ClipboardEvent) => {
      const file = imageFromClipboard(event.clipboardData?.items);
      if (file) {
        event.preventDefault();
        void send(file);
      }
    };
    document.addEventListener("paste", onPaste);
    return () => document.removeEventListener("paste", onPaste);
  }, [send]);

  const pick = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = ""; // choosing the same picture again must work
    if (file) void send(file);
  };

  const message: Record<Problem, string> = {
    type: s.errorType,
    size: s.errorSize,
    busy: s.errorBusy,
    down: s.errorDown,
    off: s.errorOff,
  };

  return (
    <section id="upload" className={`upload${over ? " over" : ""}`} aria-labelledby="upload-h">
      <h2 className="headline" id="upload-h">
        {s.heading} <span className="beta">{s.beta}</span>
      </h2>
      <p>{s.lead}</p>
      <p className="label beta-note">{s.betaNote}</p>
      <div
        className="dropzone"
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          const file = e.dataTransfer.files?.[0];
          if (file) void send(file);
        }}
      >
        <p className="label">{busy ? s.sending : s.drop}</p>
        <div className="upload-buttons">
          <button type="button" className="btn btn-line" disabled={busy} onClick={() => fileInput.current?.click()}>
            {s.choose}
          </button>
          <button type="button" className="btn btn-line" disabled={busy} onClick={() => cameraInput.current?.click()}>
            {s.camera}
          </button>
        </div>
        <input ref={fileInput} type="file" accept="image/*" hidden onChange={pick} data-testid="file-input" />
        <input
          ref={cameraInput}
          type="file"
          accept="image/*"
          capture="environment"
          hidden
          onChange={pick}
          data-testid="camera-input"
        />
      </div>
      {problem && (
        <p className="error" role="alert" id="upload-error">
          {message[problem]}
        </p>
      )}
    </section>
  );
}
