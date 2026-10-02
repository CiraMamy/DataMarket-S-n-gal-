export function EvidencePanel({ evidence }: { evidence: { title: string; detail: string }[] }) {
  return (
    <div className="space-y-3">
      {evidence.map((item, idx) => (
        <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="font-medium text-navy">{item.title}</p>
          <p className="mt-2 text-sm text-slate-600">{item.detail}</p>
        </div>
      ))}
    </div>
  );
}
