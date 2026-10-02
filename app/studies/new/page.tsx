import Link from 'next/link';
import { ArrowRight, Check, Info } from 'lucide-react';

const steps = [
  { label: 'Question business', status: 'completed' },
  { label: 'Définition du marché', status: 'completed' },
  { label: 'Territoire', status: 'current' },
  { label: 'Paramètres', status: 'upcoming' },
  { label: 'Données disponibles', status: 'upcoming' },
  { label: 'Lancer l’analyse', status: 'upcoming' },
];

export default function StudyWizardPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Étude de marché</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Créer une étude</h1>
      </header>

      <section className="surface p-6 shadow-soft">
        <div className="mb-6 grid gap-3 md:grid-cols-2 xl:grid-cols-6">
          {steps.map((step) => (
            <div key={step.label} className={`rounded-xl border p-3 ${step.status === 'completed' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : step.status === 'current' ? 'border-navy bg-slate-100 text-navy' : 'border-slate-200 bg-white text-slate-500'}`}>
              <div className="mb-2 flex items-center gap-2">
                {step.status === 'completed' ? <Check size={14} /> : <span className="inline-flex h-4 w-4 items-center justify-center rounded-full border text-[10px]">{step.status === 'current' ? '•' : steps.indexOf(step) + 1}</span>}
                <span className="text-xs font-medium uppercase tracking-[0.12em]">Étape {steps.indexOf(step) + 1}</span>
              </div>
              <p className="text-sm font-medium">{step.label}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Pays</label>
              <select className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy">
                <option>Sénégal</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Région</label>
              <select className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy">
                <option>Dakar</option>
                <option>Thiès</option>
                <option>Saint-Louis</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Question business</label>
              <textarea className="min-h-[120px] w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" defaultValue="Je souhaite lancer un point de vente alimentaire à Dakar avec un potentiel de 15 millions FCFA." />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Produit / service</label>
                <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" defaultValue="Supérette de proximité" />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Secteur</label>
                <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" defaultValue="Commerce de proximité" />
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center gap-2 text-navy"><Info size={16} /> <span className="font-medium">Résumé</span></div>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Région: Dakar</li>
                <li>Type: Commerce de proximité</li>
                <li>Budget: 15 M FCFA</li>
                <li>Zone de chalandise estimée: 35%</li>
              </ul>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-700">Données disponibles</p>
              <div className="mt-4 space-y-2 text-sm text-slate-600">
                <div className="flex items-center justify-between"><span>Population cible</span><span className="font-medium text-slate-900">Disponible</span></div>
                <div className="flex items-center justify-between"><span>Dépenses par tête</span><span className="font-medium text-slate-900">Disponible</span></div>
                <div className="flex items-center justify-between"><span>Couverture territoriale</span><span className="font-medium text-slate-900">Partielle</span></div>
              </div>
            </div>

            <Link href="/studies/market-study-001" className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-navy px-5 py-3 font-medium text-white transition hover:bg-navySecondary">
              Lancer l’analyse <ArrowRight size={16} />
            </Link>
          </aside>
        </div>
      </section>
    </main>
  );
}
