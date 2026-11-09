import type { Verdict } from "@confam/contract";
import type { Strings } from "@confam/i18n";
import { fill } from "@confam/i18n";
import { formatCode, formatDate, formatDateTime } from "@/lib/format";

/** Official notice id, published date, checked time, record as of, check code, and two links. */
export function Receipt({ verdict, s }: { verdict: Verdict; s: Strings }) {
  const r = s.receipt;
  const { notice } = verdict;
  return (
    <section className="receipt" aria-labelledby="receipt-h">
      <h2 className="headline" id="receipt-h">
        {r.heading}
      </h2>
      <dl>
        <dt>{r.notice}</dt>
        <dd lang="en">{notice ? `${notice.id}, ${notice.title}` : r.noNotice}</dd>
        {notice && (
          <>
            <dt>{r.published}</dt>
            <dd>{formatDate(notice.published)}</dd>
          </>
        )}
        {verdict.superseded_by && (
          <>
            <dt>{r.replacedBy}</dt>
            <dd>
              <a href={`/record/${encodeURIComponent(verdict.superseded_by.id)}`}>
                {fill(r.replacedByValue, {
                  id: verdict.superseded_by.id,
                  date: formatDate(verdict.superseded_by.published),
                })}
              </a>
            </dd>
          </>
        )}
        <dt>{r.checked}</dt>
        <dd>{formatDateTime(verdict.checked_at)}</dd>
        <dt>{r.recordAsOf}</dt>
        <dd>{formatDateTime(verdict.record_as_of)}</dd>
        <dt>{r.code}</dt>
        <dd>{formatCode(verdict.code)}</dd>
      </dl>
      <div className="links">
        {notice && (
          <a href={notice.url} target="_blank" rel="noopener noreferrer">
            {r.openOriginal}
          </a>
        )}
        <a href={`/v/${verdict.code}`}>{r.verify}</a>
      </div>
    </section>
  );
}
