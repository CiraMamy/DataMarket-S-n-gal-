"use client";
import { useState } from 'react';

export function ConfirmationDialog({
  open,
  title,
  description,
  confirmLabel = 'Confirmer',
  cancelLabel = 'Annuler',
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="surface w-full max-w-sm p-6 shadow-soft">
        <h2 className="text-xl font-semibold text-navy">{title}</h2>
        <p className="mt-3 text-slate-600">{description}</p>
        <div className="mt-6 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded-full border border-slate-200 bg-white px-4 py-2.5 font-medium text-slate-700 transition hover:bg-slate-100">
            {cancelLabel}
          </button>
          <button onClick={onConfirm} className="flex-1 rounded-full bg-navy px-4 py-2.5 font-medium text-white transition hover:bg-navySecondary">
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
