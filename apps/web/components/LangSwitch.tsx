import { LANGUAGES, type Lang } from "@confam/i18n";

type Props = {
  current: Lang;
  /** Path of the page we are on, e.g. "/v/A7T3R4ED". */
  path: string;
  /** Query string of the page without lang, e.g. "a=1". */
  search: string;
  label: string;
};

function hrefFor(path: string, search: string, lang: Lang) {
  const params = new URLSearchParams(search);
  params.set("lang", lang);
  return `${path}?${params.toString()}`;
}

/**
 * All five languages. From 900px they sit in the cover in a row. On phones the current
 * language is a button that opens a row of all five (a plain <details>, so no script is
 * needed). Only one of the two is ever shown, so screen readers never hear it twice.
 */
export function LangSwitch({ current, path, search, label }: Props) {
  const links = LANGUAGES.map((l) => (
    <li key={l.code}>
      <a
        href={hrefFor(path, search, l.code)}
        lang={l.code}
        hrefLang={l.code}
        aria-current={l.code === current ? "true" : undefined}
      >
        {l.name}
      </a>
    </li>
  ));
  const currentName = LANGUAGES.find((l) => l.code === current)!.name;
  return (
    <>
      <nav className="lang-wide" aria-label={label}>
        <ul>{links}</ul>
      </nav>
      <details className="lang-narrow">
        <summary aria-label={`${label}: ${currentName}`}>
          <span lang={current}>{currentName}</span>
        </summary>
        <nav aria-label={label}>
          <ul>{links}</ul>
        </nav>
      </details>
    </>
  );
}
