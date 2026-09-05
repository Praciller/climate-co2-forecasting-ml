import type { ModelSelection } from '../../types/api'

export interface ModelSelectionSummaryProps {
  selection: ModelSelection
  developmentMae?: number
  foldCount: number
  finalTestWinner?: {
    model: string
    mae: number
    samples: number
  }
}

export function ModelSelectionSummary({ developmentMae, finalTestWinner, foldCount, selection }: ModelSelectionSummaryProps) {
  return (
    <section aria-labelledby="model-selection-summary-heading" className="rounded-lg border border-primary/30 bg-primary-muted/45 p-5">
      <h2 id="model-selection-summary-heading" className="section-heading">Model selection</h2>
      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div aria-labelledby="model-selection-development-heading">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-primary">Selected by development</p>
          <h3 id="model-selection-development-heading" className="mt-2 text-xl font-semibold tracking-tight">{selection.selected_model}</h3>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">Selection uses {selection.metric}. {selection.rationale}</p>
          <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
            <div><dt className="text-xs text-muted-foreground">Evidence split</dt><dd className="mt-1 font-medium">{selection.evidence_split}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Development folds</dt><dd className="mt-1 font-medium">{foldCount} rolling-origin folds</dd></div>
            <div><dt className="text-xs text-muted-foreground">Development mean MAE</dt><dd className="tabular mt-1 font-medium">{developmentMae === undefined ? '—' : `${developmentMae.toFixed(3)} ppm`}</dd></div>
          </dl>
        </div>
        <div aria-labelledby="model-selection-final-test-heading" className="border-t border-primary/20 pt-5 lg:border-l lg:border-t-0 lg:pl-5 lg:pt-0">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">Post-selection evaluation</p>
          <h3 id="model-selection-final-test-heading" className="mt-2 text-xl font-semibold tracking-tight">Lowest final-test MAE</h3>
          <p className="mt-2 text-lg font-semibold">{finalTestWinner?.model ?? 'Unavailable'}</p>
          <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
            <div><dt className="text-xs text-muted-foreground">Final-test MAE</dt><dd className="tabular mt-1 font-medium">{finalTestWinner ? `${finalTestWinner.mae.toFixed(3)} ppm` : '—'}</dd></div>
            <div><dt className="text-xs text-muted-foreground">Held-out evidence</dt><dd className="mt-1 font-medium">{finalTestWinner ? `${finalTestWinner.samples} months` : '—'}</dd></div>
          </dl>
        </div>
      </div>
      <p className="mt-5 border-t border-primary/20 pt-4 text-sm leading-6 text-muted-foreground">The final test evaluates after selection; it does not choose or replace the serving model.</p>
    </section>
  )
}
