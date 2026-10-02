import Link from 'next/link';
import { ArrowRight, FileText, Search } from 'lucide-react';
import { analyses } from '@/lib/mock-data';

export default function AnalysesPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Analyses</p>
          <h1 className="mt-2 text-4xl font-semibold text-navy">Bibliothèque d’analyses</h1>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-slate-700 shadow-sm">
          <Search size={16} />
          <input className="w-52 bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder="Rechercher" />
        </div>
      </header>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {analyses.map((analysis) => (
          <article key={analysis.id} className="surface p-5 shadow-soft">
            <div className="mb-4 flex items-center justify-between">
              <span className="chip">{analysis.status}</span>
              <FileText size={16} className="text-slate-500" />
            </div>
            <h2 className="text-xl font-semibold text-navy">{analysis.title}</h2>
            <p className="mt-3 text-sm text-slate-600">{analysis.description}</p>
            <div className="mt-4 text-sm text-slate-600">
              <div className="flex justify-between"><span>Version</span><span className="font-medium text-slate-900">{analysis.version}</span></div>
              <div className="mt-2 flex justify-between"><span>Dernière mise à jour</span><span className="font-medium text-slate-900">{analysis.lastUpdated}</span></div>
            </div>
            <Link href={`/analyses/${analysis.id}`} className="mt-5 inline-flex items-center gap-2 link-arrow">Voir le détail <ArrowRight size={15} /></Link>
          </article>
        ))}
      </section>
    </main>
  );
}
