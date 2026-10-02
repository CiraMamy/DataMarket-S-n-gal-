import { ArrowRight } from 'lucide-react';

export function DatasetCard({
  title,
  source,
  period,
  territory,
  status,
  onSelect,
}: {
  title: string;
  source: string;
  period: string;
  territory: string;
  status: string;
  onSelect: () => void;
}) {
  return (
    <article className="surface p-5 shadow-soft transition hover:shadow-lg">
      <div className="mb-4 flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-navy">{title}</h3>
        <span className="chip">{status}</span>
      </div>

      <div className="space-y-2 text-sm text-slate-600">
        <div className="flex justify-between">
          <span>Source</span>
          <span className="font-medium text-slate-900">{source}</span>
        </div>
        <div className="flex justify-between">
          <span>Période</span>
          <span className="font-medium text-slate-900">{period}</span>
        </div>
        <div className="flex justify-between">
          <span>Zone</span>
          <span className="font-medium text-slate-900">{territory}</span>
        </div>
      </div>

      <button onClick={onSelect} className="mt-5 inline-flex items-center gap-2 link-arrow">
        Voir le détail <ArrowRight size={15} />
      </button>
    </article>
  );
}
