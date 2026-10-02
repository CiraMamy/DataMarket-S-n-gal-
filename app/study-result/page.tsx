import { PageHeader } from '@/components/page-header';
import { ConfirmationDialog } from '@/components/confirmation-dialog';
import { SourceBadge } from '@/components/source-badge';
import { ProvenancePanel } from '@/components/provenance-panel';
import { AssumptionPanel } from '@/components/assumption-panel';
import { LimitationPanel } from '@/components/limitation-panel';
import { EstimateBreakdown } from '@/components/estimate-breakdown';
import { EvidencePanel } from '@/components/evidence-panel';
import { MarketSizeChart } from '@/components/market-size-chart';
import { TimeSeriesChart } from '@/components/time-series-chart';

export default function StudyResultPage() {
  return (
    <main className="container-shell space-y-8 pb-10 pt-8">
      <PageHeader
        eyebrow="Résultats d'étude"
        title="Superette à Dakar"
        action={<span className="chip">Analyse terminée</span>}
      />

      {/* Synthèse */}
      <section className="surface p-6 shadow-soft">
        <h2 className="mb-4 text-2xl font-semibold text-navy">Synthèse</h2>
        <p className="text-slate-700">
          Le potentiel de marché pour une superette dans le secteur de proximité à Dakar reste élevé,
          porté par une demande urbaine structurée et une densité de population significative.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <SourceBadge source="ANSD" period="2023" />
          <SourceBadge source="EHCVM II" period="2021-2022" />
          <SourceBadge source="Modèle DataMarket" period="2026" />
        </div>
      </section>

      {/* TAM / SAM / SOM */}
      <section className="grid gap-6 lg:grid-cols-3">
        <ProvenancePanel
          label="TAM (Total Addressable Market)"
          value="200 M FCFA"
          source="ANSD + EHCVM"
          methodology="Population × dépense annuelle"
        />
        <ProvenancePanel
          label="SAM (Serviceable Available Market)"
          value="90 M FCFA"
          source="Estimation régionale"
          methodology="TAM × zone de chalandise (45%)"
        />
        <ProvenancePanel
          label="SOM (Serviceable Obtainable Market)"
          value="27 M FCFA"
          source="Hypothèse métier"
          methodology="SAM × part visée (30%)"
        />
      </section>

      {/* Graphiques */}
      <section className="surface p-6 shadow-soft">
        <h2 className="mb-5 text-2xl font-semibold text-navy">Comparaison TAM/SAM/SOM par territoire</h2>
        <MarketSizeChart />
      </section>

      <section className="surface p-6 shadow-soft">
        <h2 className="mb-5 text-2xl font-semibold text-navy">Tendance du marché</h2>
        <TimeSeriesChart title="Évolution du potentiel sur 4 ans" />
      </section>

      {/* Estimation détaillée */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-navy">Détail de l'estimation</h2>
        <EstimateBreakdown
          items={[
            { label: 'Population cible', value: '3,9 M', type: 'observed' },
            { label: 'Dépense moyenne annuelle par personne', value: '542 706 FCFA', type: 'observed' },
            { label: 'Taux de captation urbain', value: '55%', type: 'hypothesis' },
            { label: 'Part alimentation + hygiène', value: '88%', type: 'calculated' },
            { label: 'TAM estimé', value: '200 M FCFA', type: 'calculated' },
          ]}
        />
      </section>

      {/* Hypothèses et limites */}
      <section className="grid gap-6 lg:grid-cols-2">
        <AssumptionPanel
          assumptions={[
            { key: 'Zone de chalandise', value: '45% du SAM' },
            { key: 'Part de marché visée', value: '30% du SAM' },
            { key: 'Horizon', value: '3 ans' },
            { key: 'Croissance annuelle', value: '2,9%' },
          ]}
        />
        <LimitationPanel
          limitations={[
            'Les dépenses sont des moyennes régionales et masquent des écarts de revenu.',
            'Le SOM ne modélise pas la concurrence à l\'échelle de la rue.',
            'Les données EHCVM datent de 2021-2022, hors inflation ultérieure.',
            'La prévalence du diabète varie entre milieu urbain et rural.',
          ]}
        />
      </section>

      {/* Éléments de preuve */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-navy">Éléments de preuve</h2>
        <EvidencePanel
          evidence={[
            {
              title: 'Demande urbaine confirmée',
              detail: 'La concentration de population à Dakar (22% nationale) et le taux d\'urbanisation (54,7%) créent une demande de proximité structurée.',
            },
            {
              title: 'Budget alimentaire significatif',
              detail: 'L\'alimentation représente ~60% des dépenses de ménages urbains, soit un marché stable et prévisible.',
            },
            {
              title: 'Captation commerciale en hausse',
              detail: 'Le commerce organisé (superettes, boutiques) capture 55% du marché urbain, contre 30% en zone rurale.',
            },
          ]}
        />
      </section>

      {/* Actions */}
      <section className="flex gap-3">
        <button className="rounded-full bg-navy px-5 py-3 font-medium text-white">Télécharger le rapport PDF</button>
        <button className="rounded-full border border-slate-200 bg-white px-5 py-3 font-medium text-navy">Partager l'étude</button>
      </section>
    </main>
  );
}
