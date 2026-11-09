import { NextResponse, type NextRequest } from "next/server";
import { pickLang, isLang } from "@confam/i18n";

const COOKIE = "confam_lang";
const ONE_YEAR = 60 * 60 * 24 * 365;

/**
 * Language: ?lang= wins and is remembered in a cookie (a language choice, no personal
 * data). Otherwise the cookie. Otherwise English. The result is passed to the pages in
 * request headers, so <html lang> and every string follow it.
 */
export function middleware(request: NextRequest) {
  const url = request.nextUrl;
  const asked = url.searchParams.get("lang");
  const cookie = request.cookies.get(COOKIE)?.value;
  const lang = pickLang(asked, cookie);

  const rest = new URLSearchParams(url.searchParams);
  rest.delete("lang");

  const headers = new Headers(request.headers);
  headers.set("x-confam-lang", lang);
  headers.set("x-confam-path", url.pathname);
  headers.set("x-confam-search", rest.toString());

  const response = NextResponse.next({ request: { headers } });
  if (isLang(asked) && asked !== cookie) {
    response.cookies.set(COOKIE, asked, { path: "/", maxAge: ONE_YEAR, sameSite: "lax" });
  }
  return response;
}

export const config = { matcher: ["/((?!_next/|favicon.ico).*)"] };
