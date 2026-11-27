import { useEffect, useState } from 'react'
import { runQuery } from '../api'
import { BarChart } from './BarChart'
import { MetricCard } from './MetricCard'

// Renders one saved chart: runs its governed query as the current user, then
// renders by chart_type. A "number" chart is a big-number card; everything else
// falls back to a bar chart over the first dimension/measure pair.
export function ChartRenderer({
  title,
  chartType,
  query,
}: {
  title: string
  chartType: string
  query: Record<string, unknown>
}) {
  const [data, setData] = useState<Record<string, string>[]>([])
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    runQuery(query).then(setData).catch((e) => setErr(String(e)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (err) return <div className="chart-error">"{title}": {err}</div>

  if (chartType === 'number') {
    const first = data[0] || {}
    const value = Object.values(first)[0]
    return <MetricCard label={title} value={value != null ? String(value) : '…'} />
  }

  const measures = (query.measures as string[]) || []
  const dimensions = (query.dimensions as string[]) || []
  const yKey = measures[0]
  const xKey = dimensions[0]

  if (!xKey || !yKey) {
    const first = data[0] || {}
    const value = Object.values(first)[0]
    return <MetricCard label={title} value={value != null ? String(value) : '…'} />
  }

  return <BarChart title={title} data={data} xKey={xKey} yKey={yKey} />
}
