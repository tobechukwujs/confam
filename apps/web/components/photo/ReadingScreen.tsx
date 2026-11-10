"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { Strings } from "@confam/i18n";
import { moveToCode } from "@/lib/pending-image";
import { apiBase } from "@/lib/upload";

type Stage = "queued" | "reading_1" | "reading_2" | "comparing";
const STAGES: Stage[] = ["queued", "reading_1", "reading_2", "comparing"];
// "expired" = the check is gone or the server stopped answering (a restart loses jobs): one plain message.
type View = { kind: "working"; stage: Stage } | { kind: "failed" } | { kind: "expired" };

/**
 * Follows the REAL stage of the job on the server (no timers, no fake progress, no numbers).
 * When the check is done it opens the verdict.
 */
export function ReadingScreen({ jobId, s }: { jobId: string; s: Strings["reading"] }) {
  const router = useRouter();
  const [view, setView] = useState<View>({ kind: "working", stage: "queued" });

  useEffect(() => {
    let stopped = false;
    let misses = 0;
    let timer: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const res = await fetch(`${apiBase()}/v1/checks/${encodeURIComponent(jobId)}`, { cache: "no-store" });
        if (stopped) return;
        if (res.status === 404) return setView({ kind: "expired" });
        if (!res.ok) throw new Error(String(res.status));
        const job = (await res.json()) as { status: string; stage: string; code: string | null };
        misses = 0;
        if (job.status === "done" && job.code) {
          moveToCode(jobId, job.code);
          router.replace(`/v/${job.code}`);
          return;
        }
        if (job.status === "failed") return setView({ kind: "failed" });
        setView({ kind: "working", stage: (STAGES as string[]).includes(job.stage) ? (job.stage as Stage) : "queued" });
      } catch {
        if (++misses >= 8) return setView({ kind: "expired" }); // the server is not answering
      }
      if (!stopped) timer = setTimeout(poll, 700);
    };

    void poll();
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [jobId, router]);

  if (view.kind !== "working") {
    return (
      <div className="answer" style={{ maxWidth: 640 }}>
        <h1 className="display">{s.title}</h1>
        <p className="beta-line">
          <span className="beta">{s.beta}</span>
        </p>
        <p className="status" role="alert">
          {view.kind === "failed" ? s.failed : s.expired}
        </p>
        <a className="btn btn-primary" href="/">
          {s.back}
        </a>
      </div>
    );
  }

  const current = STAGES.indexOf(view.stage);
  return (
    <div className="answer" style={{ maxWidth: 640 }}>
      <h1 className="display">{s.title}</h1>
      <p className="beta-line">
        <span className="beta">{s.beta}</span>
      </p>
      <ol className="stages" aria-live="polite">
        {STAGES.map((stage, i) => (
          <li
            key={stage}
            className={i < current ? "past" : i === current ? "now" : "next"}
            aria-current={i === current ? "step" : undefined}
          >
            {s.stages[stage]}
          </li>
        ))}
      </ol>
      <p className="label">{s.why}</p>
    </div>
  );
}
