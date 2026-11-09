// Response shapes of GET /v1/record and GET /v1/record/{id}.
// TODO: hand-written for now; generate from the API's OpenAPI document so they cannot drift.

export type RecordSummary = {
  id: string;
  title: string;
  published: string;
  lang: string;
  superseded_by: { id: string; published: string } | null;
};

export type RecordList = { record_as_of: string; notices: RecordSummary[] };

export type RecordSignature = { reviewer: string; role: "first" | "second"; signed_at: string };

export type RecordEntry = RecordSummary & {
  url: string;
  text: string;
  signatures: RecordSignature[];
};
