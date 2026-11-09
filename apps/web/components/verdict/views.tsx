import type { Change, Conflict, Verdict } from "@confam/contract";
import { NOTICE_LANG } from "@/lib/format";
import { pickReplacedChange, splitDate } from "@/lib/replaced";
import { Mark } from "../marks/Mark";
import { Pin } from "../sheet/Pin";

// One stage per verdict: the marked figure. Marks ride above the text and never edit it.
// Pins pair with rows in the "What changed" list (see VerdictLayout).

const isLong = (value: string) => value.length > 10;

export function ConfirmedStage() {
  return (
    <div className="stage-tick">
      <Mark kind="tick" tone="green" />
    </div>
  );
}

/** The value of the OLD notice, with its day big and month small when it is a date. */
function FigureValue({ value }: { value: string }) {
  const split = splitDate(value);
  if (!split) return <>{value}</>;
  return (
    <>
      <span className="figure-main">{split.main}</span>
      <span className="figure-sub">{split.rest}</span>
    </>
  );
}

/**
 * "Real, but replaced": the changed fact, not notice ids. The old value (what the copy
 * says) sits in pencil brackets and the new value is handwritten above it in pencil.
 * "now" is interface text, so it is set in Andika, not in the hand font.
 */
export function ReplacedStage({ verdict, nowLabel }: { verdict: Verdict; nowLabel: string }) {
  const picked = pickReplacedChange(verdict);
  if (!picked) {
    // Nothing expressible as a fact: bracket the old notice's title instead of showing ids.
    return <PartialStage verdict={verdict} />;
  }
  const { change, index } = picked;
  const oldValue = change.copy ?? "";
  const newValue = change.official ?? "";
  return (
    <div className="stage">
      {newValue && (
        <span className="hand-line hand-reveal">
          <span className="now-label">{nowLabel}</span>
          <span className="hand tone-pencil" lang={NOTICE_LANG}>
            {newValue}
          </span>
        </span>
      )}
      <div className="figure-row">
        <Pin n={index + 1} tone="pencil" />
        <span className={`figure${isLong(oldValue) && !splitDate(oldValue) ? " long" : ""}`} lang={NOTICE_LANG}>
          {oldValue ? <FigureValue value={oldValue} /> : <span className="gap" />}
          <Mark kind="bracket" tone="pencil" />
        </span>
      </div>
    </div>
  );
}

/** The first change is the marked figure; every change gets a row in the list. */
export function AlteredStage({ change }: { change: Change }) {
  const copy = change.copy ?? "";
  const official = change.official ?? "";
  return (
    <div className="stage">
      {change.op !== "insert" && (
        <span className={`hand tone-red hand-reveal${isLong(official) ? " long" : ""}`} lang={NOTICE_LANG}>
          {official}
        </span>
      )}
      <div className="figure-row">
        <Pin n={1} tone="red" />
        {change.op === "delete" ? (
          <span className="figure">
            <span className="gap" />
            <Mark kind="caret" tone="red" />
          </span>
        ) : (
          <span className={`figure${isLong(copy) ? " long" : ""}`} lang={NOTICE_LANG}>
            {copy}
            <Mark kind={change.op === "insert" ? "strike" : "ring"} tone="red" />
          </span>
        )}
      </div>
    </div>
  );
}

export function NotOfficialStage({ conflict }: { conflict: Conflict }) {
  return (
    <div className="stage">
      <div className="sheet">
        <span className="claim struck" lang={NOTICE_LANG}>
          {conflict.copy}
        </span>
        <Mark kind="cross" tone="red" />
      </div>
      <span className={`hand tone-red hand-reveal${isLong(conflict.official) ? " long" : ""}`} lang={NOTICE_LANG}>
        {conflict.official}
      </span>
    </div>
  );
}

export function PartialStage({ verdict }: { verdict: Verdict }) {
  return (
    <div className="stage">
      <div className="sheet">
        <span className="claim" lang={NOTICE_LANG}>
          {verdict.notice?.title}
          <Mark kind="bracket" tone="pencil" />
        </span>
      </div>
    </div>
  );
}

export function CannotConfirmStage() {
  return (
    <div className="stage-tick">
      <Mark kind="unsure" tone="pencil" />
    </div>
  );
}
