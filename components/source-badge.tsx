export function SourceBadge({ source, period }: { source: string; period: string }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700">
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
      {source} • {period}
    </div>
  );
}
