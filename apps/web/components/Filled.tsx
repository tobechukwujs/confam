import { Fragment } from "react";
import { fillParts } from "@confam/i18n";

/**
 * Fill a template whose {placeholders} are official words. The interface words around
 * them are in the page language; the official words are marked with the notice's own
 * language, so they are never translated and screen readers pronounce them correctly.
 */
export function Filled({
  template,
  values,
  lang,
}: {
  template: string;
  values: Record<string, string>;
  lang: string;
}) {
  return (
    <>
      {fillParts(template, values).map((part, i) =>
        part.value ? (
          <span key={i} lang={lang}>
            {part.text}
          </span>
        ) : (
          <Fragment key={i}>{part.text}</Fragment>
        ),
      )}
    </>
  );
}
