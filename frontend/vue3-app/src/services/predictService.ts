import type { PredictionFormModel, PredictionResponse } from '@/types/dashboard';
import { requestJson } from './http';

export async function predictHeartRisk(form: PredictionFormModel): Promise<PredictionResponse> {
  return requestJson<PredictionResponse>('/predict', {
    method: 'POST',
    body: JSON.stringify(form),
  });
}
