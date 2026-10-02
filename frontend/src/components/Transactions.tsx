import type { FormEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { Category, Source, Transaction, TransactionCreate } from '../api'
import { fmtMoney, todayISO } from '../format'

const CURRENT_MONTH = todayISO().slice(0, 7)

function monthKey(date: string): string {
  return date.slice(0, 7)
}

function shiftMonth(month: string, amount: number): string {
  const [year, monthNumber] = month.split('-').map(Number)
  const shifted = new Date(year, monthNumber - 1 + amount, 1)
  return `${shifted.getFullYear()}-${String(shifted.getMonth() + 1).padStart(2, '0')}`
}

function formatMonth(month: string): string {
  const [year, monthNumber] = month.split('-').map(Number)
  return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(new Date(year, monthNumber - 1, 1))
}

function lastDayOfMonth(month: string): string {
  const [year, monthNumber] = month.split('-').map(Number)
  return new Date(year, monthNumber, 0).toISOString().slice(0, 10)
}

const PAGE_SIZE = 100

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
  category: 'supplies' as Category,
}

export function Transactions() {
  const [rows, setRows] = useState<Transaction[]>([])
  const [total, setTotal] = useState(0)
  const [selectedMonth, setSelectedMonth] = useState<string>(CURRENT_MONTH)
  const [form, setForm] = useState({ ...EMPTY_FORM })
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [importSummary, setImportSummary] = useState<{created:number; skipped:number; errors:number} | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadMonth = async (month: string, append = false, existing: Transaction[] = []) => {
    if (append) setLoadingMore(true)
    else setLoading(true)
    try {
      const page = await api.listTransactions({
        from_date: `${month}-01`,
        to_date: lastDayOfMonth(month),
        sort: 'date_desc',
        limit: PAGE_SIZE,
        offset: append ? existing.length : 0,
      })
      setRows(append ? [...existing, ...page.items] : page.items)
      setTotal(page.total)
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  useEffect(() => {
    void loadMonth(selectedMonth)
  }, [selectedMonth])

  const loadMore = () => void loadMonth(selectedMonth, true, rows)

  const set = (key: keyof typeof EMPTY_FORM, value: string) => setForm((f) => ({ ...f, [key]: value }))

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    const payload: TransactionCreate = {
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
      const createdMonth = monthKey(form.date)
      if (createdMonth !== selectedMonth) setSelectedMonth(createdMonth)
      else await loadMonth(selectedMonth)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add')
    } finally {
      setSubmitting(false)
    }
  }

  const remove = async (id: number) => {
    try {
      await api.deleteTransaction(id)
      await loadMonth(selectedMonth)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete')
    }
  }

  const exportCsv = async () => {
    try {
      setError('')
      const blob = await api.exportTransactions({
        from_date: `${selectedMonth}-01`,
        to_date: lastDayOfMonth(selectedMonth),
        sort: 'date_desc',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `transactions-${selectedMonth}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
    }
  }

  const triggerImport = () => fileInputRef.current?.click()

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      setError('')
      setSubmitting(true)
      const summary = await api.importTransactions(file)
      setImportSummary({ created: summary.created, skipped: summary.skipped, errors: summary.errors.length })
      await loadMonth(selectedMonth)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed')
    } finally {
      setSubmitting(false)
    }
  }

  const activeMonth = selectedMonth
  const visibleRows = rows

  return (
    <div className="stack">
      <form className="card" onSubmit={submit}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
          <h3>Log a slip</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="button" className="btn-ghost" onClick={triggerImport} disabled={submitting}>Import CSV</button>
            <input ref={fileInputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={handleImport} />
          </div>
        </div>
        {importSummary && (
          <p className="text-dim">Imported {importSummary.created} rows, skipped {importSummary.skipped} {importSummary.errors > 0 ? `with ${importSummary.errors} errors` : ''}.</p>
        )}
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
        <div className="slips-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
          <div>
            <h3>Slips for {formatMonth(activeMonth)}</h3>
            <span className="text-dim">
              {total === 0 ? 'nothing logged' : `${visibleRows.length} of ${total} logged`}
            </span>
          </div>
          <button type="button" className="btn-ghost" onClick={exportCsv}>Export CSV</button>
        </div>
        {loading && <div className="loading">Loading…</div>}
        {!loading && (
          <>
            <div className="table-wrap" style={{ marginTop: 8 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Type</th>
                    <th>Tag</th>
                    <th className="num">Amount</th>
                    <th className="num">Net after fees</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {visibleRows.map((t) => (
                    <tr key={t.id}>
                      <td className="mono datetime">{t.date}</td>
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
                          {t.type === 'income' ? (t.source ?? '').replace('_', ' ') : (t.category ?? '').replace('_', ' ')}
                        </span>
                      </td>
                      <td className="num money">{fmtMoney(t.amount)}</td>
                      <td className="num money text-dim">{fmtMoney(t.net_amount)}</td>
                      <td className="num">
                        <button className="link-danger" onClick={() => void remove(t.id)}>
                          delete
                        </button>
                      </td>
                    </tr>
                  ))}
                  {visibleRows.length === 0 && (
                    <tr>
                      <td colSpan={7} className="text-dim">
                        {`No slips logged in ${formatMonth(activeMonth)}.`}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            {visibleRows.length < total && (
              <button
                type="button"
                className="month-pager-button"
                disabled={loadingMore}
                onClick={loadMore}
                style={{ marginTop: 8 }}
              >
                {loadingMore ? 'Loading…' : `Show more (${total - visibleRows.length} remaining)`}
              </button>
            )}
            <div className="month-pager" aria-label="Slip months">
              <button
                type="button"
                className="month-pager-button"
                aria-label="View earlier month"
                onClick={() => setSelectedMonth(shiftMonth(activeMonth, -1))}
              >
                ← Earlier
              </button>
              <span className="mono month-pager-label">{formatMonth(activeMonth)}</span>
              <button
                type="button"
                className="month-pager-button"
                aria-label="View later month"
                onClick={() => setSelectedMonth(shiftMonth(activeMonth, 1))}
              >
                Later →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}