import Link from 'next/link';
import { ArrowLeft, Download, FileText, Sparkles } from 'lucide-react';

export default function ReportPreviewPage({ params }: { params: { id: string } }) {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <div className="flex items-center gap-3 text-sm text-textMuted">
        <Link href="/reports" className="inline-flex items-center gap-2 hover:text-navy"><ArrowLeft size={15} /> Retour</Link>
      </div>

      <section className="surface p-6 shadow-soft">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-textMuted">Prévisualisation</p>
            <h1 className="mt-2 text-4xl font-semibold text-navy">Rapport {params.id}</h1>
          </div>
          <button className="inline-flex items-center gap-2 rounded-full bg-mustard px-5 py-3 font-medium text-navy">
            <Download size={16} /> Export PDF
          </button>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><FileText size={16} /> <span className="font-medium">Synthèse</span></div>
              <p className="mt-3 text-slate-700">Le potentiel de marché reste le plus fort sur les zones périurbaines de Dakar, avec des opportunités de modernisation dans le secteur de la distribution alimentaire.</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><Sparkles size={16} /> <span className="font-medium">Hypothèses</span></div>
              <p className="mt-3 text-slate-700">Les hypothèses de captation et de prix restent à valider avec des données terrain, mais elles sont explicitement documentées.</p>
            </div>
          </div>

          <aside className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Table des matières</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              <li>1. Synthèse</li>
              <li>2. Définition du marché</li>
              <li>3. Taille du marché</li>
              <li>4. Analyse territoriale</li>
              <li>5. Sources et méthodologie</li>
            </ul>
          </aside>
        </div>
      </section>
    </main>
  );
}
