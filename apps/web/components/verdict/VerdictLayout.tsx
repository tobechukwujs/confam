import type { Verdict } from "@confam/contract";
import { fill, type Strings, type VerdictCopy } from "@confam/i18n";
import { isSample, viewKey, formatDate, type ViewKey } from "@/lib/format";
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

function Stage({ v, key_ }: { v: Verdict; key_: ViewKey }) {
  switch (key_) {
    case "confirmed":
      return <ConfirmedStage />;
    case "replaced":
      return <ReplacedStage verdict={v} />;
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

function Action({ v, key_, copy, s }: { v: Verdict; key_: ViewKey; copy: VerdictCopy; s: Strings }) {
  const share = { copiedText: s.share.copied, failedText: s.share.copyFailed };
  switch (key_) {
    case "confirmed":
      return <ShareButton label={copy.action} text="" {...share} />;
    case "replaced":
      return (
        <ShareButton
          label={copy.action}
          text={fill(s.share.currentNoticeText, {
            id: v.superseded_by?.id ?? "",
            date: v.superseded_by ? formatDate(v.superseded_by.published) : "",
          })}
          {...share}
        />
      );
    case "altered":
    case "not_official":
      return v.notice ? (
        <ShareButton
          label={copy.action}
          text={fill(s.share.correctNoticeText, { title: v.notice.title })}
          url={v.notice.url}
          {...share}
        />
      ) : null;
    case "partial":
      return v.notice ? (
        <a className="btn btn-primary" href={v.notice.url} target="_blank" rel="noopener noreferrer">
          {copy.action}
        </a>
      ) : null;
    case "cannot_confirm":
      return (
        <a className="btn btn-primary" href="/">
          {copy.action}
        </a>
      );
  }
}

/** Rows for the "What changed" list; each pairs with a Pin on the sheet. */
function ChangeRows({ v, s }: { v: Verdict; s: Strings }) {
  const c = s.changes;
  const rows: { kind: string; text: string; tone: "red" }[] = [
    ...v.changes.map((ch) => ({
      kind: c.kinds[ch.kind],
      text: fill(c[ch.op], {
        copy: ch.copy ?? "",
        official: ch.official ?? "",
      }),
      tone: "red" as const,
    })),
    ...v.conflicts.map((cf) => ({
      kind: c.conflictKinds[cf.kind],
      text: fill(c.conflict, { copy: cf.copy, official: cf.official }),
      tone: "red" as const,
    })),
  ];
  if (rows.length === 0) return <p>{c.none}</p>;
  return (
    <ol className="changes">
      {rows.map((row, i) => (
        <li key={i}>
          <Pin n={i + 1} tone={row.tone} />
          <p lang="en">
            <span className="kind">{row.kind}. </span>
            {row.text}
          </p>
        </li>
      ))}
    </ol>
  );
}

export function VerdictLayout({ verdict, s }: { verdict: Verdict; s: Strings }) {
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
        <Stage v={verdict} key_={key} />
        <p>{copy.sentence}</p>
        <p>{copy.instruction}</p>
        <div className="actions">
          <Action v={verdict} key_={key} copy={copy} s={s} />
        </div>
      </section>
      <section className="proof" aria-label={s.receipt.heading}>
        {/* Nothing was compared when we cannot confirm, so do not claim "no differences". */}
        {key !== "cannot_confirm" && (
          <div>
            <h2 className="headline">{s.changes.heading}</h2>
            <ChangeRows v={verdict} s={s} />
          </div>
        )}
        {isSample(verdict) && <p className="sample-note">{s.sampleNotice}</p>}
        <Receipt verdict={verdict} s={s} />
      </section>
    </div>
  );
}
