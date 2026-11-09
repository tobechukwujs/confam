import "server-only";
import { headers } from "next/headers";
import { isLang, type Lang } from "@confam/i18n";

/**
 * The interface language for this request. middleware.ts decides it (?lang= beats the
 * saved cookie, default English) and passes it on in a request header.
 */
export async function resolveLang(): Promise<Lang> {
  const value = (await headers()).get("x-confam-lang");
  return isLang(value) ? value : "en";
}

/** Where we are, so the language links keep the same page. `search` excludes ?lang=. */
export async function currentLocation(): Promise<{ path: string; search: string }> {
  const h = await headers();
  return { path: h.get("x-confam-path") ?? "/", search: h.get("x-confam-search") ?? "" };
}
