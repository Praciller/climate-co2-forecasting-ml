export type PageId =
  | 'overview'
  | 'data'
  | 'forecasting'
  | 'anomalies'
  | 'evaluation'

export interface HistoricalPoint {
  date: string
  co2: number
  rolling_mean_12: number | null
}

export interface ForecastPoint {
  date: string
  prediction: number
  lower: number
  upper: number
}

export interface ForecastResponse {
  model: string
  horizon_months: number
  generated_at: string
  forecast: ForecastPoint[]
}

export interface AnomalyPoint {
  date: string
  co2: number
  residual_anomaly: boolean
  isolation_forest_anomaly: boolean
  methods: string[]
}

export interface ModelMetrics {
  mae: number
  rmse: number
  mape: number
  smape: number
  mase: number
}

export interface ForecastMetrics {
  best_model?: string
  test_start?: string
  test_end?: string
  models?: Record<string, ModelMetrics>
}

export interface ModelInfo {
  active_model: string
  live_forecast_mode: string
  training_rows: number
  training_end: string
  available_models: string[]
  metrics: ForecastMetrics
}

export interface DashboardData {
  historical: HistoricalPoint[]
  modelInfo: ModelInfo
  anomalies: AnomalyPoint[]
}
