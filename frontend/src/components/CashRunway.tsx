import { useState } from 'react'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
  ReferenceDot,
} from 'recharts'
import { fmtMoney, statusClass } from '../format'
import { useDashboard, LEVEL_COLORS, TOOLTIP_STYLE, MONO_TICK, fmtDay } from '../hooks/useDashboard'

function HeroArrow() {
  return (
    <svg width="16" height="8" viewBox="0 0 16 8" aria-hidden="true">
      <path d="M1 4h12.5M13.5 4l-3-3M13.5 4l-3 3" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinecap="round" />
    </svg>
  )
}

export function CashRunway() {
  const { summary, radar, loading } = useDashboard()
  const [heroHover, setHeroHover] = useState(false)

  if (loading || !radar || !summary) return null

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
    <>
      <div className="card hero">
        <div className="hero-copy">
          <div className="hero-head">
            <h3>Cash runway</h3>
            <span className={statusClass(radar.level)}>{radar.level}</span>
          </div>
          <div className="hero-big" style={radar.projected_balance_30d < 0 ? { color: 'var(--tone-commission)' } : undefined}>
            {fmtMoney(radar.projected_balance_30d)}
          </div>
          <div className="hero-path">
            <span className="hero-path-word">today</span>
            <span className="hero-money">{fmtMoney(radar.balance)}</span>
            <span className="hero-arrow"><HeroArrow /></span>
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
          <div className="hero-chart" onMouseEnter={() => setHeroHover(true)} onMouseLeave={() => setHeroHover(false)} onTouchStart={() => setHeroHover(true)} onTouchEnd={() => setHeroHover(false)}>
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
                  cursor={{ stroke: '#d9e2ec', strokeDasharray: '3 3', strokeWidth: 1 }}
                />
                {min < 0 && <ReferenceLine y={0} stroke="#d9e2ec" strokeDasharray="4 4" strokeWidth={1} />}
                <Area type="monotone" dataKey="balance" stroke={levelColor} strokeWidth={1.5} fill="url(#run-wash)" />
                <ReferenceDot x={0} y={vals[0]} r={3.5} fill="#241e16" stroke="#f8fafc" strokeWidth={1.5} />
                <ReferenceDot x={30} y={vals[vals.length - 1]} r={3.5} fill={levelColor} stroke="#f8fafc" strokeWidth={1.5} />
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
          <h3>Effective rate</h3>
          <div className="big">{summary.hourly_rate ? fmtMoney(summary.hourly_rate) : '—'}</div>
          <div className="hint">per hour across commissions</div>
        </div>
        <div className="card">
          <h3>Platform fees paid</h3>
          <div className="big">{fmtMoney(summary.total_fees)}</div>
          <div className="hint">Etsy, payment processors</div>
        </div>
      </div>

      <div className="card">
        <h3>Top merchants</h3>
        <div className="grid cols-3" style={{ marginTop: 10 }}>
          {summary.top_merchants.map((m, i) => (
            <div key={m.merchant} className="text-dim">
              <span style={{ fontSize: 11 }}>#{i + 1} {m.merchant}</span>
              <div className="money" style={{ color: 'var(--ink)', fontSize: 18 }}>{fmtMoney(m.total)}</div>
            </div>
          ))}
          {summary.top_merchants.length === 0 && <div className="text-dim">No expense data yet — your feed of receipts is still empty.</div>}
        </div>
      </div>
    </>
  )
}
