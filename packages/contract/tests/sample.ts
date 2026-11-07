// Compile-time check that the generated TypeScript type accepts the contract example.
// Run with `pnpm contract:tsc`.
import type { Verdict } from "../ts/verdict";

export const sample: Verdict = {
  code: "K7Q2M9XA",
  verdict: "altered",
  reason: null,
  lang: "en",
  checked_at: "2026-11-05T14:02:00+01:00",
  record_as_of: "2026-11-05T13:40:00+01:00",
  notice: {
    id: "SEC-2026-114",
    title: "Voter registration deadline",
    published: "2026-09-03",
    url: "https://sec.example/notices/SEC-2026-114",
  },
  superseded_by: null,
  changes: [
    { op: "replace", kind: "date", official: "14th", copy: "15th", box: [0.21, 0.46, 0.08, 0.03] },
  ],
  conflicts: [],
};
