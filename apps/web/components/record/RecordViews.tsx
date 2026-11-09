import { fill, type Lang, type Strings } from "@confam/i18n";
import { formatDate, formatDateTime, isRealSourceUrl } from "@/lib/format";
import type { RecordEntry, RecordList } from "@/lib/record-types";

/** Public list of every notice in the signed record. No status pills: replacement is said in words. */
export function RecordIndexView({ list, s, lang }: { list: RecordList; s: Strings; lang: Lang }) {
  const r = s.record;
  return (
    <div className="answer" style={{ maxWidth: 720 }}>
      <h1 className="display">{r.title}</h1>
      <p>{r.lead}</p>
      <p className="sample-note">{s.sampleNotice}</p>
      <p className="label">
        {fill(r.asOf, { date: formatDateTime(list.record_as_of, lang) })}
      </p>
      <ul className="record-list">
        {list.notices.map((n) => (
          <li key={n.id}>
            <a className="record-title" href={`/record/${encodeURIComponent(n.id)}`} lang={n.lang}>
              {n.title}
            </a>
            <p className="label">
              {n.id} · {formatDate(n.published, lang)} ·{" "}
              {n.superseded_by ? fill(r.replacedBy, { id: n.superseded_by.id }) : r.current}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** One notice: its exact signed text, who signed it and when. */
export function RecordEntryView({ entry, s, lang }: { entry: RecordEntry; s: Strings; lang: Lang }) {
  const r = s.record;
  return (
    <div className="spread">
      <span className="staple top" aria-hidden="true" />
      <span className="staple bottom" aria-hidden="true" />
      <section className="answer" aria-labelledby="record-h">
        <h1 className="display record-h1" id="record-h" lang={entry.lang}>
          {entry.title}
        </h1>
        <p className="sample-note">{s.sampleNotice}</p>
        <dl className="facts">
          <dt>{r.idLabel}</dt>
          <dd>{entry.id}</dd>
          <dt>{r.published}</dt>
          <dd>{formatDate(entry.published, lang)}</dd>
        </dl>
        <p>
          {entry.superseded_by ? (
            <a href={`/record/${encodeURIComponent(entry.superseded_by.id)}`}>
              {fill(r.replacedBy, { id: entry.superseded_by.id })}
            </a>
          ) : (
            r.current
          )}
        </p>
        {isRealSourceUrl(entry.url) && (
          <p>
            <a className="secondary-link" href={entry.url} target="_blank" rel="noopener noreferrer">
              {r.viewSource}
            </a>
          </p>
        )}
        <p>
          <a href="/record">{r.back}</a>
        </p>
      </section>
      <section className="proof" aria-label={r.textHeading}>
        <div>
          <h2 className="headline">{r.textHeading}</h2>
          <p className="label">{r.textNote}</p>
          <div className="sheet">
            <div className="record-text" lang={entry.lang}>
              {entry.text}
            </div>
          </div>
        </div>
        <div>
          <h2 className="headline">{r.signedHeading}</h2>
          <ol className="signatures">
            {entry.signatures.map((sig) => (
              <li key={sig.role}>
                <span className="kind">{sig.role === "first" ? r.first : r.second}</span>
                <span>
                  {sig.reviewer}, {formatDateTime(sig.signed_at, lang)}
                </span>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </div>
  );
}
