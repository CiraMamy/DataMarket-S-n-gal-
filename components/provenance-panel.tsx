export function ProvenancePanel({
  label,
  value,
  source,
  methodology,
}: {
  label: string;
  value: string;
  source: string;
  methodology: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-sm text-textMuted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-navy">{value}</p>
      <div className="mt-4 space-y-2 text-xs text-slate-600">
        <div className="flex justify-between">
          <span>Source</span>
          <span className="font-medium text-slate-900">{source}</span>
        </div>
        <div className="flex justify-between">
          <span>Méthode</span>
          <span className="font-medium text-slate-900">{methodology}</span>
        </div>
      </div>
    </div>
  );
}
