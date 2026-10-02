import { Bot, MessageSquareText, Search, Sparkles } from 'lucide-react';

const messages = [
  { from: 'assistant', title: 'Synthèse', text: 'La demande urbaine reste structurée autour de l’alimentation de proximité, avec un potentiel attractif sur les zones de forte densité.', badge: 'Réponse de démonstration' },
  { from: 'assistant', title: 'Sources', text: 'ANSD, EHCVM, modèle DataMarket — données de démonstration, non officielles.', badge: 'Traçabilité' },
  { from: 'assistant', title: 'Limites', text: 'Les hypothèses de capture et de prix restent à valider avec les données terrain.', badge: 'Attention' },
];

export default function AssistantPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <header>
        <p className="text-sm font-medium uppercase tracking-[0.16em] text-textMuted">Assistant DataMarket</p>
        <h1 className="mt-2 text-4xl font-semibold text-navy">Expliquez un résultat, demandez une analyse.</h1>
      </header>

      <section className="surface p-6 shadow-soft">
        <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3 text-navy">
            <Bot size={18} />
            <h2 className="text-2xl font-semibold">Conversation</h2>
          </div>
          <div className="chip">Mode démonstration</div>
        </div>

        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div key={index} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="font-medium text-navy">{msg.title}</p>
                <span className="chip">{msg.badge}</span>
              </div>
              <p className="text-slate-700">{msg.text}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4">
          <div className="flex items-center gap-3 text-slate-700">
            <MessageSquareText size={18} />
            <input className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder="Posez une question économique..." />
          </div>
        </div>
      </section>
    </main>
  );
}
