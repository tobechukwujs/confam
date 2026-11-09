import type { Tone } from "../marks/Mark";

/** A numbered ring. Each Pin on the sheet pairs with a row in the "What changed" list. */
export function Pin({ n, tone }: { n: number; tone: Tone }) {
  return (
    <span className={`pin tone-${tone}`} aria-hidden="true" data-pin={n}>
      {n}
    </span>
  );
}
