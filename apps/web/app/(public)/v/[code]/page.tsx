import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getStrings } from "@confam/i18n";
import { VerdictLayout } from "@/components/verdict/VerdictLayout";
import { getVerdict } from "@/lib/api";
import { formatCode } from "@/lib/format";

type Props = { params: Promise<{ code: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { code } = await params;
  return { title: `Check ${formatCode(code.replace(/-/g, "").toUpperCase())}`, robots: { index: false } };
}

export default async function VerdictPage({ params }: Props) {
  const { code } = await params;
  const verdict = await getVerdict(code);
  if (!verdict) notFound();
  const { s, draft } = getStrings(verdict.lang);
  return (
    <>
      {draft && <p className="draft-label">{s.draftTranslation}</p>}
      <VerdictLayout verdict={verdict} s={s} />
    </>
  );
}
