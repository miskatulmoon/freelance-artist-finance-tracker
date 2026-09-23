import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Source, Transaction } from '../api'
import { fmtMoney, todayISO } from '../format'

const SOURCES: { value: Source; label: string }[] = [
  { value: 'commission', label: 'Commission' },
  { value: 'etsy', label: 'Etsy / shop' },
  { value: 'patreon', label: 'Patreon / Ko-fi' },
  { value: 'other_income', label: 'Other income' },
]

const CATEGORIES: { value: string; label: string }[] = [
  { value: 'supplies', label: 'Supplies' },
  { value: 'platform_fees', label: 'Platform fees' },
  { value: 'subscriptions', label: 'Subscriptions' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'other_expense', label: 'Other' },
]

const SOURCE_TONE: Record<string, string> = {
  commission: 'tone-commission',
  etsy: 'tone-etsy',
  patreon: 'tone-patreon',
  other_income: 'tone-other',
}

const CATEGORY_TONE: Record<string, string> = {
  supplies: 'tone-other',
  platform_fees: 'tone-etsy',
  subscriptions: 'tone-patreon',
  equipment: 'tone-commission',
  other_expense: '',
}

const EMPTY_FORM = {
  type: 'income' as 'income' | 'expense',
  amount: '',
  description: '',
  merchant: '',
  date: todayISO(),
  fee_amount: '',
  source: 'commission' as Source,
  category: 'supplies',
}

export function Transactions() {
  const [rows, setRows] = useState<Transaction[]>([])
  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const load = async () => {
    try {
      setRows(await api.listTransactions())
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
      type: form.type,
      amount: Number(form.amount),
      description: form.description,
      date: form.date,
      merchant: form.merchant || null,
    }
    if (form.fee_amount) payload.fee_amount = Number(form.fee_amount)
    if (form.type === 'income') payload.source = form.source
    else payload.category = form.category
    try {
      await api.createTransaction(payload)
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
      await api.deleteTransaction(id)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete')
    }
  }

  return (
    <div className="stack">
      <form className="card" onSubmit={submit}>
        <h3>Log a slip</h3>
        <div className="form-row" style={{ marginTop: 10 }}>
          <select value={form.type} onChange={(e) => set('type', e.target.value)}>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <label className="field">
            Amount ($)
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              value={form.amount}
              onChange={(e) => set('amount', e.target.value)}
              placeholder="0.00"
            />
          </label>
          <label className="field">
            Description
            <input
              required
              value={form.description}
              onChange={(e) => set('description', e.target.value)}
              placeholder="e.g. yellow commission or marker refill"
            />
          </label>
          <label className="field">
            Merchant (optional)
            <input value={form.merchant} onChange={(e) => set('merchant', e.target.value)} placeholder="Etsy / Blick" />
          </label>
          <label className="field">
            Date
            <input type="date" value={form.date} onChange={(e) => set('date', e.target.value)} />
          </label>
          {form.type === 'income' ? (
            <label className="field">
              Source
              <select value={form.source} onChange={(e) => set('source', e.target.value)}>
                {SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <label className="field">
              Category
              <select value={form.category} onChange={(e) => set('category', e.target.value)}>
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label className="field">
            Fee (optional)
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.fee_amount}
              onChange={(e) => set('fee_amount', e.target.value)}
              placeholder="0.00"
            />
          </label>
          <button className="btn" disabled={submitting} type="submit">
            {submitting ? 'Adding…' : 'Add'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </form>

      <div className="card">
        <h3>All slips</h3>
        {loading && <div className="loading">Loading…</div>}
        {!loading && (
          <div className="table-wrap" style={{ marginTop: 8 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Type</th>
                  <th>Tag</th>
                  <th className="num">Amount</th>
                  <th className="num">Net</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((t) => (
                  <tr key={t.id}>
                    <td className="text-dim">{t.date}</td>
                    <td>
                      {t.description}
                      {t.merchant && <span className="text-dim"> · {t.merchant}</span>}
                      {t.auto_categorized && (
                        <span className="stamp" title="Tagged automatically from your description">
                          auto
                        </span>
                      )}
                    </td>
                    <td>
                      <span className={`pill ${t.type}`}>{t.type}</span>
                    </td>
                    <td>
                      <span className={`pill ${t.type === 'income' ? SOURCE_TONE[t.source ?? ''] ?? '' : CATEGORY_TONE[t.category ?? ''] ?? ''}`}>
                        {t.type === 'income' ? t.source : t.category}
                      </span>
                    </td>
                    <td className={`num ${t.type === 'income' ? 'stat-positive' : 'stat-negative'}`}>
                      {fmtMoney(t.amount)}
                    </td>
                    <td className="num text-dim">{fmtMoney(t.net_amount)}</td>
                    <td className="num">
                      <button className="link-danger" onClick={() => void remove(t.id)}>
                        delete
                      </button>
                    </td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-dim">
                      No slips yet — money in or out, start with today&apos;s. The assistant can tag it for you if you have
                      no idea where it fits.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}