import { Badge } from '../ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table'
import type { EvaluationSplit } from '../../types/api'

export interface ModelComparisonProps {
  selectedModel: string
  finalTest: EvaluationSplit
}

export function ModelComparison({ finalTest, selectedModel }: ModelComparisonProps) {
  const rows = Object.entries(finalTest.models).sort(([, left], [, right]) => left.mae - right.mae)
  const lowestFinalTestModel = rows[0]?.[0]

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <Table className="min-w-[720px]">
        <caption className="sr-only">Final-test model comparison from {finalTest.start} to {finalTest.end}</caption>
        <TableHeader>
          <TableRow>
            <TableHead>Model</TableHead><TableHead>Evidence role</TableHead>
            <TableHead className="text-right">MAE</TableHead><TableHead className="text-right">RMSE</TableHead>
            <TableHead className="text-right">MAPE</TableHead><TableHead className="text-right">sMAPE</TableHead><TableHead className="text-right">MASE</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map(([name, metrics]) => (
            <TableRow key={name} className={name === selectedModel ? 'bg-primary-muted/45' : undefined}>
              <TableCell className="font-medium" aria-label={name === selectedModel ? 'Selected by development' : undefined}>{name}</TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1.5">
                  {name === lowestFinalTestModel ? <Badge variant="secondary">Lowest final-test MAE</Badge> : null}
                </div>
              </TableCell>
              <MetricCell value={metrics.mae} /><MetricCell value={metrics.rmse} />
              <MetricCell value={metrics.mape} suffix="%" /><MetricCell value={metrics.smape} suffix="%" /><MetricCell value={metrics.mase} />
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

function MetricCell({ suffix = '', value }: { value: number | null; suffix?: string }) {
  return <TableCell className="tabular text-right text-muted-foreground">{value === null ? '—' : `${value.toFixed(3)}${suffix}`}</TableCell>
}
