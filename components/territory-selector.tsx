import Link from 'next/link';

export function TerritorySelector({
  territories,
  selected,
  onChange,
}: {
  territories: { id: string; name: string }[];
  selected: string[];
  onChange: (id: string, checked: boolean) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
      {territories.map((t) => (
        <label key={t.id} className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 cursor-pointer hover:bg-slate-50">
          <input
            type="checkbox"
            checked={selected.includes(t.id)}
            onChange={(e) => onChange(t.id, e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-navy"
          />
          <span className="text-sm font-medium text-slate-700">{t.name}</span>
        </label>
      ))}
    </div>
  );
}
