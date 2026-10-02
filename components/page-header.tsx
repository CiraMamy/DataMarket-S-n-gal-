import Link from 'next/link';

export function PageHeader({
  eyebrow,
  title,
  action,
}: {
  eyebrow: string;
  title: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">{eyebrow}</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">{title}</h1>
      </div>
      {action}
    </header>
  );
}
