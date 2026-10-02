import Link from 'next/link';

export default function ForgotPasswordPage() {
  return (
    <main className="container-shell flex min-h-[70vh] items-center justify-center py-12">
      <div className="surface w-full max-w-md p-8 shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Réinitialisation</p>
        <h1 className="mt-2 text-3xl font-semibold text-navy">Mot de passe oublié</h1>
        <p className="mt-3 text-sm text-slate-600">Entrez votre email pour recevoir un lien de réinitialisation.</p>
        <div className="mt-6">
          <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
          <input className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-navy" placeholder="prenom@entreprise.sn" />
        </div>
        <button className="mt-5 w-full rounded-full bg-navy px-5 py-3 font-medium text-white">Envoyer le lien</button>
        <div className="mt-4 text-sm text-slate-600">
          <Link href="/auth/login" className="text-navy">Retour à la connexion</Link>
        </div>
      </div>
    </main>
  );
}
