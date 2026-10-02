export type ApiResourceStatus = 'draft' | 'active' | 'ready' | 'archived';

export type DatasetCategory =
  | 'Population'
  | 'Santé'
  | 'Emploi'
  | 'Agriculture'
  | 'Prix'
  | 'Entreprises'
  | 'Territoires';

export type DatasetRecord = {
  id: string;
  name: string;
  category: DatasetCategory;
  source: string;
  territory: string;
  period: string;
  frequency: string;
  description: string;
  status: ApiResourceStatus;
  updatedAt: string;
  license: string;
};

export type MarketStudy = {
  id: string;
  title: string;
  summary: string;
  sector: string;
  region: string;
  status: ApiResourceStatus;
  updatedAt: string;
  tam: string;
  sam: string;
  som: string;
};

export type Territory = {
  id: string;
  name: string;
  regionType: string;
  population: string;
  indicator: string;
  value: string;
  description: string;
};

export type Analysis = {
  id: string;
  title: string;
  description: string;
  version: string;
  lastUpdated: string;
  status: ApiResourceStatus;
};

export type Report = {
  id: string;
  title: string;
  summary: string;
  version: string;
  state: 'generated' | 'running' | 'draft';
};

export type ApiErrorShape = {
  code: string;
  message: string;
  details?: string[];
};
