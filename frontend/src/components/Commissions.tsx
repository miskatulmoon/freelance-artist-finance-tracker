import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Commission, CommissionSummary } from '../api'
import { fmtMoney, todayISO } from '../format'

const EMPTY_FORM = {
  client: '',
  piece: '',
  amount: '',
  hours: '',
  expected_date: todayISO(),
  status: 'in_progress',
}

const STATUSES = ['agreed', 'in_progress', 'completed', 'cancelled']

const SUMMARY_HINTS = {
  expected: 'agreed or in progress',
  earned: 'finished pieces, already in the ledger',
  lost: 'cancelled pieces',
}

export function Commissions() {
  const [rows, setRows] = useState<Commission[]>([])
  const [summary, setSummary] = useState<CommissionSummary | null>(null)
  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const load = async () => {
    try {
      const [commissions, commissionSummary] = await Promise.all([
        api.listCommissions(),
        api.getCommissionSummary(),
      ])
      setRows(commissions)
      setSummary(commissionSummary)
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const set = (key: keyof typeof EMPTY_FORM, value: string) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    const payload: Record<string, unknown> = {
      client: form.client,
      piece: form.piece,
      amount: Number(form.amount),
      hours_spent: Number(form.hours || 0),
      status: form.status,
    }
    if (form.expected_date) payload.expected_date = form.expected_date
    try {
      await api.createCommission(payload)
      setForm({ ...EMPTY_FORM })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add')
    } finally {
      setSubmitting(false)
    }
  }

  const remove = async (id: number) => {
    try {
      await api.deleteCommission(id)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete')
    }
  }

  const setStatus = async (id: number, status: string) => {
    setError('')
    const prev = rows.find((r) => r.id === id)?.status
    setRows((rs) => rs.map((c) => (c.id === id ? { ...c, status } : c)))
    try {
      await api.updateCommissionStatus(id, status)
      await load()
    } catch (err) {
      setRows((rs) => rs.map((c) => (c.id === id && prev ? { ...c, status: prev } : c)))
      setError(err instanceof Error ? err.message : 'Failed to update status')
    }
  }

  const totalHours = rows.reduce((acc, c) => acc + c.hours_spent, 0)
  const activeCount = summary ? summary.counts.agreed + summary.counts.in_progress : 0

  return (
    <div className="stack">
      {summary && rows.length > 0 && (
        <div className="grid cols-3">
          <div className="card">
            <h3>
              <span className="card-head-dot">
                <span className="pigment-dot" style={{ background: 'var(--pig-spend)' }} />
                Expected income
              </span>
            </h3>
            <div className="big">{fmtMoney(summary.expected_income)}</div>
            <div className="hint">
              {activeCount} {activeCount === 1 ? 'piece' : 'pieces'} {SUMMARY_HINTS.expected}
            </div>
          </div>
          <div className="card">
            <h3>
              <span className="card-head-dot">
                <span className="pigment-dot" style={{ background: 'var(--pig-other)' }} />
                Earned income
              </span>
            </h3>
            <div className="big">{fmtMoney(summary.earned_income)}</div>
            <div className="hint">{SUMMARY_HINTS.earned}</div>
          </div>
          <div className="card">
            <h3>
              <span className="card-head-dot">
                <span className="pigment-dot" style={{ background: 'var(--pig-commission)' }} />
                Lost income
              </span>
            </h3>
            <div className="big">{fmtMoney(summary.lost_income)}</div>
            <div className="hint">{SUMMARY_HINTS.lost}</div>
          </div>
        </div>
      )}

      <form className="card" onSubmit={submit}>
        <h3>Log a commission</h3>
        <p className="text-dim" style={{ fontSize: 13, margin: '6px 0 0' }}>
          The terms — client, price, hours, and due date — lock in here. From then on you only move its
          status: marking a piece completed writes its income slip into the ledger for you.
        </p>
        <div className="form-row" style={{ marginTop: 12 }}>
          <label className="field">
            Client
            <input required value={form.client} onChange={(e) => set('client', e.target.value)} placeholder="who" />
          </label>
          <label className="field">
            Piece
            <input required value={form.piece} onChange={(e) => set('piece', e.target.value)} placeholder="what" />
          </label>
          <label className="field">
            Agreed price ($)
            <input
              required
              type="number"
              step="0.01"
              min="0"
              value={form.amount}
              onChange={(e) => set('amount', e.target.value)}
              placeholder="0.00"
            />
          </label>
          <label className="field">
            Agreed hours
            <input
              type="number"
              step="0.5"
              min="0"
              value={form.hours}
              onChange={(e) => set('hours', e.target.value)}
              placeholder="0"
            />
          </label>
          <label className="field">
            Due date
            <input type="date" value={form.expected_date} onChange={(e) => set('expected_date', e.target.value)} />
          </label>
          <label className="field">
            Status
            <select value={form.status} onChange={(e) => set('status', e.target.value)}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          </label>
          <button className="btn" disabled={submitting} type="submit">
            {submitting ? 'Adding…' : 'Add'}
          </button>
        </div>
        {error && <p className="error" style={{ marginTop: 10 }}>{error}</p>}
      </form>

      <div className="card">
        <h3>
          Commissions <span className="text-dim">· {totalHours} hrs logged</span>
        </h3>
        {loading && <div className="loading">Loading…</div>}
        {!loading && (
          <div className="table-wrap" style={{ marginTop: 8 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Piece</th>
                  <th>Progress</th>
                  <th className="num">Agreed</th>
                  <th className="num">Hours</th>
                  <th className="num">$/hr</th>
                  <th>Due</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: 500 }}>{c.client}</td>
                    <td className="text-dim">{c.piece}</td>
                    <td>
                      <span className="status-wrap">
                        <select
                          className={`badge badge-${c.status} status-control`}
                          value={c.status}
                          onChange={(e) => void setStatus(c.id, e.target.value)}
                          aria-label={`Progress for ${c.client} — ${c.piece}`}
                        >
                          {STATUSES.map((s) => (
                            <option key={s} value={s}>
                              {s.replace('_', ' ')}
                            </option>
                          ))}
                        </select>
                        <svg
                          className="status-chevron"
                          width="8"
                          height="5"
                          viewBox="0 0 8 5"
                          aria-hidden="true"
                        >
                          <path
                            d="M1 1l3 3 3-3"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.4"
                            strokeLinecap="round"
                          />
                        </svg>
                      </span>
                      {c.income_autologged && (
                        <span className="stamp" title="Income recorded in Slips when you marked this piece completed">
                          logged
                        </span>
                      )}
                    </td>
                    <td className="num money">{fmtMoney(c.amount)}</td>
                    <td className="num mono-num text-dim">{c.hours_spent}</td>
                    <td className="num mono-num">{c.effective_rate !== null ? fmtMoney(c.effective_rate) : '—'}</td>
                    <td className="mono datetime">{c.expected_date ?? '—'}</td>
                    <td className="num">
                      <button className="link-danger" onClick={() => void remove(c.id)}>
                        delete
                      </button>
                    </td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={8} className="text-dim">
                      No commissions yet — log the piece on your desk right now. Move its status as the work
                      moves; when you mark it completed, the ledger records the income and works out what your
                      time was worth.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {rows.some((c) => c.effective_rate !== null) && (
        <div className="why-note">
          <h2 className="why-title">Why this matters</h2>
          <p className="why-copy">
            Your effective rate is paid income ÷ hours worked. If a <i>{fmtMoney(500)}</i> portrait took{' '}
            <strong>20 h</strong>, that's <strong>{fmtMoney(25)}/hr</strong> — probably below minimum wage.
            Comparing pieces this way is the fastest way to see which work is worth pricing higher.
          </p>
        </div>
      )}
    </div>
  )
}
