import Link from 'next/link';
import { ArrowLeft, BarChart3, CalendarClock, Database, MapPinned, ShieldCheck } from 'lucide-react';
import { datasetDetail } from '@/lib/mock-data';

export default function DatasetDetailPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <div className="flex items-center gap-3 text-sm text-textMuted">
        <Link href="/explore" className="inline-flex items-center gap-2 hover:text-navy"><ArrowLeft size={15} /> Retour</Link>
      </div>

      <section className="surface p-6 shadow-soft">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-textMuted">{datasetDetail.category}</p>
            <h1 className="mt-2 text-4xl font-semibold text-navy">{datasetDetail.name}</h1>
          </div>
          <span className="chip">{datasetDetail.status}</span>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5">
            <p className="text-slate-700">{datasetDetail.description}</p>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-navy"><Database size={16} /> <span className="font-medium">Méthodologie</span></div>
                <p className="mt-3 text-sm text-slate-600">{datasetDetail.methodology}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-navy"><ShieldCheck size={16} /> <span className="font-medium">Provenance</span></div>
                <p className="mt-3 text-sm text-slate-600">{datasetDetail.provenance}</p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><BarChart3 size={16} /> <span className="font-medium">Aperçu des observations</span></div>
              <div className="mt-4 h-52 rounded-xl bg-gradient-to-r from-[#EFF4FF] to-[#F8F4E8] p-4">
                <div className="flex h-full items-end gap-2">
                  {[28, 40, 35, 52, 66, 60, 78, 72, 92].map((height, i) => (
                    <div key={i} className="flex-1 rounded-t-xl bg-navy/80" style={{ height: `${height}%` }} />
                  ))}
                </div>
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Métadonnées</p>
              <dl className="mt-4 space-y-3 text-sm text-slate-700">
                <div className="flex justify-between gap-3"><dt>Source</dt><dd className="font-medium text-slate-900">{datasetDetail.source}</dd></div>
                <div className="flex justify-between gap-3"><dt>Zone</dt><dd className="font-medium text-slate-900">{datasetDetail.territory}</dd></div>
                <div className="flex justify-between gap-3"><dt>Période</dt><dd className="font-medium text-slate-900">{datasetDetail.period}</dd></div>
                <div className="flex justify-between gap-3"><dt>Fréquence</dt><dd className="font-medium text-slate-900">{datasetDetail.frequency}</dd></div>
                <div className="flex justify-between gap-3"><dt>Licence</dt><dd className="font-medium text-slate-900">{datasetDetail.license}</dd></div>
              </dl>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><CalendarClock size={16} /> <span className="font-medium">Dernière mise à jour</span></div>
              <p className="mt-3 text-sm text-slate-700">{datasetDetail.updatedAt}</p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><MapPinned size={16} /> <span className="font-medium">Couverture géographique</span></div>
              <p className="mt-3 text-sm text-slate-700">{datasetDetail.coverage}</p>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
