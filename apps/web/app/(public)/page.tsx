import { getStrings } from "@confam/i18n";
import { CheckForm } from "@/components/CheckForm";

export default function Home() {
  const { s } = getStrings("en");
  // Sample links only where the API is seeded with the fictional sample verdicts.
  const showSamples = process.env.SHOW_SAMPLES === "1";
  return (
    <div className="answer" style={{ maxWidth: 640 }}>
      <h1 className="display">{s.home.title}</h1>
      <p>{s.home.lead}</p>
      <CheckForm s={s.home} />
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
