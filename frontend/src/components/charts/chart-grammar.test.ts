import { describe, expect, it } from 'vitest'
import { chartColors, formatChartDate, formatPpm } from './chart-grammar'

describe('chart grammar', () => {
  it('uses semantic chart tokens and exact ppm formatting', () => {
    expect(chartColors.forecast).toBe('var(--color-chart-forecast)')
    expect(formatPpm(371.976)).toBe('371.98 ppm')
    expect(formatPpm(null)).toBe('—')
  })
  it('formats valid dates and preserves invalid labels', () => {
    expect(formatChartDate('2001-12-31')).toMatch(/Dec 2001/)
    expect(formatChartDate('not-a-date')).toBe('not-a-date')
  })
})
