/**
 * "old to new". Andika has no arrow glyph, so a text arrow would fall back to a system
 * font. This draws one as a small pen mark, and says the word ("to") for screen readers.
 */
export function Arrow({ label }: { label: string }) {
  return (
    <span className="arrow">
      <svg viewBox="0 0 24 12" aria-hidden="true" focusable="false">
        <path d="M1 6.5 C8 5.5, 15 6.5, 22 6 M17 1.5 L22.5 6 L17 10.5" />
      </svg>
      <span className="sr-only"> {label} </span>
    </span>
  );
}
