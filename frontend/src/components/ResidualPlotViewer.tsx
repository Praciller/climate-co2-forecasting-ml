interface ResidualPlotViewerProps {
  alt: string
  src: string
}

export function ResidualPlotViewer({ alt, src }: ResidualPlotViewerProps) {
  return (
    <figure className="overflow-hidden rounded-lg border border-rule bg-surface">
      <img src={src} alt={alt} className="h-auto w-full" loading="lazy" />
    </figure>
  )
}
