export type RiskLevel = 'low' | 'medium' | 'high';

export interface DashboardOverview {
  sampleCount: number;
  positiveCount: number;
  negativeCount: number;
  prevalenceRate: number;
  datasetCount: number;
  modelAuc: number;
  updatedAt: string;
  datasets: Array<{
    name: string;
    rows: number;
    columns: number;
    target: string;
    usage: string;
  }>;
}

export interface AgeAnalysisItem {
  ageGroup: string;
  sampleCount: number;
  positiveCount: number;
  prevalenceRate: number;
}

export interface LifestyleAnalysisItem {
  factor: string;
  category: string;
  sampleCount: number;
  positiveCount: number;
  prevalenceRate: number;
}

export interface ClinicalGroupItem {
  category: string;
  sampleCount: number;
  positiveCount: number;
  prevalenceRate: number;
}

export interface ClinicalFeatureItem {
  feature: string;
  label: string;
  groups: ClinicalGroupItem[];
}

export interface ModelMetricItem {
  name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  auc: number;
}

export interface FeatureImportanceItem {
  feature: string;
  label: string;
  importance: number;
}

export interface PredictionFormModel {
  BMI: number;
  Smoking: 'Yes' | 'No';
  AlcoholDrinking: 'Yes' | 'No';
  Stroke: 'Yes' | 'No';
  PhysicalHealth: number;
  MentalHealth: number;
  DiffWalking: 'Yes' | 'No';
  Sex: 'Male' | 'Female';
  AgeCategory: string;
  Diabetic: 'No' | 'Yes' | 'Borderline' | 'During pregnancy';
  PhysicalActivity: 'Yes' | 'No';
  GenHealth: 'Poor' | 'Fair' | 'Good' | 'Very good' | 'Excellent';
  SleepTime: number;
  Asthma: 'Yes' | 'No';
  KidneyDisease: 'Yes' | 'No';
  SkinCancer: 'Yes' | 'No';
}

export interface PredictionFactor {
  feature: string;
  label: string;
  impact: string;
}

export interface PredictionResponse {
  probability: number;
  riskLevel: RiskLevel;
  riskLabel: string;
  model: string;
  topFactors: PredictionFactor[];
  createdAt: string;
}

export interface SummarySlice {
  label: string;
  value: string;
  sampleCount: number;
  prevalenceRate: number;
  tone: RiskLevel;
}

export interface DashboardBundle {
  overview: DashboardOverview;
  age: { items: AgeAnalysisItem[] };
  lifestyle: { items: LifestyleAnalysisItem[] };
  clinical: { items: ClinicalFeatureItem[] };
  metrics: { models: ModelMetricItem[]; featureImportance: FeatureImportanceItem[] };
  derived: {
    gender: SummarySlice[];
    bmi: SummarySlice[];
    comorbidity: SummarySlice[];
  };
}

export const createDefaultPredictionForm = (): PredictionFormModel => ({
  BMI: 28.4,
  Smoking: 'Yes',
  AlcoholDrinking: 'No',
  Stroke: 'No',
  PhysicalHealth: 4,
  MentalHealth: 2,
  DiffWalking: 'No',
  Sex: 'Male',
  AgeCategory: '60-64',
  Diabetic: 'No',
  PhysicalActivity: 'Yes',
  GenHealth: 'Good',
  SleepTime: 7,
  Asthma: 'No',
  KidneyDisease: 'No',
  SkinCancer: 'No',
});
