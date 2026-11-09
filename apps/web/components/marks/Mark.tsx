// Pen marks. Each is drawn as a stroke that fits its target (SVG stretched with
// preserveAspectRatio="none"), so they ride above the text and never edit it.
// TODO: port assets/marks.js from the confam-ui prototype once it is available;
// these are first-pass shapes. Drawn with pathLength=1 so the Pen animation works.

export type MarkKind = "ring" | "strike" | "caret" | "tick" | "cross" | "unsure" | "bracket";
export type Tone = "red" | "green" | "pencil";

const SHAPES: Record<MarkKind, string[]> = {
  ring: ["M 6 52 C 3 16, 42 3, 78 8 C 102 13, 99 72, 66 91 C 36 105, 5 90, 9 44"],
  strike: ["M 1 55 C 26 44, 60 62, 99 46"],
  caret: ["M 20 72 L 50 24 L 80 72"],
  tick: ["M 9 55 L 38 86 L 92 14"],
  cross: ["M 5 7 C 40 40, 60 62, 95 94", "M 95 6 C 60 38, 40 62, 5 93"],
  unsure: [
    "M 10 50 C 8 18, 40 6, 66 10 C 94 15, 94 72, 66 90 C 36 104, 8 88, 12 46",
    "M 38 38 C 38 22, 64 22, 64 38 C 64 50, 50 52, 50 64",
    "M 50 76 L 50 77",
  ],
  bracket: ["M 14 3 L 3 3 L 3 97 L 14 97", "M 86 3 L 97 3 L 97 97 L 86 97"],
};

const DEFAULT_FIT: Record<MarkKind, string> = {
  ring: "fit",
  strike: "fit",
  caret: "fit",
  bracket: "fit",
  cross: "cross-over",
  tick: "big",
  unsure: "big",
};

export function Mark({
  kind,
  tone,
  className,
  animate = true,
}: {
  kind: MarkKind;
  tone: Tone;
  className?: string;
  animate?: boolean;
}) {
  const fit = className ?? DEFAULT_FIT[kind];
  const stretch = fit !== "big";
  return (
    <svg
      className={`mark mark-${kind} tone-${tone} ${fit}${animate ? " pen" : ""}`}
      viewBox="0 0 100 100"
      preserveAspectRatio={stretch ? "none" : "xMidYMid meet"}
      aria-hidden="true"
      focusable="false"
      data-mark={kind}
    >
      {SHAPES[kind].map((d) => (
        <path key={d} d={d} pathLength={1} />
      ))}
    </svg>
  );
}
