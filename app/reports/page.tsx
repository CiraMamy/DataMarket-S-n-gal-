import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { analyses } from '@/lib/mock-data';

export default function AnalysisDetailPage({ params }: { params: { id: string } }) {
  const analysis = analyses.find((item) => item.id === params.id) ?? analyses[0];

  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <div className="flex items-center gap-3 text-sm text-textMuted">
        <Link href="/analyses" className="inline-flex items-center gap-2 hover:text-navy"><ArrowLeft size={15} /> Retour</Link>
      </div>

      <section className="surface p-6 shadow-soft">
        <p className="text-xs uppercase tracking-[0.18em] text-textMuted">Analyse</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">{analysis.title}</h1>
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Paramètres utilisés</p>
            <p className="mt-3 text-slate-700">{analysis.description}</p>
          </div>
          <aside className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Version</p>
            <p className="mt-3 text-slate-700">{analysis.version}</p>
            <p className="mt-3 text-sm text-slate-600">Mise à jour: {analysis.lastUpdated}</p>
          </aside>
        </div>
      </section>
    </main>
  );
}
