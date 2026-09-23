import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'
import type { CashflowRadar, Summary } from '../api'
import { fmtMonth, fmtMoney, statusClass } from '../format'

const SOURCE_COLORS: Record<string, string> = {
  commission: '#8b7cf6',
  etsy: '#f59e0b',
  patreon: '#f472b6',
  other_income: '#60a5fa',
}

function useDashboard() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const [radar, setRadar] = useState<CashflowRadar | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const [s, r] = await Promise.all([api.getSummary(), api.getRadar()])
      setSummary(s)
      setRadar(r)
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])
  return { summary, radar, loading, error, reload: load }
}

function InsightsBox() {
  const [insights, setInsights] = useState<string | null>(null)
  const [radarText, setRadarText] = useState<string | null>(null)
  const [working, setWorking] = useState(false)
  const [error, setError] = useState('')

  const runInsights = async () => {
    setWorking(true)
    setError('')
    try {
      const [i, c] = await Promise.all([api.getInsights(), api.getRadarNarrative()])
      setInsights(i.insights)
      setRadarText(`${c.narrative}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed')
    } finally {
      setWorking(false)
    }
  }

  return (
    <div className="card">
      <h3>AI Financial Coach</h3>
      <p className="text-dim" style={{ fontSize: 13, lineHeight: 1.5 }}>
        Ask the model to read your numbers and explain what they mean — stream health, your effective hourly rate, and
        the next 30 days.
      </p>
      <button className="btn" onClick={runInsights} disabled={working}>
        {working ? 'Thinking…' : 'Generate insights'}
      </button>
      {error && <p className="error">{error}</p>}
      {insights && <div className="insights-box" style={{ marginTop: 12 }}>{insights}</div>}
      {radarText && (
        <div className="insights-box" style={{ marginTop: 10 }}>
          {radarText}
        </div>
      )}
    </div>
  )
}

export function Dashboard() {
  const { summary, radar, loading, error } = useDashboard()

  if (loading) return <div className="loading">Loading dashboard…</div>
  if (error || !summary || !radar) return <div className="error">{error || 'No data'}</div>

  const sources = Object.entries(summary.per_source_net).map(([name, net]) => ({
    name: name.replace('_', ' '),
    net,
    color: SOURCE_COLORS[name] ?? '#9aa3b2',
  }))

  return (
    <div className="stack">
      <div className="grid cols-4">
        <div className="card">
          <h3>Net balance</h3>
          <div className="big">{fmtMoney(summary.balance)}</div>
          <div className="hint">all-time income − expenses</div>
        </div>
        <div className="card">
          <h3>Effective rate</h3>
          <div className="big">{summary.hourly_rate ? fmtMoney(summary.hourly_rate) : '—'}</div>
          <div className="hint">per hour across commissions</div>
        </div>
        <div className="card">
          <h3>Platform fees paid</h3>
          <div className="big">{fmtMoney(summary.total_fees)}</div>
          <div className="hint">Etsy, payment processors</div>
        </div>
        <div className="card">
          <h3>Cash-flow level</h3>
          <div className="big">
            <span className={statusClass(radar.level)}>{radar.level}</span>
          </div>
          <div className="hint">
            {radar.coverage_pct === null ? 'no spend history' : `${radar.coverage_pct}% 30-day coverage`}
          </div>
        </div>
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3>Net income by source</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={sources} margin={{ top: 12, right: 8, left: 8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262b36" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#9aa3b2', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#9aa3b2', fontSize: 12 }} axisLine={false} tickLine={false} width={54} />
              <Tooltip
                formatter={(v) => [fmtMoney(Number(v)), 'Net']}
                contentStyle={{ background: '#171a21', border: '1px solid #262b36', borderRadius: 10 }}
                labelStyle={{ color: '#e8eaf0' }}
              />
              <Bar dataKey="net" radius={[6, 6, 0, 0]}>
                {sources.map((s) => (
                  <Cell key={s.name} fill={s.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Monthly trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={summary.monthly_trend} margin={{ top: 12, right: 8, left: 8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262b36" vertical={false} />
              <XAxis
                dataKey="month"
                tick={{ fill: '#9aa3b2', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={fmtMonth}
              />
              <YAxis tick={{ fill: '#9aa3b2', fontSize: 12 }} axisLine={false} tickLine={false} width={54} />
              <Tooltip
                formatter={(v, n) => [fmtMoney(Number(v)), String(n)]}
                contentStyle={{ background: '#171a21', border: '1px solid #262b36', borderRadius: 10 }}
                labelStyle={{ color: '#e8eaf0' }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: '#9aa3b2' }} />
              <Bar dataKey="income" fill="#4ade80" radius={[6, 6, 0, 0]} />
              <Bar dataKey="expense" fill="#f87171" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid cols-2">
        <InsightsBox />
        <div className="card">
          <h3>Cash-flow radar · next 30 days</h3>
          <div className="grid cols-2" style={{ marginTop: 10 }}>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Committed income</div>
              <div className="money stat-positive" style={{ fontSize: 20 }}>{fmtMoney(radar.committed_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Projected spend</div>
              <div className="money stat-negative" style={{ fontSize: 20 }}>{fmtMoney(radar.burn_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Projected balance</div>
              <div className="money" style={{ fontSize: 20 }}>{fmtMoney(radar.projected_balance_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Burn rate</div>
              <div className="money" style={{ fontSize: 20 }}>{fmtMoney(radar.burn_per_day)}<span className="text-dim" style={{ fontSize: 12 }}>/day</span></div>
            </div>
          </div>
          <div className="hint" style={{ marginTop: 14 }}>
            {radar.coverage_pct === null
              ? 'Add a few transactions to unlock the forecast.'
              : `Balance + committed income cover ${radar.coverage_pct}% of projected spend.`}
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Top merchants</h3>
        <div className="grid cols-3">
          {summary.top_merchants.map((m, i) => (
            <div key={m.merchant} className="text-dim">
              <span style={{ fontSize: 12 }}>#{i + 1} {m.merchant}</span>
              <div className="money" style={{ color: 'var(--text)', fontSize: 18 }}>{fmtMoney(m.total)}</div>
            </div>
          ))}
          {summary.top_merchants.length === 0 && <div className="text-dim">No expense data yet.</div>}
        </div>
      </div>
    </div>
  )
}