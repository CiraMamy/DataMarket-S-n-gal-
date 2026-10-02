import { Search } from 'lucide-react';

export function SearchBar({ placeholder = 'Rechercher...' }: { placeholder?: string }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-slate-700 shadow-sm">
      <Search size={16} />
      <input className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder={placeholder} />
    </div>
  );
}
