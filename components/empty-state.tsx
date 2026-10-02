import Link from 'next/link';

export function EmptyState({
  title,
  description,
  actionLabel,
  actionHref,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
}) {
  return (
    <div className="surface p-8 text-center shadow-soft">
      <h3 className="text-2xl font-semibold text-navy">{title}</h3>
      <p className="mt-3 text-slate-600">{description}</p>
      {actionLabel && actionHref ? (
        <Link href={actionHref} className="mt-6 inline-flex rounded-full bg-navy px-5 py-3 font-medium text-white">
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
}
