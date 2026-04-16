import { createDefaultPredictionForm, type PredictionFormModel } from '@/types/dashboard';

export { createDefaultPredictionForm };

export const predictionFieldOrder: Array<keyof PredictionFormModel> = [
  'BMI',
  'Smoking',
  'AlcoholDrinking',
  'Stroke',
  'PhysicalHealth',
  'MentalHealth',
  'DiffWalking',
  'Sex',
  'AgeCategory',
  'Diabetic',
  'PhysicalActivity',
  'GenHealth',
  'SleepTime',
  'Asthma',
  'KidneyDisease',
  'SkinCancer',
];
