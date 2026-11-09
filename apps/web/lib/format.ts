import type { Verdict } from "@confam/contract";

const dateFmt = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
const dateTimeFmt = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
  timeZone: "Africa/Lagos",
});

/** "2026-10-09" -> "9 Oct 2026" */
export function formatDate(isoDate: string): string {
  return dateFmt.format(new Date(`${isoDate}T00:00:00Z`));
}

/** ISO timestamp -> "8 Nov 2026, 10:00" in Lagos time (WAT). */
export function formatDateTime(iso: string): string {
  return `${dateTimeFmt.format(new Date(iso))} WAT`;
}

/** The stored code has no hyphen; XXXX-XXXX is presentation only. */
export function formatCode(code: string): string {
  return `${code.slice(0, 4)}-${code.slice(4)}`;
}

export type ViewKey =
  | "confirmed"
  | "replaced"
  | "altered"
  | "not_official"
  | "partial"
  | "cannot_confirm";

export function viewKey(v: Verdict): ViewKey {
  if (v.verdict === "confirmed" && v.superseded_by) return "replaced";
  return v.verdict;
}

/** True for notices from the fictional Simulated Electoral Commission. */
export function isSample(v: Verdict): boolean {
  return Boolean(v.notice?.id.startsWith("SEC-"));
}
