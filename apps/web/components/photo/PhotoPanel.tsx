"use client";

import { useEffect, useState } from "react";
import type { Change } from "@confam/contract";
import type { Strings } from "@confam/i18n";
import { imageForCode } from "@/lib/pending-image";
import { Mark, type MarkKind } from "../marks/Mark";
import { Pin } from "../sheet/Pin";

const KIND: Record<Change["op"], MarkKind> = { replace: "ring", insert: "strike", delete: "caret" };

/**
 * "Your photo, marked": the person's own photo with a red mark at each box. The photo is read
 * from this browser tab's memory (see lib/pending-image.ts), so after a reload or on a shared
 * link there is nothing to show and this renders nothing; the text sheet above still answers.
 */
export function PhotoPanel({ code, changes, s }: { code: string; changes: Change[]; s: Strings["photo"] }) {
  const [url, setUrl] = useState<string | undefined>();
  useEffect(() => setUrl(imageForCode(code)), [code]);
  if (!url) return null;

  return (
    <section className="photo-panel" aria-labelledby="photo-h">
      <h2 className="headline" id="photo-h">
        {s.heading} <span className="beta">{s.beta}</span>
      </h2>
      <p className="label">{s.note}</p>
      <div className="photo-frame">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={url} alt={s.alt} />
        {changes.map((change, i) =>
          change.box ? (
            <span
              key={i}
              className="photo-mark"
              style={{
                left: `${change.box[0] * 100}%`,
                top: `${change.box[1] * 100}%`,
                width: `${change.box[2] * 100}%`,
                height: `${change.box[3] * 100}%`,
              }}
            >
              <Mark kind={KIND[change.op]} tone="red" className="fit" />
              <Pin n={i + 1} tone="red" />
            </span>
          ) : null,
        )}
      </div>
    </section>
  );
}
