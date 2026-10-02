"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bell, ChevronDown, LayoutDashboard, LogIn, MapPinned, MessageSquareText, Search, Settings, UserCircle2, BarChart3, FileText, Database, Building2 } from 'lucide-react';
import clsx from 'clsx';

const navigation = [
  { href: '/dashboard', label: 'Vue d’ensemble', icon: LayoutDashboard },
  { href: '/explore', label: 'Explorer', icon: Database },
  { href: '/studies', label: 'Études de marché', icon: Building2 },
  { href: '/territories', label: 'Territoires', icon: MapPinned },
  { href: '/analyses', label: 'Analyses', icon: BarChart3 },
  { href: '/reports', label: 'Rapports', icon: FileText },
  { href: '/assistant', label: 'Assistant IA', icon: MessageSquareText },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen">
      <div className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="container-shell flex h-20 items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy text-lg font-semibold text-white">D</div>
              <div>
                <p className="text-lg font-semibold text-navy">DataMarket</p>
                <p className="text-xs uppercase tracking-[0.16em] text-textMuted">Données aux décisions</p>
              </div>
            </Link>
          </div>

          <div className="hidden items-center gap-3 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 md:flex">
            <Search size={15} />
            <input className="w-72 bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder="Rechercher..." />
          </div>

          <div className="flex items-center gap-3">
            <button className="rounded-full border border-slate-200 bg-white p-2.5 text-slate-700">
              <Bell size={17} />
            </button>
            <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 md:flex">
              <UserCircle2 size={16} className="text-navy" />
              <span className="text-sm font-medium text-slate-700">Awa M.</span>
              <ChevronDown size={14} className="text-slate-500" />
            </div>
            <Link href="/auth/login" className="inline-flex items-center gap-2 rounded-full bg-navy px-4 py-2.5 text-sm font-medium text-white">
              <LogIn size={16} />
              <span className="hidden sm:inline">Connexion</span>
            </Link>
          </div>
        </div>
      </div>

      <div className="container-shell py-6">
        <div className="grid gap-6 xl:grid-cols-[240px_1fr]">
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

          <div className="min-w-0">{children}</div>
        </div>
      </div>

      <div className="border-t border-slate-200 bg-white">
        <div className="container-shell flex flex-col gap-3 py-6 text-sm text-slate-600 md:flex-row md:items-center md:justify-between">
          <p>© 2026 DataMarket. Données aux décisions.</p>
          <div className="flex items-center gap-4">
            <span>Sources et méthodologie</span>
            <span>Mode démonstration</span>
          </div>
        </div>
      </div>
    </div>
  );
}
