import Link from 'next/link';

export default function ComparePage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Comparateur</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Comparer les territoires</h1>
      </header>

      <section className="surface p-6 shadow-soft">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h2 className="font-medium text-navy">Territoires sélectionnés</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                {['Dakar', 'Thiès', 'Saint-Louis'].map((territory) => (
                  <span key={territory} className="chip">{territory}</span>
                ))}
              </div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h2 className="font-medium text-navy">Indicateurs</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Population</li>
                <li>Dépense moyenne par tête</li>
                <li>Potentiel de marché</li>
                <li>Couverture territoriale</li>
              </ul>
            </div>
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 font-medium text-slate-700">Indicateur</th>
                  <th className="px-4 py-3 font-medium text-slate-700">Dakar</th>
                  <th className="px-4 py-3 font-medium text-slate-700">Thiès</th>
                  <th className="px-4 py-3 font-medium text-slate-700">Saint-Louis</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-slate-200">
                  <td className="px-4 py-3 text-slate-700">Population</td>
                  <td className="px-4 py-3 text-slate-700">3,9 M</td>
                  <td className="px-4 py-3 text-slate-700">2,1 M</td>
                  <td className="px-4 py-3 text-slate-700">1,2 M</td>
                </tr>
                <tr className="border-t border-slate-200">
                  <td className="px-4 py-3 text-slate-700">Potentiel</td>
                  <td className="px-4 py-3 text-slate-700">Très fort</td>
                  <td className="px-4 py-3 text-slate-700">Fort</td>
                  <td className="px-4 py-3 text-slate-700">Moyen</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="flex justify-end">
        <Link href="/territories" className="rounded-full bg-navy px-5 py-3 font-medium text-white">Retour aux territoires</Link>
      </div>
    </main>
  );
}
