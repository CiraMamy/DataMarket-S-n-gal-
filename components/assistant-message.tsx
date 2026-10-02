import Link from 'next/link';
import { MessageSquareText } from 'lucide-react';

export function AssistantMessage({
  type,
  content,
  badge,
}: {
  type: 'question' | 'response' | 'insight';
  content: string;
  badge?: string;
}) {
  const bgColors = {
    question: 'bg-slate-100 border-slate-200',
    response: 'bg-blue-50 border-blue-200',
    insight: 'bg-amber-50 border-amber-200',
  };

  return (
    <div className={`rounded-xl border ${bgColors[type]} p-4`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <MessageSquareText size={16} className="text-navy" />
            <p className="font-medium text-navy">Assistant DataMarket</p>
          </div>
          <p className="mt-2 text-slate-700">{content}</p>
        </div>
        {badge && <span className="chip">{badge}</span>}
      </div>
    </div>
  );
}
