import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '@/components/app-shell';

export const metadata: Metadata = {
  title: 'DataMarket | Données aux décisions',
  description: 'Plateforme d’intelligence économique pour le Sénégal.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="min-h-screen bg-[#F8F8F6] text-slate-800">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
