import type { Metadata, Viewport } from "next";
import { Andika, Playwrite_NG_Modern } from "next/font/google";
import { getStrings } from "@confam/i18n";
import { LangSwitch } from "@/components/LangSwitch";
import { currentLocation, resolveLang } from "@/lib/lang";
import "../styles/globals.css";

// Andika for all interface text (latin-ext covers Hausa, Yoruba and Igbo letters).
const andika = Andika({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "700"],
  display: "swap",
  variable: "--font-andika",
});

// Playwrite NG Modern is for handwritten corrections only, never interface copy.
// It has no Hausa hooked letters or Yoruba/Igbo dotted letters.
const hand = Playwrite_NG_Modern({
  weight: "400",
  display: "swap",
  variable: "--font-hand",
});

export async function generateMetadata(): Promise<Metadata> {
  const { s } = getStrings(await resolveLang());
  return {
    title: { default: s.appName, template: `%s | ${s.appName}` },
    description: s.independence,
  };
}

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const lang = await resolveLang();
  const { path, search } = await currentLocation();
  const { s, draft } = getStrings(lang);
  return (
    <html lang={lang} className={`${andika.variable} ${hand.variable}`}>
      <body>
        <a className="skip" href="#main">
          {s.skipLink}
        </a>
        <header className="cover">
          <a className="brand" href="/">
            {s.appName}
          </a>
          {/* Every non-English screen says its words are an unreviewed draft. */}
          {draft && <span className="draft-label">{s.draftTranslation}</span>}
          <LangSwitch current={lang} path={path} search={search} label={s.languageMenu} />
        </header>
        <main id="main" className="book">
          {children}
        </main>
        <footer className="footer">
          <p>
            <a href="/record">{s.record.nav}</a>
          </p>
          <p>{s.independence}</p>
        </footer>
      </body>
    </html>
  );
}
