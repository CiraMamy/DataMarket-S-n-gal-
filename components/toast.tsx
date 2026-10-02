"use client";
import { useState } from 'react';
import { AlertCircle, Check, AlertTriangle } from 'lucide-react';

export function Toast({
  type = 'info',
  title,
  message,
}: {
  type?: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
}) {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  const colors = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const icons = {
    success: <Check size={16} />,
    error: <AlertCircle size={16} />,
    warning: <AlertTriangle size={16} />,
    info: <AlertCircle size={16} />,
  };

  return (
    <div className={`fixed bottom-4 right-4 flex items-center gap-3 rounded-xl border px-4 py-3 ${colors[type]}`}>
      {icons[type]}
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm">{message}</p>
      </div>
      <button onClick={() => setVisible(false)} className="ml-2 font-bold">
        ×
      </button>
    </div>
  );
}
