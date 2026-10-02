import Link from 'next/link';
import { ArrowRight, FileArchive } from 'lucide-react';
import { reports } from '@/lib/mock-data';

export default function ReportsPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Rapports</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Espace de rapports</h1>
      </header>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {reports.map((report) => (
          <article key={report.id} className="surface p-5 shadow-soft">
            <div className="mb-4 flex items-center justify-between">
              <span className="chip">{report.state}</span>
              <FileArchive size={16} className="text-slate-500" />
            </div>
            <h2 className="text-xl font-semibold text-navy">{report.title}</h2>
            <p className="mt-3 text-sm text-slate-600">{report.summary}</p>
            <div className="mt-4 text-sm text-slate-700">
              <div className="flex justify-between"><span>Version</span><span className="font-medium text-slate-900">{report.version}</span></div>
            </div>
            <Link href={`/reports/${report.id}`} className="mt-5 inline-flex items-center gap-2 link-arrow">Voir le rapport <ArrowRight size={15} /></Link>
          </article>
        ))}
      </section>
    </main>
  );
}
