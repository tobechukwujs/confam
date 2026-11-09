import { getStrings } from "@confam/i18n";
import { resolveLang } from "@/lib/lang";

export default async function RecordNotFound() {
  const { s } = getStrings(await resolveLang());
  return (
    <div className="answer" style={{ maxWidth: 640 }}>
      <h1 className="display">{s.record.notFoundTitle}</h1>
      <p>{s.record.notFoundBody}</p>
      <a className="btn btn-primary" href="/record">
        {s.record.back}
      </a>
    </div>
  );
}
