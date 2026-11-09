import type { Metadata } from "next";
import { getStrings } from "@confam/i18n";
import { ReadingScreen } from "@/components/photo/ReadingScreen";
import { resolveLang } from "@/lib/lang";

type Props = { params: Promise<{ job: string }> };

export async function generateMetadata(): Promise<Metadata> {
  const { s } = getStrings(await resolveLang());
  return { title: s.reading.title, robots: { index: false } };
}

export default async function CheckPage({ params }: Props) {
  const { job } = await params;
  const { s } = getStrings(await resolveLang());
  return <ReadingScreen jobId={job} s={s.reading} />;
}
