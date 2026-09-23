import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'
import type { CashflowRadar, Summary } from '../api'
import { fmtMonth, fmtMoney, statusClass } from '../format'

const SOURCE_COLORS: Record<string, string> = {
  commission: '#5b52c4',
  etsy: '#bd8a2e',
  patreon: '#c75d8a',
  other_income: '#2f7d6f',
}

const WASH = {
  commission: ['#b7b2ee', '#5b52c4'],
  etsy: ['#e5c88e', '#bd8a2e'],
  patreon: ['#eeb4cd', '#c75d8a'],
  other_income: ['#8cc3b6', '#2f7d6f'],
  income: ['#e2bc78', '#9a6720'],
  expense: ['#a5bdd3', '#50708e'],
} as const

const TOOLTIP_STYLE = {
  background: '#fdf8ee',
  border: '1px solid #e2d7bf',
  borderRadius: 10,
  color: '#2b241d',
  boxShadow: '0 8px 20px rgba(43,36,29,0.08)',
  fontSize: 13,
}

function WashDefs() {
  return (
    <defs>
      {Object.entries(WASH).map(([key, [light, deep]]) => (
        <linearGradient key={key} id={`wash-${key}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={light} />
          <stop offset="100%" stopColor={deep} />
        </linearGradient>
      ))}
    </defs>
  )
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
      setError(e instanceof Error ? e.message : 'Failed to load ledger')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])
  return { summary, radar, loading, error, reload: load }
}

function DashboardSkeleton() {
  return (
    <div className="stack">
      <div className="grid cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div className="card" key={i} style={{ paddingInline: 0, overflow: 'hidden' }}>
            <div className="sk-block" style={{ width: '100%', height: 78 }} />
          </div>
        ))}
      </div>
      <div className="grid cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <div className="card" key={i} style={{ paddingInline: 0, overflow: 'hidden' }}>
            <div className="sk-block" style={{ width: '100%', height: 240 }} />
          </div>
        ))}
      </div>
      <div className="card" style={{ paddingInline: 0, overflow: 'hidden' }}>
        <div className="sk-block" style={{ width: '100%', height: 120 }} />
      </div>
    </div>
  )
}

export function Dashboard() {
  const { summary, radar, loading, error } = useDashboard()

  if (loading) return <DashboardSkeleton />
  if (error || !summary || !radar) return <div className="error">{error || 'No data'}</div>

  const sources = Object.entries(summary.per_source_net).map(([name, net]) => ({
    name: name.replace('_', ' '),
    net,
    color: SOURCE_COLORS[name] ?? '#8a7f6d',
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
          <h3>
            <span className="card-head-dot">
              <span className="pigment-dot" style={{ background: 'var(--pig-commission)' }} />
              Effective rate
            </span>
          </h3>
          <div className="big">{summary.hourly_rate ? fmtMoney(summary.hourly_rate) : '—'}</div>
          <div className="hint">per hour across commissions</div>
        </div>
        <div className="card">
          <h3>
            <span className="card-head-dot">
              <span className="pigment-dot" style={{ background: 'var(--graphite)' }} />
              Platform fees paid
            </span>
          </h3>
          <div className="big">{fmtMoney(summary.total_fees)}</div>
          <div className="hint">Etsy, payment processors</div>
        </div>
        <div className="card">
          <h3>Cash-flow level</h3>
          <div className="big">
            <span className={statusClass(radar.level)}>{radar.level}</span>
          </div>
          <div className="hint">
            {radar.coverage_pct === null ? 'no spend history yet' : `${radar.coverage_pct}% 30-day coverage`}
          </div>
        </div>
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3>Net income by source</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={sources} margin={{ top: 12, right: 8, left: 8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 6" stroke="#d7caac" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#6f6350', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#6f6350', fontSize: 12 }} axisLine={false} tickLine={false} width={56} />
              <Tooltip
                formatter={(v) => [fmtMoney(Number(v)), 'Net']}
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ color: '#5a4f41', fontWeight: 600 }}
              />
              <WashDefs />
              <Bar dataKey="net" radius={[7, 7, 0, 0]}>
                {sources.map((s) => (
                  <Cell key={s.name} fill={`url(#wash-${s.name.replace(' ', '_')})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Monthly trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={summary.monthly_trend} margin={{ top: 12, right: 8, left: 8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 6" stroke="#d7caac" vertical={false} />
              <XAxis
                dataKey="month"
                tick={{ fill: '#6f6350', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={fmtMonth}
              />
              <YAxis tick={{ fill: '#6f6350', fontSize: 12 }} axisLine={false} tickLine={false} width={56} />
              <Tooltip
                formatter={(v, n) => [fmtMoney(Number(v)), String(n)]}
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ color: '#5a4f41', fontWeight: 600 }}
              />
              <Legend wrapperStyle={{ fontSize: 12, color: '#6f6350' }} />
              <WashDefs />
              <Bar dataKey="income" fill="url(#wash-income)" radius={[7, 7, 0, 0]} />
              <Bar dataKey="expense" fill="url(#wash-expense)" radius={[7, 7, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3>Cash-flow · next 30 days</h3>
          <div className="grid cols-2" style={{ marginTop: 10 }}>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Committed income</div>
              <div className="money stat-positive" style={{ fontSize: 19 }}>{fmtMoney(radar.committed_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Projected spend</div>
              <div className="money stat-negative" style={{ fontSize: 19 }}>{fmtMoney(radar.burn_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Projected balance</div>
              <div className="money" style={{ fontSize: 19 }}>{fmtMoney(radar.projected_balance_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 12 }}>Burn rate</div>
              <div className="money" style={{ fontSize: 19 }}>
                {fmtMoney(radar.burn_per_day)}<span className="text-dim" style={{ fontSize: 12 }}>/day</span>
              </div>
            </div>
          </div>
          <div className="hint" style={{ marginTop: 14 }}>
            {radar.coverage_pct === null
              ? 'Add a few slips to unlock the forecast.'
              : `Balance + committed income cover ${radar.coverage_pct}% of projected spend.`}
          </div>
        </div>

        <div className="card">
          <h3>Top merchants</h3>
          <div className="grid cols-3" style={{ marginTop: 10 }}>
            {summary.top_merchants.map((m, i) => (
              <div key={m.merchant} className="text-dim">
                <span style={{ fontSize: 12 }}>
                  <span className="pigment-dot" style={{ background: 'var(--pig-etsy)', marginRight: 5 }} />
                  #{i + 1} {m.merchant}
                </span>
                <div className="money" style={{ color: 'var(--ink)', fontSize: 17 }}>{fmtMoney(m.total)}</div>
              </div>
            ))}
            {summary.top_merchants.length === 0 && <div className="text-dim">No expense data yet — your feed of receipts is still empty.</div>}
          </div>
        </div>
      </div>
    </div>
  )
}