export function ErrorState({ title, message }: { title: string; message: string }) {
  return (
    <div className="surface flex flex-col items-center justify-center p-8 text-center shadow-soft">
      <p className="font-semibold text-red-700">{title}</p>
      <p className="mt-2 text-slate-600">{message}</p>
    </div>
  );
}
