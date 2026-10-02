import Link from 'next/link';
import { ArrowLeft, BadgeCheck, FileText, TrendingUp } from 'lucide-react';
import { marketStudies } from '@/lib/mock-data';

export default function StudiesPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Analyses</p>
          <h1 className="mt-2 text-4xl font-semibold text-navy">Études de marché</h1>
        </div>
        <Link href="/studies/new" className="rounded-full bg-navy px-5 py-2.5 font-medium text-white">Nouvelle étude</Link>
      </header>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {marketStudies.map((study) => (
          <article key={study.id} className="surface p-5 shadow-soft">
            <div className="mb-4 flex items-center justify-between gap-3">
              <span className="chip">{study.status}</span>
              <span className="text-sm text-textMuted">{study.updatedAt}</span>
            </div>
            <h2 className="text-xl font-semibold text-navy">{study.title}</h2>
            <p className="mt-3 text-sm text-slate-600">{study.summary}</p>
            <div className="mt-4 space-y-2 text-sm text-slate-700">
              <div className="flex justify-between"><span>Territoire</span><span className="font-medium text-slate-900">{study.region}</span></div>
              <div className="flex justify-between"><span>Marché</span><span className="font-medium text-slate-900">{study.market}</span></div>
            </div>
            <div className="mt-5 flex items-center justify-between gap-3">
              <span className="flex items-center gap-2 text-sm font-medium text-emerald-700"><BadgeCheck size={16} /> {study.score}</span>
              <Link href={`/studies/${study.id}`} className="link-arrow">Ouvrir <ArrowRight size={15} /></Link>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
