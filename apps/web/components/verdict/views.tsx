import type { Change, Conflict, Verdict } from "@confam/contract";
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

export function ReplacedStage({ verdict }: { verdict: Verdict }) {
  const oldId = verdict.notice?.id ?? "";
  const newId = verdict.superseded_by?.id ?? "";
  return (
    <div className="stage">
      <span className="hand tone-pencil hand-reveal" lang="en">
        {newId}
      </span>
      <span className="notice-id" lang="en">
        {oldId}
        <Mark kind="bracket" tone="pencil" />
      </span>
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
        <span className={`hand tone-red hand-reveal${isLong(official) ? " long" : ""}`} lang="en">
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
          <span className={`figure${isLong(copy) ? " long" : ""}`} lang="en">
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
        <span className="claim struck" lang="en">
          {conflict.copy}
        </span>
        <Mark kind="cross" tone="red" />
      </div>
      <span className={`hand tone-red hand-reveal${isLong(conflict.official) ? " long" : ""}`} lang="en">
        {conflict.official}
      </span>
    </div>
  );
}

export function PartialStage({ verdict }: { verdict: Verdict }) {
  return (
    <div className="stage">
      <div className="sheet">
        <span className="claim" lang="en">
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
