import { apiClient } from '@/lib/api/client';
import type { Analysis, DatasetRecord, MarketStudy, Report, Territory } from '@/lib/types';

const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

function withDemoFallback<T>(data: T, fallback: T): T {
  return DEMO_MODE ? data : fallback;
}

export async function fetchDatasets(): Promise<DatasetRecord[]> {
  const demo: DatasetRecord[] = [
    {
      id: 'population',
      name: 'Population régionale',
      category: 'Population',
      source: 'ANSD',
      territory: 'National',
      period: '2023',
      frequency: 'Annuel',
      description: 'Population et densité par région.',
      status: 'active',
      updatedAt: '12 août 2026',
      license: 'Ouvert',
    },
    {
      id: 'depenses',
      name: 'Dépenses par tête',
      category: 'Prix',
      source: 'EHCVM II',
      territory: 'National',
      period: '2021-2022',
      frequency: 'Annuel',
      description: 'Dépenses de consommation et budget de ménages.',
      status: 'active',
      updatedAt: '12 août 2026',
      license: 'Ouvert',
    },
  ];

  try {
    return await apiClient<DatasetRecord[]>('/datasets');
  } catch {
    return withDemoFallback(demo, demo);
  }
}

export async function fetchStudies(): Promise<MarketStudy[]> {
  const demo: MarketStudy[] = [
    {
      id: 'study-001',
      title: 'Supérette de proximité à Dakar',
      summary: 'Analyse de la demande urbaine et de la viabilité d’un point de vente alimentaire.',
      sector: 'Commerce de proximité',
      region: 'Dakar',
      status: 'ready',
      updatedAt: '22 août 2026',
      tam: '200 M FCFA',
      sam: '90 M FCFA',
      som: '27 M FCFA',
    },
  ];

  try {
    return await apiClient<MarketStudy[]>('/market-studies');
  } catch {
    return withDemoFallback(demo, demo);
  }
}

export async function fetchTerritories(): Promise<Territory[]> {
  const demo: Territory[] = [
    {
      id: 'dakar',
      name: 'Dakar',
      regionType: 'Région',
      population: '3,9 M',
      indicator: 'Potentiel élevé',
      value: 'Très fort',
      description: 'Grande concentration de demande urbaine et de consommation.',
    },
    {
      id: 'thies',
      name: 'Thiès',
      regionType: 'Région',
      population: '2,1 M',
      indicator: 'Potentiel fort',
      value: 'Fort',
      description: 'Marchés dynamiques et corridors de développement.',
    },
  ];

  try {
    return await apiClient<Territory[]>('/territories');
  } catch {
    return withDemoFallback(demo, demo);
  }
}

export async function fetchAnalyses(): Promise<Analysis[]> {
  const demo: Analysis[] = [
    {
      id: 'analysis-001',
      title: 'Analyse de la demande urbaine',
      description: 'Étude de la structure de la demande sur les territoires densément peuplés.',
      version: 'v3',
      lastUpdated: '12 août 2026',
      status: 'active',
    },
  ];

  try {
    return await apiClient<Analysis[]>('/analyses');
  } catch {
    return withDemoFallback(demo, demo);
  }
}

export async function fetchReports(): Promise<Report[]> {
  const demo: Report[] = [
    {
      id: 'report-001',
      title: 'Rapport de marché – Dakar',
      summary: 'Synthèse du potentiel de marché pour un commerce de proximité.',
      version: 'v1.2',
      state: 'generated',
    },
  ];

  try {
    return await apiClient<Report[]>('/reports');
  } catch {
    return withDemoFallback(demo, demo);
  }
}
