import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Commission } from '../api'
import { fmtMoney, todayISO } from '../format'

const EMPTY_FORM = {
  client: '',
  piece: '',
  hours: '',
  amount: '',
  expected_date: todayISO(),
  status: 'in_progress',
}

const STATUSES = ['agreed', 'in_progress', 'completed', 'cancelled']

const STATUS_TONE: Record<string, string> = {
  agreed: 'tone-commission',
  in_progress: 'tone-etsy',
  completed: 'tone-other',
  cancelled: '',
}

export function Commissions() {
  const [rows, setRows] = useState<Commission[]>([])
  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const load = async () => {
    try {
      setRows(await api.listCommissions())
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
      hours_spent: Number(form.hours || 0),
      status: form.status,
    }
    if (form.amount) payload.amount = Number(form.amount)
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

  const totalHours = rows.reduce((acc, c) => acc + c.hours_spent, 0)

  return (
    <div className="stack">
      <form className="card" onSubmit={submit}>
        <h3>Log a commission</h3>
        <p className="text-dim" style={{ fontSize: 13, margin: '6px 0 0' }}>
          Track agreed work. Once the client pays, record the income in Slips and link it here — the ledger works out your
          effective hourly rate.
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
              type="number"
              step="0.01"
              min="0"
              value={form.amount}
              onChange={(e) => set('amount', e.target.value)}
              placeholder="0.00"
            />
          </label>
          <label className="field">
            Hours spent
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
            Expected date
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
        {error && <p className="error">{error}</p>}
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
                  <th>Status</th>
                  <th className="num">Agreed</th>
                  <th className="num">Hours</th>
                  <th className="num">$/hr</th>
                  <th>Expected</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id}>
                    <td>{c.client}</td>
                    <td className="text-dim">{c.piece}</td>
                    <td>
                      <span className={`pill ${STATUS_TONE[c.status] ?? ''}`}>{c.status.replace('_', ' ')}</span>
                    </td>
                    <td className="num money">{c.amount !== null ? fmtMoney(c.amount) : '—'}</td>
                    <td className="num text-dim">{c.hours_spent}</td>
                    <td className="num">{c.effective_rate !== null ? fmtMoney(c.effective_rate) : '—'}</td>
                    <td className="text-dim">{c.expected_date ?? '—'}</td>
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
                      No commissions yet — log the piece on your desk right now. Once it&apos;s paid and the hours are
                      in, the ledger tells you what your time was worth.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {rows.some((c) => c.effective_rate !== null) && (
        <div className="card" style={{ borderColor: 'var(--hairline)', borderStyle: 'dashed' }}>
          <h2 className="note-head">Why this matters</h2>
          <p className="text-dim" style={{ fontSize: 13.5, lineHeight: 1.6, margin: '6px 0 0' }}>
            Your effective rate is paid income ÷ hours worked. If a <i>{fmtMoney(500)}</i> portrait took <b>20 h</b>,
            that&apos;s <b>{fmtMoney(25)}/hr</b> — probably below minimum wage. Comparing pieces this way is the fastest
            way to see which work is worth pricing higher.
          </p>
        </div>
      )}
    </div>
  )
}