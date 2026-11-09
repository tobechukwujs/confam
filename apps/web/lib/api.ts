import "server-only";
import type { Verdict } from "@confam/contract";
import type { Lang } from "@confam/i18n";
import type { RecordEntry, RecordList } from "./record-types";

// Server-side only: the browser never talks to the API directly, so no CORS is needed
// for the web app. (The API still allows CONFAM_CORS_ORIGINS for future clients.)
const API_URL = (process.env.API_URL ?? "http://localhost:8000").replace(/\/$/, "");

export type CheckResult =
  | { ok: true; verdict: Verdict }
  | { ok: false; status: number };

export async function postCheck(text: string, lang: Lang): Promise<CheckResult> {
  const res = await fetch(`${API_URL}/v1/checks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, lang }),
    cache: "no-store",
  });
  if (!res.ok) return { ok: false, status: res.status };
  return { ok: true, verdict: (await res.json()) as Verdict };
}

export async function getRecordList(): Promise<RecordList> {
  const res = await fetch(`${API_URL}/v1/record`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Record list failed: ${res.status}`);
  return (await res.json()) as RecordList;
}

/** null when the notice is not in the record (404). */
export async function getRecordEntry(id: string): Promise<RecordEntry | null> {
  const res = await fetch(`${API_URL}/v1/record/${encodeURIComponent(id)}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Record entry failed: ${res.status}`);
  return (await res.json()) as RecordEntry;
}

/** null when the code is unknown or expired (404). Throws on any other failure. */
export async function getVerdict(code: string): Promise<Verdict | null> {
  const res = await fetch(`${API_URL}/v1/verdicts/${encodeURIComponent(code)}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Verdict lookup failed: ${res.status}`);
  return (await res.json()) as Verdict;
}
