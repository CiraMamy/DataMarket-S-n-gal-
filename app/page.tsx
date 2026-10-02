import Link from 'next/link';
import { ArrowRight, BarChart3, Building2, Database, MapPinned, MessageSquareText, Search, ShieldCheck, Sparkles } from 'lucide-react';

const pillars = [
  {
    title: 'Observatoire économique',
    text: 'Centralisez les indicateurs fiables, les sources et les méthodologies pour transformer l’information en décision.',
    icon: BarChart3,
  },
  {
    title: 'Explorer les marchés',
    text: 'Comparez territoires, secteurs et données dans une expérience conçue pour les décideurs et leurs équipes.',
    icon: Search,
  },
  {
    title: 'Études structurées',
    text: 'Passez d’une question métier à un plan d’action documenté, avec hypothèses, limites et références explicites.',
    icon: Building2,
  },
];

const workflow = [
  {
    title: '1. Formuler la question',
    text: 'Définissez le marché, la zone de chalandise et les hypothèses.',
  },
  {
    title: '2. Mobiliser les données',
    text: 'Rassemblez les jeux de données, les sources, les territoires et les indicateurs.',
  },
  {
    title: '3. Produire une analyse',
    text: 'Calculez, comparez et documentez les résultats avec la bonne méthodologie.',
  },
  {
    title: '4. Décider',
    text: 'Exploitez les résultats dans des rapports, analyses et recommandations.',
  },
];

const useCases = [
  'Évaluer une opportunité de commerce de proximité',
  'Analyser la demande dans une région donnée',
  'Comparer des territoires pour un investissement',
  'Préparer un rapport de marché pour un partenariat',
  'Suivre des données économiques par thématique',
];

export default function HomePage() {
  return (
    <main className="space-y-16 pb-20 pt-8">
      <section className="container-shell">
        <div className="grid gap-10 rounded-[28px] border border-slate-200 bg-navy px-6 py-10 text-white shadow-soft lg:grid-cols-[1.2fr_0.8fr] lg:px-10 lg:py-12">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-200">
              <Sparkles size={14} /> DataMarket
            </div>
            <div className="space-y-4">
              <h1 className="max-w-xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                Comprendre les marchés sénégalais par la donnée.
              </h1>
              <p className="max-w-xl text-lg text-slate-200">
                Explorez les données économiques, comparez les territoires et transformez vos questions en analyses documentées.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/explore" className="inline-flex items-center gap-2 rounded-full bg-mustard px-5 py-3 font-medium text-navy transition hover:bg-[#E6BB4A]">
                Explorer les données <ArrowRight size={16} />
              </Link>
              <Link href="/studies/new" className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-5 py-3 font-medium text-white transition hover:bg-white/10">
                Créer une étude
              </Link>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-300">Synthèse</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">Observatoire national</h2>
              </div>
              <div className="rounded-full bg-mustard/20 px-2 py-1 text-xs text-mustard">Mode démonstration</div>
            </div>
            <div className="space-y-4">
              <div className="rounded-xl bg-white/5 p-4">
                <p className="text-sm text-slate-300">Population nationale</p>
                <p className="mt-2 text-3xl font-semibold text-white">18,1 M</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl bg-white/5 p-4">
                  <p className="text-sm text-slate-300">Dépense moyenne</p>
                  <p className="mt-2 text-xl font-semibold text-white">542 706 FCFA</p>
                </div>
                <div className="rounded-xl bg-white/5 p-4">
                  <p className="text-sm text-slate-300">Territoires</p>
                  <p className="mt-2 text-xl font-semibold text-white">14 régions</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container-shell">
        <div className="mb-8 flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Pourquoi DataMarket</p>
            <h2 className="section-title mt-2">Une plateforme pensée pour les décisions économiques.</h2>
          </div>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {pillars.map(({ title, text, icon: Icon }) => (
            <article key={title} className="surface p-6 shadow-soft">
              <div className="mb-4 inline-flex rounded-xl bg-[#F2E8C9] p-3 text-navy">
                <Icon size={22} />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-navy">{title}</h3>
              <p className="text-slate-600">{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="container-shell">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="surface p-6 shadow-soft">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-xl bg-slate-100 p-2 text-navy"><Database size={18} /></div>
              <h3 className="text-2xl font-semibold text-navy">Traçabilité des données</h3>
            </div>
            <ul className="space-y-4 text-slate-700">
              <li className="flex items-start gap-3"><ShieldCheck className="mt-0.5 text-mustard" size={18} /> Chaque résultat reste rattaché à une source, une méthode et une limite.</li>
              <li className="flex items-start gap-3"><ShieldCheck className="mt-0.5 text-mustard" size={18} /> Les hypothèses sont visibles, lisibles et modifiables.</li>
              <li className="flex items-start gap-3"><ShieldCheck className="mt-0.5 text-mustard" size={18} /> Les écarts de couverture et de période sont explicités.</li>
            </ul>
          </div>

          <div className="space-y-4">
            <div className="mb-2 flex items-center gap-3">
              <div className="rounded-xl bg-slate-100 p-2 text-navy"><MapPinned size={18} /></div>
              <h3 className="text-2xl font-semibold text-navy">Sources & méthodologie</h3>
            </div>
            <div className="space-y-3">
              <div className="surface p-4">
                <p className="font-medium text-navy">Données de référence</p>
                <p className="mt-1 text-slate-600">Population, dépenses et production sectorielle issues des référentiels publics du Sénégal.</p>
              </div>
              <div className="surface p-4">
                <p className="font-medium text-navy">Méthodologie explicite</p>
                <p className="mt-1 text-slate-600">Le calcul de TAM, SAM et SOM est toujours documenté et traceable.</p>
              </div>
              <div className="surface p-4">
                <p className="font-medium text-navy">Limites clarifiées</p>
                <p className="mt-1 text-slate-600">Les hypothèses, données absentes et incertitudes sont affichées sans masque.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container-shell">
        <div className="mb-8">
          <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Fonctionnement</p>
          <h2 className="section-title mt-2">De la question métier à la décision.</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {workflow.map((step) => (
            <div key={step.title} className="surface p-5 shadow-soft">
              <p className="mb-2 text-sm font-medium uppercase tracking-[0.12em] text-mustardDark">{step.title.split('.')[0]}</p>
              <h3 className="text-lg font-semibold text-navy">{step.title.replace(/^\d+\.\s*/, '')}</h3>
              <p className="mt-3 text-slate-600">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container-shell">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Cas d’usage</p>
            <h2 className="section-title mt-2">Des usages concrets pour les acteurs économiques.</h2>
          </div>
        </div>
        <div className="mt-8 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {useCases.map((item) => (
            <div key={item} className="surface flex items-center gap-3 p-4 shadow-soft">
              <div className="h-2.5 w-2.5 rounded-full bg-mustard" />
              <span className="text-slate-700">{item}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="container-shell">
        <div className="surface bg-[#F1F3F6] p-8 text-center shadow-soft">
          <div className="mx-auto max-w-2xl">
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Prêt à commencer</p>
            <h2 className="mt-2 text-3xl font-semibold text-navy">Créez votre première étude DataMarket.</h2>
            <p className="mt-4 text-slate-600">
              Transformez une question de marché en une analyse structurée, comparable et exploitable.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <Link href="/studies/new" className="rounded-full bg-navy px-5 py-3 font-medium text-white transition hover:bg-navySecondary">Créer une étude</Link>
              <Link href="/dashboard" className="rounded-full border border-navy/20 bg-white px-5 py-3 font-medium text-navy transition hover:border-navy/40">Accéder au tableau de bord</Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
