import type { DatasetMetadata, PreprocessingMetadata } from '../../types/api'

export interface DataProvenanceProps {
  dataset: DatasetMetadata
  preprocessing: PreprocessingMetadata
}

export function DataProvenance({ dataset, preprocessing }: DataProvenanceProps) {
  return (
    <section aria-labelledby="data-provenance-heading" className="rounded-lg border border-border bg-card p-5">
      <h2 id="data-provenance-heading" className="section-heading">Data provenance</h2>
      <p className="mt-1 text-sm text-muted-foreground">The dashboard reads governed, packaged historical artifacts.</p>
      <h3 className="mt-5 text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground">Preparation lineage</h3>
      <dl className="mt-5 grid gap-x-6 gap-y-4 text-sm sm:grid-cols-2">
        <ProvenanceItem label="Source module" value={dataset.source_module} />
        <ProvenanceItem label="Source package" value={dataset.source_package_version} />
        <ProvenanceItem label="Raw SHA-256" value={dataset.raw_sha256} mono />
        <ProvenanceItem label="Observed values" value={`${dataset.observed_values.toLocaleString()} · ${dataset.missing_values} missing`} />
        <ProvenanceItem label="Historical only" value={dataset.historical_only ? 'Yes' : 'No'} />
        <ProvenanceItem label="Preprocessing" value={preprocessing.monthly_aggregation} />
        <ProvenanceItem label="Feature contract" value={preprocessing.feature_contract} />
      </dl>
    </section>
  )
}

function ProvenanceItem({ label, mono = false, value }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-[0.1em] text-muted-foreground">{label}</dt>
      <dd className={`mt-1 font-medium ${mono ? 'break-all font-mono text-xs' : ''}`}>{value}</dd>
    </div>
  )
}
