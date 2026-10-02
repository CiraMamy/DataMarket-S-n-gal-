import Link from 'next/link';

export default function RegisterPage() {
  return (
    <main className="container-shell flex min-h-[70vh] items-center justify-center py-12">
      <div className="surface w-full max-w-md p-8 shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Inscription</p>
        <h1 className="mt-2 text-3xl font-semibold text-navy">Créer votre compte</h1>
        <div className="mt-6 space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Nom complet</label>
            <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="Prénom Nom" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Organisation</label>
            <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="Entreprise / organisation" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
            <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="prenom@entreprise.sn" />
          </div>
          <button className="w-full rounded-full bg-mustard px-5 py-3 font-medium text-navy">Créer mon compte</button>
        </div>
        <div className="mt-4 text-sm text-slate-600">
          Déjà inscrit ? <Link href="/auth/login" className="text-navy">Se connecter</Link>
        </div>
      </div>
    </main>
  );
}
