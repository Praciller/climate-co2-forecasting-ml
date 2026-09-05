import type {
  AnomalyPoint,
  DashboardData,
  ForecastResponse,
  HistoricalPoint,
  ModelInfo,
} from '../types/api'
import { resolveApiBase } from './api-config'

const API_URL = resolveApiBase(import.meta.env)

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { signal })
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}.`)
  }
  return response.json() as Promise<T>
}

export async function getDashboardData(
  signal?: AbortSignal,
): Promise<DashboardData> {
  const [historical, modelInfo, anomalies] = await Promise.all([
    request<HistoricalPoint[]>('/historical-data', signal),
    request<ModelInfo>('/model-info', signal),
    request<AnomalyPoint[]>('/anomalies', signal),
  ])
  return { historical, modelInfo, anomalies }
}

export function getForecast(
  horizonMonths: number,
  signal?: AbortSignal,
): Promise<ForecastResponse> {
  return request<ForecastResponse>(
    `/forecast?horizon_months=${horizonMonths}`,
    signal,
  )
}
