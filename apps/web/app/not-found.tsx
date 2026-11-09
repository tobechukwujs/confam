import { getStrings } from "@confam/i18n";
import { resolveLang } from "@/lib/lang";

export default async function NotFound() {
  const { s } = getStrings(await resolveLang());
  return (
    <div className="answer" style={{ maxWidth: 640 }}>
      <h1 className="display">{s.notFound.title}</h1>
      <p>{s.notFound.body}</p>
      <a className="btn btn-primary" href="/">
        {s.notFound.back}
      </a>
    </div>
  );
}
