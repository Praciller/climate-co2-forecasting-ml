import { lazy, Suspense, useState } from 'react'

import { AppShell } from './components/AppShell'
import { ErrorMessage } from './components/ErrorMessage'
import { LoadingState } from './components/LoadingState'
import { useDashboardData } from './hooks/useDashboardData'
import type { PageId } from './types/api'

const AnomalyDetectionPage = lazy(() => import('./pages/AnomalyDetectionPage'))
const DataExplorerPage = lazy(() => import('./pages/DataExplorerPage'))
const ForecastingPage = lazy(() => import('./pages/ForecastingPage'))
const ModelEvaluationPage = lazy(() => import('./pages/ModelEvaluationPage'))
const OverviewPage = lazy(() => import('./pages/OverviewPage'))

const PAGE_TITLES: Record<PageId, string> = {
  overview: 'Overview',
  data: 'Data Explorer',
  forecasting: 'Forecasting',
  anomalies: 'Anomaly Detection',
  evaluation: 'Model Evaluation',
}

function App() {
  const [page, setPage] = useState<PageId>('overview')
  const { data, error, isLoading, reload } = useDashboardData()

  let content
  if (isLoading) {
    content = <LoadingState />
  } else if (error || !data) {
    content = (
      <ErrorMessage
        message={error ?? 'API data is unavailable.'}
        onRetry={reload}
      />
    )
  } else if (page === 'data') {
    content = (
      <DataExplorerPage
        historical={data.historical}
        modelInfo={data.modelInfo}
      />
    )
  } else if (page === 'forecasting') {
    content = <ForecastingPage historical={data.historical} />
  } else if (page === 'anomalies') {
    content = (
      <AnomalyDetectionPage
        anomalies={data.anomalies}
        historical={data.historical}
      />
    )
  } else if (page === 'evaluation') {
    content = <ModelEvaluationPage modelInfo={data.modelInfo} />
  } else {
    content = (
      <OverviewPage
        anomalies={data.anomalies}
        historical={data.historical}
        modelInfo={data.modelInfo}
      />
    )
  }

  return (
    <AppShell
      activePage={page}
      apiStatus={isLoading ? 'connecting' : data && !error ? 'connected' : 'unavailable'}
      pageTitle={PAGE_TITLES[page]}
      onNavigate={setPage}
    >
      <Suspense fallback={<LoadingState />}>{content}</Suspense>
    </AppShell>
  )
}

export default App
