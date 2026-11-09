import type { Verdict } from "@confam/contract";
import type { Lang, Strings } from "@confam/i18n";
import { Filled } from "../Filled";
import { NOTICE_LANG, formatCode, formatDate, formatDateTime, isRealSourceUrl } from "@/lib/format";

/** Official notice id, published date, checked time, record as of, check code, and links. */
export function Receipt({ verdict, s, lang }: { verdict: Verdict; s: Strings; lang: Lang }) {
  const r = s.receipt;
  const { notice } = verdict;
  return (
    <section className="receipt" aria-labelledby="receipt-h">
      <h2 className="headline" id="receipt-h">
        {r.heading}
      </h2>
      <dl>
        <dt>{r.notice}</dt>
        <dd lang={NOTICE_LANG}>{notice ? `${notice.id}, ${notice.title}` : <span lang={lang}>{r.noNotice}</span>}</dd>
        {notice && (
          <>
            <dt>{r.published}</dt>
            <dd>{formatDate(notice.published, lang)}</dd>
          </>
        )}
        {verdict.superseded_by && (
          <>
            <dt>{r.replacedBy}</dt>
            <dd>
              <a href={`/record/${encodeURIComponent(verdict.superseded_by.id)}`}>
                <Filled
                  template={r.replacedByValue}
                  values={{
                    id: verdict.superseded_by.id,
                    date: formatDate(verdict.superseded_by.published, lang),
                  }}
                  lang={NOTICE_LANG}
                />
              </a>
            </dd>
          </>
        )}
        <dt>{r.checked}</dt>
        <dd>{formatDateTime(verdict.checked_at, lang)}</dd>
        <dt>{r.recordAsOf}</dt>
        <dd>{formatDateTime(verdict.record_as_of, lang)}</dd>
        <dt>{r.code}</dt>
        <dd>{formatCode(verdict.code)}</dd>
      </dl>
      <div className="links">
        {notice && <a href={`/record/${encodeURIComponent(notice.id)}`}>{r.openOriginal}</a>}
        <a href={`/v/${verdict.code}`}>{r.verify}</a>
        {notice && isRealSourceUrl(notice.url) && (
          <a className="secondary-link" href={notice.url} target="_blank" rel="noopener noreferrer">
            {r.viewSource}
          </a>
        )}
      </div>
    </section>
  );
}
