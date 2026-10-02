export function LoadingState() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="surface flex items-center gap-3 px-5 py-3 shadow-soft">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-navy" />
        <p className="font-medium text-navy">Chargement...</p>
      </div>
    </div>
  );
}
