"use client";

import { useActionState } from "react";
import { checkNotice, type CheckState } from "@/app/(public)/actions";
import type { Lang, Strings } from "@confam/i18n";

export function CheckForm({ s, lang }: { s: Strings["home"]; lang: Lang }) {
  const [state, action, pending] = useActionState<CheckState, FormData>(checkNotice, {});
  const message = state.error
    ? {
        empty: s.errorEmpty,
        tooLong: s.errorTooLong,
        busy: s.errorBusy,
        down: s.errorDown,
      }[state.error]
    : null;

  return (
    <form action={action} className="field">
      {/* The check carries the language the person is reading in. */}
      <input type="hidden" name="lang" value={lang} />
      <label htmlFor="text">{s.label}</label>
      <textarea
        id="text"
        name="text"
        placeholder={s.placeholder}
        maxLength={6000}
        aria-invalid={message ? true : undefined}
        aria-describedby={message ? "text-error" : undefined}
      />
      {message && (
        <p className="error" id="text-error" role="alert">
          {message}
        </p>
      )}
      <div style={{ marginTop: "var(--line)" }}>
        <button type="submit" className="btn btn-primary" disabled={pending}>
          {pending ? s.checking : s.submit}
        </button>
      </div>
    </form>
  );
}
