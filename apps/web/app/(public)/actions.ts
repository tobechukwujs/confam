"use server";

import { redirect } from "next/navigation";
import { isLang } from "@confam/i18n";
import { postCheck } from "@/lib/api";

export type CheckState = { error?: "empty" | "tooLong" | "busy" | "down" };

/** Works with JavaScript off: a plain form post, then a redirect to the verdict page. */
export async function checkNotice(_prev: CheckState, formData: FormData): Promise<CheckState> {
  const text = String(formData.get("text") ?? "");
  const asked = formData.get("lang");
  const lang = isLang(asked) ? asked : "en";
  if (!text.trim()) return { error: "empty" };
  if (text.length > 5000) return { error: "tooLong" };

  let code: string;
  try {
    const result = await postCheck(text, lang);
    if (!result.ok) return { error: result.status === 429 ? "busy" : "down" };
    code = result.verdict.code;
  } catch {
    return { error: "down" };
  }
  redirect(`/v/${code}`);
}
