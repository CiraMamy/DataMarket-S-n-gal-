import Link from 'next/link';
import { ArrowRight, BriefcaseBusiness, ChartColumnBig, FolderKanban, History, Search, Sparkles } from 'lucide-react';
import { dashboardStats, recentStudies, dataCards, recentActivity } from '@/lib/mock-data';

export default function DashboardPage() {
  return (
    <main className="space-y-8 pb-10 pt-8">
      <section className="container-shell">
        <div className="surface flex flex-col gap-6 bg-navy p-6 text-white shadow-soft lg:flex-row lg:items-center lg:justify-between lg:p-8">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-300">Tableau de bord</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Bienvenue dans votre espace DataMarket</h1>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/explore" className="rounded-full bg-mustard px-4 py-2.5 font-medium text-navy">Rechercher</Link>
            <Link href="/studies/new" className="rounded-full border border-white/15 bg-white/5 px-4 py-2.5 font-medium text-white">Créer une étude</Link>
          </div>
        </div>
      </section>

      <section className="container-shell grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dashboardStats.map((stat) => (
          <div key={stat.label} className="surface p-5 shadow-soft">
            <p className="text-sm text-textMuted">{stat.label}</p>
            <div className="mt-4 flex items-end justify-between gap-3">
              <p className="text-3xl font-semibold text-navy">{stat.value}</p>
              <span className="rounded-full bg-mustard/10 px-2 py-1 text-xs font-medium text-mustardDark">{stat.delta}</span>
            </div>
          </div>
        ))}
      </section>

      <section className="container-shell grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-slate-100 p-2 text-navy"><Search size={18} /></div>
              <h2 className="text-2xl font-semibold text-navy">Reprendre une étude</h2>
            </div>
            <Link href="/studies" className="link-arrow">Voir tout <ArrowRight size={15} /></Link>
          </div>
          <div className="space-y-3">
            {recentStudies.map((study) => (
              <Link key={study.id} href={`/studies/${study.id}`} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4 transition hover:border-slate-300 hover:bg-slate-100">
                <div>
                  <p className="font-medium text-navy">{study.title}</p>
                  <p className="mt-1 text-sm text-textMuted">{study.region} • {study.updatedAt}</p>
                </div>
                <span className="chip">{study.status}</span>
              </Link>
            ))}
          </div>
        </div>

        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-xl bg-slate-100 p-2 text-navy"><FolderKanban size={18} /></div>
            <h2 className="text-2xl font-semibold text-navy">Projets</h2>
          </div>
          <div className="space-y-3">
            {dataCards.slice(0, 3).map((item) => (
              <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-navy">{item.name}</p>
                  <span className="chip">{item.status}</span>
                </div>
                <p className="mt-2 text-sm text-textMuted">{item.source}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="container-shell grid gap-6 xl:grid-cols-[1fr_1fr]">
        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-xl bg-slate-100 p-2 text-navy"><History size={18} /></div>
            <h2 className="text-2xl font-semibold text-navy">Dernières analyses consultées</h2>
          </div>
          <div className="space-y-3">
            {recentActivity.map((item) => (
              <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="font-medium text-navy">{item.title}</p>
                <p className="mt-1 text-sm text-textMuted">{item.date}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="surface p-6 shadow-soft">
          <div className="mb-5 flex items-center gap-3">
            <div className="rounded-xl bg-slate-100 p-2 text-navy"><ChartColumnBig size={18} /></div>
            <h2 className="text-2xl font-semibold text-navy">Données récemment ajoutées</h2>
          </div>
          <div className="space-y-3">
            {dataCards.slice(0, 3).map((item) => (
              <div key={item.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-navy">{item.name}</p>
                  <span className="chip">{item.frequency}</span>
                </div>
                <p className="mt-2 text-sm text-textMuted">{item.source}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
