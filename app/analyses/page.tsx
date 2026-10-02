import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { territories } from '@/lib/mock-data';

export default function TerritoryPage({ params }: { params: { slug: string } }) {
  const territory = territories.find((item) => item.slug === params.slug) ?? territories[0];

  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <div className="flex items-center gap-3 text-sm text-textMuted">
        <Link href="/territories" className="inline-flex items-center gap-2 hover:text-navy"><ArrowLeft size={15} /> Retour</Link>
      </div>

      <section className="surface p-6 shadow-soft">
        <p className="text-xs uppercase tracking-[0.18em] text-textMuted">Territoire</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">{territory.name}</h1>
        <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="font-medium text-navy">Fiche territoriale</p>
              <p className="mt-2 text-slate-600">{territory.description}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="font-medium text-navy">Indicateurs disponibles</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Population</li>
                <li>Dépense moyenne par tête</li>
                <li>Potentiel de marché</li>
                <li>Couverture territoriale</li>
              </ul>
            </div>
          </div>

          <aside className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Indicateurs</p>
            <dl className="mt-4 space-y-3 text-sm text-slate-700">
              <div className="flex justify-between"><dt>Potentiel</dt><dd className="font-medium text-slate-900">{territory.value}</dd></div>
              <div className="flex justify-between"><dt>Population</dt><dd className="font-medium text-slate-900">{territory.population}</dd></div>
              <div className="flex justify-between"><dt>Période</dt><dd className="font-medium text-slate-900">2023</dd></div>
            </dl>
          </aside>
        </div>
      </section>
    </main>
  );
}
