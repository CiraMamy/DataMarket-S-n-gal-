"use client";

export default function Error({ reset }: { reset: () => void }) {
  return (
    <main className="container-shell flex min-h-[60vh] items-center justify-center py-12">
      <div className="surface max-w-lg p-8 text-center shadow-soft">
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Erreur</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Une erreur est survenue</h1>
        <p className="mt-4 text-slate-600">Le système a rencontré un problème pendant le rendu.</p>
        <button onClick={() => reset()} className="mt-6 rounded-full bg-navy px-5 py-3 font-medium text-white">Réessayer</button>
      </div>
    </main>
  );
}
