/* GENERATED from packages/contract/job.schema.json by `pnpm contract:gen`. DO NOT EDIT. Shape only: cross-field rules are in the schema. */

/**
 * Progress of a photo check. POST /v1/checks with an image returns 202 with only {job_id}; GET /v1/checks/{job_id} returns this. The stage is the real step the server is on. There is no progress percentage and no confidence (CLAUDE.md rule 4). When status is done, `code` is the check code to open at /v/{code}.
 */
export interface Job {
  job_id: string;
  status: "working" | "done" | "failed";
  stage: "queued" | "reading_1" | "reading_2" | "comparing" | "done" | "failed";
  /**
   * The check code (8 characters, no hyphen). Present only when status is done.
   */
  code: string | null;
}
