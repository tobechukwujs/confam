import type { Verdict } from "@confam/contract";
import { fill, type Lang, type Strings, type VerdictCopy } from "@confam/i18n";
import { NOTICE_LANG, formatDate, isSample, viewKey, type ViewKey } from "@/lib/format";
import { Filled } from "../Filled";
import { PhotoPanel } from "../photo/PhotoPanel";
import { Arrow } from "../sheet/Arrow";
import { Pin } from "../sheet/Pin";
import { Receipt } from "../sheet/Receipt";
import { ShareButton } from "../sheet/ShareButton";
import {
  AlteredStage,
  CannotConfirmStage,
  ConfirmedStage,
  NotOfficialStage,
  PartialStage,
  ReplacedStage,
} from "./views";

function copyFor(v: Verdict, key: ViewKey, s: Strings): VerdictCopy {
  if (key === "cannot_confirm") return s.verdict.cannot_confirm[v.reason ?? "not_in_record"];
  return s.verdict[key];
}

function Stage({ v, key_, s }: { v: Verdict; key_: ViewKey; s: Strings }) {
  switch (key_) {
    case "confirmed":
      return <ConfirmedStage />;
    case "replaced":
      return <ReplacedStage verdict={v} nowLabel={s.changes.now} />;
    case "altered":
      return v.changes[0] ? <AlteredStage change={v.changes[0]} /> : <CannotConfirmStage />;
    case "not_official":
      return v.conflicts[0] ? <NotOfficialStage conflict={v.conflicts[0]} /> : <CannotConfirmStage />;
    case "partial":
      return <PartialStage verdict={v} />;
    case "cannot_confirm":
      return <CannotConfirmStage />;
  }
}

function Action({
  v,
  key_,
  copy,
  s,
  lang,
}: {
  v: Verdict;
  key_: ViewKey;
  copy: VerdictCopy;
  s: Strings;
  lang: Lang;
}) {
  const share = { copiedText: s.share.copied, failedText: s.share.copyFailed, lang };
  switch (key_) {
    case "confirmed":
      return <ShareButton label={copy.action} text="" {...share} />;
    case "replaced":
      return (
        <ShareButton
          label={copy.action}
          text={fill(s.share.currentNoticeText, {
            id: v.superseded_by?.id ?? "",
            date: v.superseded_by ? formatDate(v.superseded_by.published, lang) : "",
          })}
          url={v.superseded_by ? `/record/${encodeURIComponent(v.superseded_by.id)}` : undefined}
          {...share}
        />
      );
    case "altered":
    case "not_official":
      return v.notice ? (
        <ShareButton
          label={copy.action}
          text={fill(s.share.correctNoticeText, { title: v.notice.title })}
          url={`/record/${encodeURIComponent(v.notice.id)}`}
          {...share}
        />
      ) : null;
    case "partial":
      return v.notice ? (
        <a className="btn btn-primary" href={`/record/${encodeURIComponent(v.notice.id)}`}>
          {copy.action}
        </a>
      ) : null;
    case "cannot_confirm":
      return (
        <a className="btn btn-primary" href={v.reason === "unclear" || v.reason === "line_missing" ? "/#upload" : "/"}>
          {copy.action}
        </a>
      );
  }
}

/** "Real, but replaced": what the newer notice changed. copy = old value, official = new value. */
function ReplacedRows({ v, s }: { v: Verdict; s: Strings }) {
  const c = s.changes;
  const changes = v.superseded_by?.changes ?? [];
  return (
    <>
      <p>{changes.length > 0 ? c.replacedIntro : c.replacedNone}</p>
      {changes.length > 0 && (
        <ol className="changes">
          {changes.map((ch, i) => (
            <li key={i}>
              <Pin n={i + 1} tone="pencil" />
              <p>
                <span className="kind">{c.kinds[ch.kind]}: </span>
                {ch.op === "replace" ? (
                  // old value, an arrow, new value (copy = old, official = new)
                  <>
                    <span lang={NOTICE_LANG}>{ch.copy}</span>
                    <Arrow label={c.to} />
                    <span lang={NOTICE_LANG}>{ch.official}</span>
                  </>
                ) : (
                  <Filled
                    template={ch.op === "insert" ? c.rowInsert : c.rowDelete}
                    values={{ copy: ch.copy ?? "", official: ch.official ?? "" }}
                    lang={NOTICE_LANG}
                  />
                )}
              </p>
            </li>
          ))}
        </ol>
      )}
    </>
  );
}

/** Rows for the "What changed" list; each pairs with a Pin on the sheet. */
function ChangeRows({ v, s }: { v: Verdict; s: Strings }) {
  const c = s.changes;
  const rows: { kind: string; template: string; values: Record<string, string>; tone: "red" }[] = [
    ...v.changes.map((ch) => ({
      kind: c.kinds[ch.kind],
      template: c[ch.op],
      values: { copy: ch.copy ?? "", official: ch.official ?? "" },
      tone: "red" as const,
    })),
    ...v.conflicts.map((cf) => ({
      kind: c.conflictKinds[cf.kind],
      template: c.conflict,
      values: { copy: cf.copy, official: cf.official },
      tone: "red" as const,
    })),
  ];
  if (rows.length === 0) return <p>{c.none}</p>;
  return (
    <ol className="changes">
      {rows.map((row, i) => (
        <li key={i}>
          <Pin n={i + 1} tone={row.tone} />
          <p>
            <span className="kind">{row.kind}. </span>
            <Filled template={row.template} values={row.values} lang={NOTICE_LANG} />
          </p>
        </li>
      ))}
    </ol>
  );
}

export function VerdictLayout({ verdict, s, lang }: { verdict: Verdict; s: Strings; lang: Lang }) {
  const key = viewKey(verdict);
  const copy = copyFor(verdict, key, s);
  return (
    <div className="spread" data-verdict={key}>
      <span className="staple top" aria-hidden="true" />
      <span className="staple bottom" aria-hidden="true" />
      <section className="answer" aria-labelledby="verdict-word">
        <h1 className="display" id="verdict-word">
          {copy.word}
        </h1>
        <Stage v={verdict} key_={key} s={s} />
        <p>{copy.sentence}</p>
        <p>{copy.instruction}</p>
        <div className="actions">
          <Action v={verdict} key_={key} copy={copy} s={s} lang={lang} />
        </div>
      </section>
      <section className="proof" aria-label={s.receipt.heading}>
        {/* The person's own photo with the marks on it. Renders only while this tab still holds it. */}
        <PhotoPanel code={verdict.code} changes={verdict.changes} s={s.photo} />
        {/* Nothing was compared when we cannot confirm, so do not claim "no differences". */}
        {key !== "cannot_confirm" && (
          <div>
            <h2 className="headline">{s.changes.heading}</h2>
            {key === "replaced" ? <ReplacedRows v={verdict} s={s} /> : <ChangeRows v={verdict} s={s} />}
          </div>
        )}
        {isSample(verdict) && <p className="sample-note">{s.sampleNotice}</p>}
        <Receipt verdict={verdict} s={s} lang={lang} />
      </section>
    </div>
  );
}
