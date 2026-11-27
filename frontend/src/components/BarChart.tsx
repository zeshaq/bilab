import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export function BarChart({
  data,
  xKey,
  yKey,
  title,
}: {
  data: Record<string, string>[]
  xKey: string
  yKey: string
  title: string
}) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!ref.current) return
    const chart = echarts.init(ref.current)
    chart.setOption({
      title: { text: title, left: 'center', textStyle: { fontSize: 15 } },
      grid: { left: 70, right: 20, top: 55, bottom: 70 },
      xAxis: {
        type: 'category',
        data: data.map((d) => d[xKey]),
        axisLabel: { rotate: 30, fontSize: 11 },
      },
      yAxis: { type: 'value' },
      tooltip: { trigger: 'axis' },
      series: [
        {
          type: 'bar',
          data: data.map((d) => Number(d[yKey])),
          itemStyle: { color: '#4f8ef7' },
          barMaxWidth: 48,
        },
      ],
    })
    const onResize = () => chart.resize()
    window.addEventListener('resize', onResize)
    return () => {
      window.removeEventListener('resize', onResize)
      chart.dispose()
    }
  }, [data, xKey, yKey, title])
  return <div ref={ref} style={{ width: '100%', height: 360 }} />
}
