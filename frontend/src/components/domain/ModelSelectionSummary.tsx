import type { ModelSelection } from '../../types/api'

export interface ModelSelectionSummaryProps {
  selection: ModelSelection
  developmentMae?: number
  foldCount: number
}

export function ModelSelectionSummary({ developmentMae, foldCount, selection }: ModelSelectionSummaryProps) {
  return (
    <section aria-labelledby="model-selection-heading" className="rounded-lg border border-primary/30 bg-primary-muted/45 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-primary">Selected by development</p>
      <h2 id="model-selection-heading" className="mt-2 text-xl font-semibold tracking-tight">{selection.selected_model}</h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{selection.rationale}</p>
      <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-3">
        <div><dt className="text-xs text-muted-foreground">Evidence split</dt><dd className="mt-1 font-medium">{selection.evidence_split}</dd></div>
        <div><dt className="text-xs text-muted-foreground">Development folds</dt><dd className="mt-1 font-medium">{foldCount} rolling-origin folds</dd></div>
        <div><dt className="text-xs text-muted-foreground">Development MAE</dt><dd className="tabular mt-1 font-medium">{developmentMae === undefined ? '—' : `${developmentMae.toFixed(3)} ppm`}</dd></div>
      </dl>
      <p className="mt-4 border-t border-primary/20 pt-3 text-xs text-muted-foreground">Final-test metrics are post-selection evaluation and do not change this selection.</p>
    </section>
  )
}
