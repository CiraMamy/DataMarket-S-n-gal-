export function EstimateBreakdown({
  items,
}: {
  items: { label: string; value: string; type: 'observed' | 'calculated' | 'estimated' | 'hypothesis' }[];
}) {
  const typeColors = {
    observed: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    calculated: 'bg-blue-50 border-blue-200 text-blue-700',
    estimated: 'bg-amber-50 border-amber-200 text-amber-700',
    hypothesis: 'bg-purple-50 border-purple-200 text-purple-700',
  };

  const typeLabels = {
    observed: 'OBS',
    calculated: 'CALC',
    estimated: 'EST',
    hypothesis: 'HYP',
  };

  return (
    <div className="space-y-3">
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4">
          <p className="font-medium text-slate-700">{item.label}</p>
          <div className="flex items-center gap-3">
            <p className="text-lg font-semibold text-navy">{item.value}</p>
            <span className={`chip ${typeColors[item.type]}`}>{typeLabels[item.type]}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
