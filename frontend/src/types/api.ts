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
  model_version: string
  forecast_origin: string
  horizon_months: number
  frequency: string
  protocol: string
  interval_method: string
  interval_nominal_coverage: number
  interval_coverage_scope: string
  generated_at: string
  limitations: string[]
  forecast: ForecastPoint[]
}

export interface AnomalyPoint {
  date: string
  co2: number
  residual_ppm: number | null
  residual_anomaly: boolean
  isolation_score: number | null
  isolation_forest_anomaly: boolean
  methods: string[]
}

export interface ModelMetrics {
  mae: number
  rmse: number
  mape: number | null
  smape: number | null
  mase: number
}

export interface SplitBoundaries {
  train_end: string
  validation_start: string
  validation_end: string
  test_start: string
  test_end: string
}

export interface DatasetMetadata {
  name: string
  source_module: string
  source_package_version: string
  raw_sha256: string
  weekly_calendar_rows: number
  observed_values: number
  missing_values: number
  period: string
  frequency: string
  unit: string
  historical_only: boolean
}

export interface PreprocessingMetadata {
  version: string
  monthly_aggregation: string
  missing_month_strategy: string
  feature_contract: string
}

export interface ForecastingProtocol {
  name: string
  training_window: string
  horizon: number
  actual_previous_observations_available: boolean
  split_boundaries: SplitBoundaries
}

export interface ModelSelection {
  selected_model: string
  metric: string
  tie_break: string
  evidence_split: string
  rationale: string
}

export interface IntervalMetadata {
  method: string
  nominal_coverage: number
  calibration_split: string
  calibration_end: string
  calibration_samples: number
  evaluation_split: string
  evaluation_samples: number
  observed_test_coverage: number
  empirical_coverage: number
  average_test_width_ppm: number
  radius_ppm: number
  horizon: number
  limitations: string
}

export interface EvaluationSplit {
  start: string
  end: string
  samples: number
  models: Record<string, ModelMetrics>
}

export interface TemporalContract {
  feature_information_cutoff: string
  train_end: string
  validation_start: string
  validation_end: string
  test_start: string
  test_end: string
  imputed_months_checked: number
}

export interface RollingFoldMetric {
  mae: number
  rmse: number
  smape: number | null
  mase: number
}

export interface RollingOriginFold {
  fold_id: number
  train_start: string
  train_end: string
  validation_start: string
  validation_end: string
  train_samples: number
  validation_samples: number
  horizon: number
  models: Record<string, RollingFoldMetric>
}

export interface RollingMetricSummary {
  mean: number
  median: number
  std: number
}

export interface RollingAggregateMetrics {
  mae: RollingMetricSummary
  rmse: RollingMetricSummary
  smape: RollingMetricSummary
  mase: RollingMetricSummary
  folds: { count: number }
}

export interface RollingOriginEvidence {
  protocol: string
  development_end: string
  fold_count: number
  models: string[]
  folds: RollingOriginFold[]
  aggregate: Record<string, RollingAggregateMetrics>
}

export interface SmokeEvidence {
  evidence_type: string
  ranking_eligible: boolean
  epochs_requested: number
  epochs_completed: number
  best_validation_loss: number
  validation_metrics: ModelMetrics
}

export interface EvaluationMetrics {
  schema_version: string
  protocol: ForecastingProtocol
  temporal_contract: TemporalContract
  selection: ModelSelection
  validation: EvaluationSplit
  final_test: EvaluationSplit
  rolling_origin: RollingOriginEvidence
  smoke_evidence: Record<string, SmokeEvidence>
}

export interface ModelInfo {
  active_model: string
  model_version: string
  dataset: DatasetMetadata
  preprocessing: PreprocessingMetadata
  split_boundaries: SplitBoundaries
  forecasting_protocol: ForecastingProtocol
  selection: ModelSelection
  interval: IntervalMetadata
  training_rows: number
  training_end: string
  artifact_generated_at: string
  candidate_models: string[]
  metrics: EvaluationMetrics
}

export interface DashboardData {
  historical: HistoricalPoint[]
  modelInfo: ModelInfo
  anomalies: AnomalyPoint[]
}
