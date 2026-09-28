import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { fmtMoney, fmtMonth } from '../format'
import { useDashboard, SOURCE_COLORS, TOOLTIP_STYLE, LABEL_TICK, MONO_TICK, WASH } from '../hooks/useDashboard'

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

export function TrendCharts() {
  const { summary } = useDashboard()
  if (!summary) return null

  const sources = Object.entries(summary.per_source_net).map(([name, net]) => ({
    name: name.replace('_', ' '),
    net,
    color: SOURCE_COLORS[name] ?? '#5c5044',
  }))

  const top = sources.length ? sources.reduce((a, b) => (b.net > a.net ? b : a)) : null

  return (
    <>
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
                cursor={{ fill: '#eef3f8' }}
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
                cursor={{ fill: '#eef3f8' }}
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
    </>
  )
}
