import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getStrings } from "@confam/i18n";
import { RecordEntryView } from "@/components/record/RecordViews";
import { getRecordEntry } from "@/lib/api";
import { resolveLang } from "@/lib/lang";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  return { title: decodeURIComponent(id) };
}

export default async function RecordEntryPage({ params }: Props) {
  const { id } = await params;
  const entry = await getRecordEntry(decodeURIComponent(id));
  if (!entry) notFound();
  const lang = await resolveLang();
  const { s } = getStrings(lang);
  return <RecordEntryView entry={entry} s={s} lang={lang} />;
}
