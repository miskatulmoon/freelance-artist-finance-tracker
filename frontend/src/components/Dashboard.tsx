import { useDashboard } from '../hooks/useDashboard'
import { CashRunway } from './CashRunway'
import { TrendCharts } from './TrendCharts'

function DashboardSkeleton() {
  return (
    <div className="stack">
      <div className="card" style={{ paddingInline: 0, overflow: 'hidden' }}>
        <div className="sk-block" style={{ width: '100%', height: 210 }} />
      </div>
      <div className="grid cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div className="card" key={i} style={{ paddingInline: 0, overflow: 'hidden' }}>
            <div className="sk-block" style={{ width: '100%', height: 124 }} />
          </div>
        ))}
      </div>
      <div className="grid cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div className="card" key={i} style={{ paddingInline: 0, overflow: 'hidden' }}>
            <div className="sk-block" style={{ width: '100%', height: 236 }} />
          </div>
        ))}
      </div>
      <div className="card" style={{ paddingInline: 0, overflow: 'hidden' }}>
        <div className="sk-block" style={{ width: '100%', height: 110 }} />
      </div>
    </div>
  )
}

export function Dashboard() {
  const { summary, radar, loading, error, isError, reload } = useDashboard()

  if (loading) return <DashboardSkeleton />
  if (isError || !summary || !radar) {
    return (
      <div className="error" role="alert">
        <p>{error || 'No data'}</p>
        <button onClick={() => reload()} type="button">Retry</button>
      </div>
    )
  }

  return (
    <div className="stack">
      <CashRunway />
      <TrendCharts />
    </div>
  )
}
