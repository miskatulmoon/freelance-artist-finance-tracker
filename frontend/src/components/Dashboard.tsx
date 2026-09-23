import { useEffect, useState } from 'react'
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'
import type { CashflowRadar, Summary } from '../api'
import { fmtMonth, fmtMoney, statusClass } from '../format'

const SOURCE_COLORS: Record<string, string> = {
  commission: '#a84b2f',
  etsy: '#a8833a',
  patreon: '#8a6070',
  other_income: '#546b57',
}

const WASH = {
  commission: '#a84b2f',
  etsy: '#a8833a',
  patreon: '#8a6070',
  other_income: '#546b57',
  income: '#a8833a',
  expense: '#5a6b96',
} as const

const TOOLTIP_STYLE = {
  background: '#f6f2ec',
  border: '1px solid #d4c9b8',
  borderRadius: 4,
  color: '#241e16',
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 12,
}

const LABEL_TICK = { fontFamily: "'Fraunces', Georgia, serif", fontSize: 11, fontStyle: 'italic' as const, fill: '#6f6350' }
const MONO_TICK = { fontFamily: "'DM Mono', monospace", fontSize: 10, fill: '#6f6350' }

function WashDefs() {
  return (
    <defs>
      {Object.entries(WASH).map(([key, color]) => (
        <linearGradient key={key} id={`wash-${key}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.9} />
          <stop offset="100%" stopColor={color} stopOpacity={0.45} />
        </linearGradient>
      ))}
    </defs>
  )
}

function LedgerLegend() {
  return (
    <div className="marg-note" style={{ gap: 16, marginTop: 8, padding: 0 }} aria-hidden="true">
      {[
        { color: '#a8833a', label: 'income' },
        { color: '#5a6b96', label: 'expense' },
      ].map((l) => (
        <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <span style={{ width: 14, height: 3, borderRadius: 1, background: l.color, display: 'inline-block' }} />
          <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: '#6f6350', letterSpacing: '0.06em' }}>
            {l.label}
          </span>
        </div>
      ))}
    </div>
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
            <div className="sk-block" style={{ width: '100%', height: 236 }} />
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
    color: SOURCE_COLORS[name] ?? '#5c5044',
  }))

  const top = sources.length ? sources.reduce((a, b) => (b.net > a.net ? b : a)) : null

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
              <span className="pigment-dot" style={{ background: 'var(--pig-spend)' }} />
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
          <ResponsiveContainer width="100%" height={188}>
            <BarChart data={sources} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barSize={40}>
              <XAxis dataKey="name" tick={LABEL_TICK} axisLine={false} tickLine={false} />
              <YAxis tick={MONO_TICK} axisLine={false} tickLine={false} width={38} />
              <Tooltip
                formatter={(v) => [fmtMoney(Number(v)), 'Net']}
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ fontWeight: 600 }}
                cursor={{ fill: '#e0d9ce' }}
              />
              <WashDefs />
              <Bar dataKey="net" radius={[2, 2, 0, 0]}>
                {sources.map((s) => (
                  <Cell key={s.name} fill={`url(#wash-${s.name.replace(' ', '_')})`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Monthly trend</h3>
          <ResponsiveContainer width="100%" height={188}>
            <BarChart data={summary.monthly_trend} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barSize={14} barCategoryGap="30%">
              <XAxis
                dataKey="month"
                tick={LABEL_TICK}
                axisLine={false}
                tickLine={false}
                tickFormatter={fmtMonth}
              />
              <YAxis tick={MONO_TICK} axisLine={false} tickLine={false} width={38} />
              <Tooltip
                formatter={(v, n) => [fmtMoney(Number(v)), String(n)]}
                contentStyle={TOOLTIP_STYLE}
                labelStyle={{ fontWeight: 600 }}
                cursor={{ fill: '#e0d9ce' }}
              />
              <WashDefs />
              <Bar dataKey="income" fill="url(#wash-income)" radius={[2, 2, 0, 0]} />
              <Bar dataKey="expense" fill="url(#wash-expense)" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <LedgerLegend />
        </div>
      </div>

      {top && (
        <div className="marg-note">
          <span className="marg-note-glyph">✦</span>
          <p className="marg-note-copy">
            {top.name.charAt(0).toUpperCase() + top.name.slice(1)} is your strongest source on record —{' '}
            {fmtMoney(top.net)} net, after fees.
          </p>
        </div>
      )}

      <div className="grid cols-2">
        <div className="card">
          <h3>Cash-flow · next 30 days</h3>
          <div className="grid cols-2" style={{ marginTop: 10, gap: 12 }}>
            <div>
              <div className="text-dim" style={{ fontSize: 11 }}>Committed income</div>
              <div className="money" style={{ fontSize: 20 }}>{fmtMoney(radar.committed_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 11 }}>Projected spend</div>
              <div className="money" style={{ fontSize: 20 }}>{fmtMoney(radar.burn_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 11 }}>Projected balance</div>
              <div className="money" style={{ fontSize: 20 }}>{fmtMoney(radar.projected_balance_30d)}</div>
            </div>
            <div>
              <div className="text-dim" style={{ fontSize: 11 }}>Burn rate</div>
              <div className="money" style={{ fontSize: 20 }}>
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
                <span style={{ fontSize: 11 }}>
                  <span className="pigment-dot" style={{ background: 'var(--pig-other)', marginRight: 5 }} />
                  #{i + 1} {m.merchant}
                </span>
                <div className="money" style={{ color: 'var(--ink)', fontSize: 18 }}>{fmtMoney(m.total)}</div>
              </div>
            ))}
            {summary.top_merchants.length === 0 && <div className="text-dim">No expense data yet — your feed of receipts is still empty.</div>}
          </div>
        </div>
      </div>
    </div>
  )
}