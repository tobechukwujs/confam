import type { Metadata, Viewport } from "next";
import { Andika, Playwrite_NG_Modern } from "next/font/google";
import { getStrings } from "@confam/i18n";
import "../styles/globals.css";

// Andika for all interface text (latin-ext covers Hausa, Yoruba and Igbo letters).
const andika = Andika({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "700"],
  display: "swap",
  variable: "--font-andika",
});

// Playwrite NG Modern is for handwritten corrections only, never interface copy.
const hand = Playwrite_NG_Modern({
  weight: "400",
  display: "swap",
  variable: "--font-hand",
});

export const metadata: Metadata = {
  title: { default: "Confam", template: "%s | Confam" },
  description:
    "Check a forwarded election notice against the official record. Independent checker. Not INEC or any party.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const { s } = getStrings("en");
  return (
    <html lang="en" className={`${andika.variable} ${hand.variable}`}>
      <body>
        <a className="skip" href="#main">
          Skip to the page
        </a>
        <header className="cover">
          <a className="brand" href="/">
            {s.appName}
          </a>
          <span className="lang">{s.languageName}</span>
        </header>
        <main id="main" className="book">
          {children}
        </main>
        <footer className="footer">
          <p>{s.independence}</p>
        </footer>
      </body>
    </html>
  );
}
