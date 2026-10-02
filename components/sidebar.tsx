import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import { BarChart3, Building2, Database, FileText, LayoutDashboard, MapPinned, MessageSquareText, Settings, UserCircle2 } from 'lucide-react';

const navigation = [
  { href: '/dashboard', label: 'Vue d’ensemble', icon: LayoutDashboard },
  { href: '/explore', label: 'Explorer', icon: Database },
  { href: '/studies', label: 'Études de marché', icon: Building2 },
  { href: '/territories', label: 'Territoires', icon: MapPinned },
  { href: '/analyses', label: 'Analyses', icon: BarChart3 },
  { href: '/reports', label: 'Rapports', icon: FileText },
  { href: '/assistant', label: 'Assistant IA', icon: MessageSquareText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="surface hidden h-fit p-4 shadow-soft xl:block">
      <div className="space-y-1">
        {navigation.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={clsx('flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium transition', active ? 'bg-navy text-white' : 'text-slate-700 hover:bg-slate-100')}>
              <Icon size={17} />
              {label}
            </Link>
          );
        })}
      </div>

      <div className="mt-6 border-t border-slate-200 pt-4">
        <Link href="/profile" className={clsx('flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium transition', pathname === '/profile' ? 'bg-slate-100 text-navy' : 'text-slate-700 hover:bg-slate-100')}>
          <UserCircle2 size={17} /> Profil
        </Link>
        <Link href="/settings" className={clsx('flex items-center gap-3 rounded-xl px-3 py-2.5 font-medium transition', pathname === '/settings' ? 'bg-slate-100 text-navy' : 'text-slate-700 hover:bg-slate-100')}>
          <Settings size={17} /> Paramètres
        </Link>
      </div>
    </aside>
  );
}
