import { getStrings } from "@confam/i18n";
import { CheckForm } from "@/components/CheckForm";
import { UploadZone } from "@/components/photo/UploadZone";
import { resolveLang } from "@/lib/lang";

export default async function Home() {
  const lang = await resolveLang();
  const { s } = getStrings(lang);
  // Sample links only where the API is seeded with the fictional sample verdicts.
  const showSamples = process.env.SHOW_SAMPLES === "1";
  return (
    <div className="answer" style={{ maxWidth: 640 }}>
      <h1 className="display">{s.home.title}</h1>
      <p>{s.home.lead}</p>
      <CheckForm s={s.home} lang={lang} />
      <UploadZone s={s.upload} lang={lang} />
      {showSamples && (
        <section aria-labelledby="samples-h" style={{ marginTop: "var(--double-line)" }}>
          <h2 className="headline" id="samples-h">
            {s.home.samplesTitle}
          </h2>
          <p className="label">{s.home.samplesNote}</p>
          <ul className="samples">
            {s.home.samples.map((sample) => (
              <li key={sample.code}>
                <a href={`/v/${sample.code}`}>{sample.label}</a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
