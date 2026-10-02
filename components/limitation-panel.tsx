export function LimitationPanel({ limitations }: { limitations: string[] }) {
  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
      <p className="mb-3 font-medium text-amber-900">Limites et restrictions</p>
      <ul className="space-y-2 text-sm text-amber-800">
        {limitations.map((limit, idx) => (
          <li key={idx} className="flex gap-2">
            <span className="text-amber-600">•</span>
            {limit}
          </li>
        ))}
      </ul>
    </div>
  );
}
