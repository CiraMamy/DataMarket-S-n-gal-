import Link from 'next/link';
import { ArrowRight, MapPinned, TrendingUp } from 'lucide-react';
import { territories } from '@/lib/mock-data';

export default function TerritoriesPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Territoires</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Analyse géographique du Sénégal</h1>
      </header>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center gap-3 text-navy">
            <MapPinned size={18} />
            <h2 className="text-2xl font-semibold">Carte des régions</h2>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-[#F8FAFF] to-[#F5F3EC] p-6">
            <div className="grid grid-cols-2 gap-3 text-sm text-slate-700">
              {territories.map((t) => (
                <div key={t.slug} className="rounded-xl border border-slate-200 bg-white/80 px-3 py-2">
                  {t.name}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center gap-3 text-navy">
            <TrendingUp size={18} />
            <h2 className="text-2xl font-semibold">Comparaison rapide</h2>
          </div>
          <div className="space-y-4">
            {territories.slice(0, 4).map((territory) => (
              <div key={territory.slug} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium text-navy">{territory.name}</p>
                    <p className="text-sm text-textMuted">{territory.indicator}</p>
                  </div>
                  <span className="font-semibold text-slate-900">{territory.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {territories.map((territory) => (
          <article key={territory.slug} className="surface p-5 shadow-soft">
            <p className="text-xs uppercase tracking-[0.15em] text-textMuted">{territory.regionType}</p>
            <h3 className="mt-2 text-xl font-semibold text-navy">{territory.name}</h3>
            <p className="mt-2 text-sm text-slate-600">{territory.description}</p>
            <div className="mt-5 flex items-center justify-between gap-3">
              <span className="font-medium text-slate-900">{territory.value}</span>
              <Link href={`/territories/${territory.slug}`} className="link-arrow">Détails <ArrowRight size={15} /></Link>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
