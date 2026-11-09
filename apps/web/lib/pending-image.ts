// The picture a person sent, kept ONLY in this browser tab's memory (rule 7).
// Nothing here is saved: no localStorage, sessionStorage, cookie, or request to any server.
// It lives until the tab is reloaded or closed, so a reload or a shared link shows the text
// sheet instead. A Map keyed by job, then by check code, survives client-side navigation.

const byJob = new Map<string, string>();
const byCode = new Map<string, string>();

const normal = (code: string) => code.replace(/-/g, "").toUpperCase();

export function rememberForJob(jobId: string, objectUrl: string): void {
  byJob.set(jobId, objectUrl);
}

export function moveToCode(jobId: string, code: string): void {
  const url = byJob.get(jobId);
  if (!url) return;
  byJob.delete(jobId);
  byCode.set(normal(code), url);
}

export function imageForCode(code: string): string | undefined {
  return byCode.get(normal(code));
}

export function forgetAllImages(): void {
  for (const url of [...byJob.values(), ...byCode.values()]) {
    try {
      URL.revokeObjectURL(url);
    } catch {
      /* not a real object URL (tests) */
    }
  }
  byJob.clear();
  byCode.clear();
}
