import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="container-shell flex min-h-[60vh] items-center justify-center py-12">
      <div className="surface max-w-lg p-8 text-center shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Erreur 404</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Page introuvable</h1>
        <p className="mt-4 text-slate-600">La page demandée n’existe pas ou n’est plus disponible.</p>
        <Link href="/" className="mt-6 inline-flex rounded-full bg-navy px-5 py-3 font-medium text-white">Retour à l’accueil</Link>
      </div>
    </main>
  );
}
