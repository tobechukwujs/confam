import type { Verdict } from "@confam/contract";
import { intlLocale, type Lang } from "@confam/i18n";

/**
 * The language official notices are quoted in. Quotes are never translated and always
 * carry this lang. TODO: take it from the notice (the record has it; the verdict does not yet).
 */
export const NOTICE_LANG = "en";

const formatters = new Map<string, Intl.DateTimeFormat>();
function formatter(lang: Lang, withTime: boolean): Intl.DateTimeFormat {
  const key = `${lang}:${withTime}`;
  let f = formatters.get(key);
  if (!f) {
    f = new Intl.DateTimeFormat(
      intlLocale(lang),
      withTime
        ? { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: false, timeZone: "Africa/Lagos" }
        : { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" },
    );
    formatters.set(key, f);
  }
  return f;
}

/** "2026-10-09" -> "9 Oct 2026" (month name in the page language). */
export function formatDate(isoDate: string, lang: Lang = "en"): string {
  return formatter(lang, false).format(new Date(`${isoDate}T00:00:00Z`));
}

/** ISO timestamp -> "8 Nov 2026, 10:00 WAT" in Lagos time. */
export function formatDateTime(iso: string, lang: Lang = "en"): string {
  return `${formatter(lang, true).format(new Date(iso))} WAT`;
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

const RESERVED_SUFFIXES = [".example", ".test", ".invalid", ".localhost", ".local"];
const RESERVED_HOSTS = ["localhost", "example.com", "example.org", "example.net"];

/**
 * A source address is only shown ("View source") when it is a real, public https address.
 * Fictional notices use reserved names (*.example, example.com...) which never resolve.
 */
export function isRealSourceUrl(value: string): boolean {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    return false;
  }
  if (url.protocol !== "https:") return false;
  const host = url.hostname.toLowerCase();
  if (!host.includes(".")) return false;
  if (/^[\d.]+$/.test(host) || host.includes(":")) return false; // IP addresses
  if (RESERVED_SUFFIXES.some((s) => host.endsWith(s))) return false;
  if (RESERVED_HOSTS.some((h) => host === h || host.endsWith(`.${h}`))) return false;
  return true;
}

/** True for notices from the fictional Simulated Electoral Commission. */
export function isSample(v: Verdict): boolean {
  return Boolean(v.notice?.id.startsWith("SEC-"));
}
