import { BriefcaseBusiness, Building2, Mail, ShieldCheck, UserCircle2 } from 'lucide-react';

export default function ProfilePage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Profil</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Profil utilisateur</h1>
      </header>

      <section className="surface grid gap-6 p-6 shadow-soft lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-2xl bg-slate-50 p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-navy text-xl font-semibold text-white">AM</div>
            <div>
              <p className="text-2xl font-semibold text-navy">Awa M.</p>
              <p className="text-sm text-textMuted">OWNER • Organisation DataMarket</p>
            </div>
          </div>

          <div className="mt-6 space-y-3 text-sm text-slate-700">
            <div className="flex items-center gap-3"><Mail size={16} /> awa@datamarket.sn</div>
            <div className="flex items-center gap-3"><Building2 size={16} /> DataMarket Sénégal</div>
            <div className="flex items-center gap-3"><ShieldCheck size={16} /> Rôle: OWNER</div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Organisation</p>
            <p className="mt-2 text-slate-600">Membres, rôles et permissions d’accès à l’instance.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Préférences</p>
            <p className="mt-2 text-slate-600">Thème: claire / langue: français / notifications: activées.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
