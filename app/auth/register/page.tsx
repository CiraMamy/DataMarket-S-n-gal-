import Link from 'next/link';

export default function LoginPage() {
  return (
    <main className="container-shell flex min-h-[70vh] items-center justify-center py-12">
      <div className="surface w-full max-w-md p-8 shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Connexion</p>
        <h1 className="mt-2 text-3xl font-semibold text-navy">Accéder à DataMarket</h1>
        <div className="mt-6 space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
            <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="prenom@entreprise.sn" />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Mot de passe</label>
            <input type="password" className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="••••••••" />
          </div>
          <button className="w-full rounded-full bg-navy px-5 py-3 font-medium text-white">Se connecter</button>
        </div>
        <div className="mt-4 flex items-center justify-between text-sm text-slate-600">
          <Link href="/auth/register" className="text-navy">Créer un compte</Link>
          <Link href="/auth/forgot-password" className="text-navy">Mot de passe oublié</Link>
        </div>
      </div>
    </main>
  );
}
