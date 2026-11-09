import type { Metadata } from "next";
import { getStrings } from "@confam/i18n";
import { RecordIndexView } from "@/components/record/RecordViews";
import { getRecordList } from "@/lib/api";

export const metadata: Metadata = { title: "The official record" };

export default async function RecordPage() {
  const { s } = getStrings("en");
  const list = await getRecordList();
  return <RecordIndexView list={list} s={s} />;
}
