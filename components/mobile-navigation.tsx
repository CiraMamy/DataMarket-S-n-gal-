import Link from 'next/link';
import { usePathname } from 'next/navigation';
import clsx from 'clsx';
import { BarChart3, Building2, Database, FileText, LayoutDashboard, MapPinned, MessageSquareText } from 'lucide-react';

const navigation = [
  { href: '/dashboard', label: 'Vue d’ensemble', icon: LayoutDashboard },
  { href: '/explore', label: 'Explorer', icon: Database },
  { href: '/studies', label: 'Études de marché', icon: Building2 },
  { href: '/territories', label: 'Territoires', icon: MapPinned },
  { href: '/analyses', label: 'Analyses', icon: BarChart3 },
  { href: '/reports', label: 'Rapports', icon: FileText },
  { href: '/assistant', label: 'Assistant IA', icon: MessageSquareText },
];

export function MobileNavigation() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-slate-200 bg-white xl:hidden">
      <div className="grid grid-cols-4 gap-1 px-2 py-2">
        {navigation.slice(0, 4).map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={clsx('flex flex-col items-center gap-1 rounded-xl px-2 py-2 text-[11px] font-medium', active ? 'bg-navy text-white' : 'text-slate-600')}>
              <Icon size={17} />
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
