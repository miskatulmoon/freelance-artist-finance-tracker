import { useEffect, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../api'
import type { CashflowRadar, Summary } from '../api'
import { fmtMonth, fmtMoney, statusClass } from '../format'
import ledgerTexture from '../assets/wesley-tingey-XvlbhiTzfWA-unsplash.jpg'

const SOURCE_COLORS: Record<string, string> = {
  commission: '#a84b2f',
  etsy: '#a8833a',
  patreon: '#8a6070',
  other_income: '#546b57',
}

const LEVEL_COLORS: Record<CashflowRadar['level'], string> = {
  healthy: '#546b57',
  moderate: '#a8833a',
  low: '#a84b2f',
  unknown: '#6f6350',
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

function HeroArrow() {
  return (
    <svg width="16" height="8" viewBox="0 0 16 8" aria-hidden="true">
      <path d="M1 4h12.5M13.5 4l-3-3M13.5 4l-3 3" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinecap="round" />
    </svg>
  )
}

function fmtDay(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
  const { summary, radar, loading, error } = useDashboard()
  const [heroHover, setHeroHover] = useState(false)

  if (loading) return <DashboardSkeleton />
  if (error || !summary || !radar) return <div className="error">{error || 'No data'}</div>

  const sources = Object.entries(summary.per_source_net).map(([name, net]) => ({
    name: name.replace('_', ' '),
    net,
    color: SOURCE_COLORS[name] ?? '#5c5044',
  }))

  const top = sources.length ? sources.reduce((a, b) => (b.net > a.net ? b : a)) : null

  const levelColor = LEVEL_COLORS[radar.level]
  const vals = radar.projection.length ? radar.projection.map((p) => p.balance) : [0]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const spread = max - min
  const pad = spread * 0.1 || Math.max(Math.abs(max), 1) * 0.1
  const yDomain: [number, number] = spread <= 0.01 && min >= 0 ? [0, (max || 1) * 1.25] : [min - pad, max + pad]

  const showChart = radar.balance !== 0 || radar.burn_next_30d > 0 || radar.committed_next_30d > 0

  const fmtAxis = (v: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(v)

  return (
    <div className="stack">
      <div className="card hero">
        <div className="hero-copy">
          <div className="hero-head">
            <h3>Cash runway</h3>
            <span className={statusClass(radar.level)}>{radar.level}</span>
          </div>
          <div
            className="hero-big"
            style={radar.projected_balance_30d < 0 ? { color: 'var(--tone-commission)' } : undefined}
          >
            {fmtMoney(radar.projected_balance_30d)}
          </div>
          <div className="hero-path">
            <span className="hero-path-word">today</span>
            <span className="hero-money">{fmtMoney(radar.balance)}</span>
            <span className="hero-arrow">
              <HeroArrow />
            </span>
            <span className="hero-path-word">+30 days</span>
            <span className="hero-money">{fmtMoney(radar.projected_balance_30d)}</span>
          </div>

          <div className="hero-subfigs">
            <div>
              <div className="text-dim">Committed income</div>
              <div className="hero-subfig-num">{fmtMoney(radar.committed_next_30d)}</div>
            </div>
            <div>
              <div className="text-dim">Projected spend</div>
              <div className="hero-subfig-num">
                {fmtMoney(radar.burn_next_30d)}
                {radar.burn_per_day > 0 && <span className="hero-subfig-mono"> {fmtMoney(radar.burn_per_day)}/day</span>}
              </div>
            </div>
            <div>
              <div className="text-dim">Days covered</div>
              <div className="hero-subfig-mono-num">
                {radar.runway_days !== null ? `~${Math.round(radar.runway_days)} days` : '—'}
              </div>
            </div>
          </div>

          <p className="hero-note">
            {radar.level === 'unknown' && 'Add a few slips to unlock the forecast.'}
            {radar.level === 'healthy' && 'Covered through the month.'}
            {radar.level === 'moderate' && 'Tight, but covered month-end.'}
            {radar.level === 'low' && (
              <>
                Projected to{' '}
                <span className="hero-note-warn">{fmtMoney(radar.projected_balance_30d)}</span> in 30 days — line up
                income before {radar.projected_zero_date ? fmtDay(radar.projected_zero_date) : 'the month is out'}.
              </>
            )}
          </p>
        </div>

        {showChart && (
          <div
            className="hero-chart"
            onMouseEnter={() => setHeroHover(true)}
            onMouseLeave={() => setHeroHover(false)}
            onTouchStart={() => setHeroHover(true)}
            onTouchEnd={() => setHeroHover(false)}
          >
            <ResponsiveContainer width="100%" height={150}>
              <AreaChart data={radar.projection} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="run-wash" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={levelColor} stopOpacity={0.22} />
                    <stop offset="100%" stopColor={levelColor} stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" type="number" domain={[0, 30]} hide />
                <YAxis tick={MONO_TICK} tickFormatter={fmtAxis} axisLine={false} tickLine={false} width={44} domain={yDomain} />
                <Tooltip
                  active={heroHover}
                  labelFormatter={(label, payload) => {
                    const datum = (payload?.[0]?.payload ?? {}) as { date?: string }
                    return datum.date ? fmtDay(datum.date) : String(label)
                  }}
                  formatter={(value) => [fmtMoney(Number(value)), 'Balance']}
                  contentStyle={TOOLTIP_STYLE}
                  labelStyle={{ fontFamily: "'DM Mono', monospace", fontSize: 10, letterSpacing: '0.06em', color: '#6f6350' }}
                  cursor={{ stroke: '#d4c9b8', strokeDasharray: '3 3', strokeWidth: 1 }}
                />
                {min < 0 && <ReferenceLine y={0} stroke="#d4c9b8" strokeDasharray="4 4" strokeWidth={1} />}
                <Area type="monotone" dataKey="balance" stroke={levelColor} strokeWidth={1.5} fill="url(#run-wash)" />
                <ReferenceDot x={0} y={vals[0]} r={3.5} fill="#241e16" stroke="#f6f2ec" strokeWidth={1.5} />
                <ReferenceDot x={30} y={vals[vals.length - 1]} r={3.5} fill={levelColor} stroke="#f6f2ec" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
            <div className="hero-legend" aria-hidden="true">
              <span className="hero-legend-item">
                <i className="hero-legend-dot" style={{ background: '#241e16' }} />
                today
              </span>
              <span className="hero-legend-item">
                <i className="hero-legend-dot" style={{ background: levelColor }} />
                in 30 days
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="grid cols-2">
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
      </div>

      <div className="dashboard-art" aria-hidden="true">
        <img src={ledgerTexture} alt="" />
        <span>your studio, in colour</span>
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
  )
}