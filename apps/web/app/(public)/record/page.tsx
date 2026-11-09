import type { Metadata } from "next";
import { getStrings } from "@confam/i18n";
import { RecordIndexView } from "@/components/record/RecordViews";
import { getRecordList } from "@/lib/api";
import { resolveLang } from "@/lib/lang";

export async function generateMetadata(): Promise<Metadata> {
  const { s } = getStrings(await resolveLang());
  return { title: s.record.title };
}

export default async function RecordPage() {
  const lang = await resolveLang();
  const { s } = getStrings(lang);
  const list = await getRecordList();
  return <RecordIndexView list={list} s={s} lang={lang} />;
}
