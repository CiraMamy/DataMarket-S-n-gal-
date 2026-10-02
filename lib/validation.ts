import { z } from 'zod';

export const datasetSchema = z.object({
  id: z.string(),
  name: z.string(),
  category: z.string(),
  source: z.string(),
  territory: z.string(),
  period: z.string(),
  frequency: z.string(),
  description: z.string(),
  status: z.enum(['draft', 'active', 'ready', 'archived']),
  updatedAt: z.string(),
  license: z.string(),
});

export const studySchema = z.object({
  id: z.string(),
  title: z.string(),
  summary: z.string(),
  sector: z.string(),
  region: z.string(),
  status: z.enum(['draft', 'active', 'ready', 'archived']),
  updatedAt: z.string(),
  tam: z.string(),
  sam: z.string(),
  som: z.string(),
});

export const authSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const organizationSchema = z.object({
  name: z.string().min(2),
  country: z.string().min(2),
});
