import { PageHeader } from '@/components/page-header';
import { AssistantMessage } from '@/components/assistant-message';
import Link from 'next/link';

export default function AssistantPageExpanded() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <PageHeader eyebrow="Assistant DataMarket" title="Demandez une analyse, explorez les résultats" />

      <section className="surface p-6 shadow-soft">
        <div className="mb-6 space-y-4">
          <AssistantMessage
            type="question"
            content="Je veux ouvrir une superette à Mbour. Quel est le potentiel?"
            badge="Votre question"
          />
          <AssistantMessage
            type="response"
            content="Le potentiel pour une superette à Mbour (Thiès) reste bon, porté par une demande urbaine croissante et une population de ~2,1 M dans la région. Le TAM estimé est de 120 M FCFA, le SAM de 50 M FCFA, et le SOM de 15 M FCFA sur 3 ans."
            badge="Réponse"
          />
          <AssistantMessage
            type="insight"
            content="Les principales limites restent la captation réelle du commerce organisé et la concurrence locale, que seule une étude de terrain peut valider."
            badge="Avertissement"
          />
        </div>

        <div className="mt-6 border-t border-slate-200 pt-4">
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.12em] text-textMuted">Voulez-vous&nbsp;?</p>
          <div className="space-y-2">
            <Link href="/studies/new" className="block rounded-xl border border-slate-200 bg-slate-50 p-3 font-medium text-navy transition hover:bg-slate-100">
              Créer une étude détaillée
            </Link>
            <Link href="/explore" className="block rounded-xl border border-slate-200 bg-slate-50 p-3 font-medium text-navy transition hover:bg-slate-100">
              Explorer plus de données
            </Link>
            <Link href="/territories" className="block rounded-xl border border-slate-200 bg-slate-50 p-3 font-medium text-navy transition hover:bg-slate-100">
              Comparer les territoires
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
