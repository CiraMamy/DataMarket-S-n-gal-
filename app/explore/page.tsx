import Link from 'next/link';
import { ArrowUpDown, FileText, Filter, Map, Search, SlidersHorizontal } from 'lucide-react';
import { dataCards, datasetFilters } from '@/lib/mock-data';

export default function ExplorerPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Explorer</p>
          <h1 className="mt-2 text-4xl font-semibold text-navy">Jeux de données et indicateurs</h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-slate-700 shadow-sm">
            <Search size={16} />
            <input className="w-52 bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder="Recherche rapide" />
          </div>
          <button className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 font-medium text-navy">
            <SlidersHorizontal size={16} /> Filtres
          </button>
        </div>
      </header>

      <section className="grid gap-6 xl:grid-cols-[260px_1fr]">
        <aside className="surface p-5 shadow-soft">
          <div className="mb-4 flex items-center gap-2 text-navy">
            <Filter size={18} />
            <h2 className="text-xl font-semibold">Filtres</h2>
          </div>
          <div className="space-y-5">
            {datasetFilters.map((filter) => (
              <div key={filter.title}>
                <p className="mb-2 text-sm font-medium text-slate-600">{filter.title}</p>
                <div className="space-y-2">
                  {filter.values.map((value) => (
                    <label key={value} className="flex items-center gap-2 text-sm text-slate-700">
                      <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-navy" />
                      {value}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>

        <div className="space-y-5">
          <div className="surface flex flex-col gap-4 p-4 shadow-soft md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <span className="chip">12 résultats</span>
              <span className="chip">Dernière mise à jour</span>
            </div>
            <div className="flex items-center gap-3">
              <button className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700">
                <ArrowUpDown size={15} /> Trier
              </button>
              <button className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700">
                <FileText size={15} /> Vue liste
              </button>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            {dataCards.map((dataset) => (
              <article key={dataset.id} className="surface p-5 shadow-soft">
                <div className="mb-4 flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.15em] text-textMuted">{dataset.category}</p>
                    <h3 className="mt-2 text-xl font-semibold text-navy">{dataset.name}</h3>
                  </div>
                  <span className="chip">{dataset.status}</span>
                </div>

                <p className="text-sm text-slate-600">{dataset.description}</p>

                <div className="mt-4 grid gap-2 text-sm text-slate-600">
                  <div className="flex items-center justify-between"><span>Source</span><span className="font-medium text-slate-700">{dataset.source}</span></div>
                  <div className="flex items-center justify-between"><span>Période</span><span className="font-medium text-slate-700">{dataset.period}</span></div>
                  <div className="flex items-center justify-between"><span>Zone</span><span className="font-medium text-slate-700">{dataset.territory}</span></div>
                </div>

                <div className="mt-5 flex items-center justify-between gap-3">
                  <span className="chip">{dataset.frequency}</span>
                  <Link href={`/explore/${dataset.id}`} className="link-arrow">Voir la fiche <ArrowRight size={15} /></Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
