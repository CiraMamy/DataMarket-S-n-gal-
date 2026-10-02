import { Sidebar } from '@/components/sidebar';
import { MobileNavigation } from '@/components/mobile-navigation';
import Link from 'next/link';
import { Bell, ChevronDown, LogIn, Search, UserCircle2 } from 'lucide-react';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-20 xl:pb-0">
      {/* Topbar */}
      <div className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="container-shell flex h-20 items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy text-lg font-semibold text-white">D</div>
              <div className="hidden sm:block">
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
            <button className="rounded-full border border-slate-200 bg-white p-2.5 text-slate-700 transition hover:bg-slate-100">
              <Bell size={17} />
            </button>
            <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 md:flex">
              <UserCircle2 size={16} className="text-navy" />
              <span className="text-sm font-medium text-slate-700">Awa M.</span>
              <ChevronDown size={14} className="text-slate-500" />
            </div>
            <Link href="/auth/login" className="inline-flex items-center gap-2 rounded-full bg-navy px-4 py-2.5 text-sm font-medium text-white transition hover:bg-navySecondary">
              <LogIn size={16} />
              <span className="hidden sm:inline">Connexion</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="container-shell py-6">
        <div className="grid gap-6 xl:grid-cols-[240px_1fr]">
          <Sidebar />
          <div className="min-w-0">{children}</div>
        </div>
      </div>

      {/* Mobile navigation */}
      <MobileNavigation />

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white mt-12">
        <div className="container-shell flex flex-col gap-3 py-6 text-sm text-slate-600 md:flex-row md:items-center md:justify-between">
          <p>© 2026 DataMarket. Données aux décisions. Plateforme d’intelligence économique du Sénégal.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-navy">Sources et méthodologie</a>
            <span className="chip">Mode démonstration</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
