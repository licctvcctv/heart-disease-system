import {
  type DashboardBundle,
  type LifestyleAnalysisItem,
  type SummarySlice,
} from '@/types/dashboard';
import { requestJson } from './http';

const buildSummary = (items: LifestyleAnalysisItem[], factors: string[]): SummarySlice[] => {
  const matched = items.filter((item) => factors.includes(item.factor));
  return matched.map((item) => ({
    label: item.category,
    value: `${(item.prevalenceRate * 100).toFixed(1)}%`,
    sampleCount: item.sampleCount,
    prevalenceRate: item.prevalenceRate,
    tone: item.prevalenceRate >= 0.12 ? 'high' : item.prevalenceRate >= 0.08 ? 'medium' : 'low',
    }));
};

export async function loadDashboardBundle(): Promise<DashboardBundle> {
  const [overview, age, lifestyle, clinical, metrics] = await Promise.all([
    requestJson<DashboardBundle['overview']>('/dashboard/overview'),
    requestJson<DashboardBundle['age']>('/analysis/age'),
    requestJson<DashboardBundle['lifestyle']>('/analysis/lifestyle'),
    requestJson<DashboardBundle['clinical']>('/analysis/clinical'),
    requestJson<DashboardBundle['metrics']>('/model/metrics'),
  ]);

  const lifestyleItems = lifestyle.items || [];

  return {
    overview,
    age,
    lifestyle,
    clinical,
    metrics,
    derived: {
      gender: buildSummary(lifestyleItems, ['Sex']),
      bmi: buildSummary(lifestyleItems, ['BMI']),
      comorbidity: buildSummary(lifestyleItems, ['Stroke', 'Diabetic', 'KidneyDisease', 'Asthma', 'SkinCancer']),
    },
  };
}
