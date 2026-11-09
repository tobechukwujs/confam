import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getStrings } from "@confam/i18n";
import { VerdictLayout } from "@/components/verdict/VerdictLayout";
import { getVerdict } from "@/lib/api";
import { formatCode } from "@/lib/format";
import { resolveLang } from "@/lib/lang";

type Props = { params: Promise<{ code: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { code } = await params;
  return { title: `Check ${formatCode(code.replace(/-/g, "").toUpperCase())}`, robots: { index: false } };
}

export default async function VerdictPage({ params }: Props) {
  const { code } = await params;
  const verdict = await getVerdict(code);
  if (!verdict) notFound();
  // The interface follows the reader's language; official words are never translated.
  const lang = await resolveLang();
  const { s } = getStrings(lang);
  return <VerdictLayout verdict={verdict} s={s} lang={lang} />;
}
