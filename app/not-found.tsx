export default function SettingsPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Paramètres</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Préférences et sécurité</h1>
      </header>

      <section className="surface p-6 shadow-soft">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Profil</p>
            <p className="mt-2 text-slate-600">Nom, organisation, langue et préférences d’affichage.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Gestion des sessions</p>
            <p className="mt-2 text-slate-600">Vérification des appareils connectés et des permissions.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Rôles</p>
            <p className="mt-2 text-slate-600">OWNER, ADMIN, MEMBER, VIEWER.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-navy">Sécurité</p>
            <p className="mt-2 text-slate-600">Révisions d’accès, MFA et gestion des sessions.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
