import { Suspense } from 'react';
import { PageHeader } from '@/components/page-header';
import { LoadingState } from '@/components/loading-state';
import Link from 'next/link';
import { ArrowRight, FileText, TrendingUp } from 'lucide-react';

const recentReports = [
  { id: '1', title: 'Rapport marché Dakar', date: 'Hier' },
  { id: '2', title: 'Synthèse territoriale', date: 'Il y a 3 jours' },
  { id: '3', title: 'Analyse sectorielle', date: 'Il y a 1 semaine' },
];

function ReportsList() {
  return (
    <div className="space-y-3">
      {recentReports.map((report) => (
        <div key={report.id} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center gap-3">
            <FileText size={16} className="text-navy" />
            <div>
              <p className="font-medium text-navy">{report.title}</p>
              <p className="text-sm text-textMuted">{report.date}</p>
            </div>
          </div>
          <Link href={`/reports/${report.id}`} className="link-arrow">
            Ouvrir <ArrowRight size={15} />
          </Link>
        </div>
      ))}
    </div>
  );
}

export default function ReportsListPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <PageHeader eyebrow="Rapports" title="Espace de rapports" />

      <section className="grid gap-6 md:grid-cols-3">
        <div className="surface p-6 shadow-soft">
          <div className="flex items-center gap-2 text-navy mb-3">
            <FileText size={18} />
            <p className="font-medium">Rapports générés</p>
          </div>
          <p className="text-3xl font-semibold text-navy">12</p>
          <p className="mt-2 text-sm text-textMuted">+2 cette semaine</p>
        </div>
        <div className="surface p-6 shadow-soft">
          <div className="flex items-center gap-2 text-navy mb-3">
            <TrendingUp size={18} />
            <p className="font-medium">En cours de génération</p>
          </div>
          <p className="text-3xl font-semibold text-navy">3</p>
          <p className="mt-2 text-sm text-textMuted">Temps moyen: 2 min</p>
        </div>
        <div className="surface p-6 shadow-soft">
          <div className="flex items-center gap-2 text-navy mb-3">
            <FileText size={18} />
            <p className="font-medium">Brouillons</p>
          </div>
          <p className="text-3xl font-semibold text-navy">5</p>
          <p className="mt-2 text-sm text-textMuted">À finaliser</p>
        </div>
      </section>

      <section className="surface p-6 shadow-soft">
        <h2 className="mb-5 text-2xl font-semibold text-navy">Rapports récents</h2>
        <Suspense fallback={<LoadingState />}>
          <ReportsList />
        </Suspense>
      </section>
    </main>
  );
}
