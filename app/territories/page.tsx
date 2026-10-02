import Link from 'next/link';
import { ArrowLeft, TrendingUp, Sparkles, ShieldCheck } from 'lucide-react';
import { marketStudies } from '@/lib/mock-data';

const study = marketStudies[0];

export default function StudyDetailPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <div className="flex items-center gap-3 text-sm text-textMuted">
        <Link href="/studies" className="inline-flex items-center gap-2 hover:text-navy"><ArrowLeft size={15} /> Retour</Link>
      </div>

      <section className="surface p-6 shadow-soft">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-textMuted">Étude de marché</p>
            <h1 className="mt-2 text-4xl font-semibold text-navy">{study.title}</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="chip">{study.status}</span>
            <span className="chip">{study.market}</span>
          </div>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Synthèse</p>
              <p className="mt-3 text-slate-700">{study.summary}</p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-textMuted">TAM</p>
                <p className="mt-2 text-2xl font-semibold text-navy">200 M FCFA</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-textMuted">SAM</p>
                <p className="mt-2 text-2xl font-semibold text-navy">90 M FCFA</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-textMuted">SOM</p>
                <p className="mt-2 text-2xl font-semibold text-navy">27 M FCFA</p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><TrendingUp size={16} /> <span className="font-medium">Tendances</span></div>
              <p className="mt-3 text-slate-700">Le potentiel de consommation demeure structuré autour de la demande urbaine, des flux de déplacements et du développement des périphéries.</p>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Définition du marché</p>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Produit: <span className="font-medium text-slate-900">Supérette de proximité</span></li>
                <li>Territoire: <span className="font-medium text-slate-900">Dakar</span></li>
                <li>Clientèle: <span className="font-medium text-slate-900">Ménages urbains</span></li>
                <li>Hypothèses: <span className="font-medium text-slate-900">Captation locale</span></li>
              </ul>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><ShieldCheck size={16} /> <span className="font-medium">Sources</span></div>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>ANSD — population et structure</li>
                <li>EHCVM — dépenses par tête</li>
                <li>Modèle DataMarket — hypothèses de captation</li>
              </ul>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
