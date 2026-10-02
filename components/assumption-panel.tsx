export function AssumptionPanel({ assumptions }: { assumptions: { key: string; value: string }[] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="mb-3 font-medium text-navy">Hypothèses de modélisation</p>
      <dl className="space-y-2 text-sm text-slate-700">
        {assumptions.map((item) => (
          <div key={item.key} className="flex justify-between">
            <dt>{item.key}</dt>
            <dd className="font-medium text-slate-900">{item.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
