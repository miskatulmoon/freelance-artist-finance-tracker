export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = Array.isArray(body.detail) ? body.detail.map((d: { msg: string }) => d.msg).join(', ') : body.detail
    } catch {
      /* keep fallback */
    }
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export type Source = 'commission' | 'etsy' | 'patreon' | 'other_income'
export type Category = 'supplies' | 'platform_fees' | 'subscriptions' | 'equipment' | 'other_expense'
export type TxType = 'income' | 'expense'

export interface Transaction {
  id: number
  type: TxType
  amount: number
  net_amount: number
  description: string
  date: string
  fee_amount: number | null
  source: Source | null
  category: Category | null
  merchant: string | null
  auto_categorized: boolean
}

export interface Commission {
  id: number
  client: string
  piece: string
  hours_spent: number
  amount: number | null
  expected_date: string | null
  status: string
  transaction_id: number | null
  effective_rate: number | null
}

export interface Summary {
  balance: number
  per_source_net: Record<Source, number>
  monthly_trend: { month: string; income: number; expense: number; net: number }[]
  top_merchants: { merchant: string; total: number }[]
  total_fees: number
  hourly_rate: number | null
}

export interface RadarPoint {
  day: number
  date: string
  balance: number
}

export interface CashflowRadar {
  balance: number
  burn_per_day: number
  burn_next_30d: number
  committed_next_30d: number
  projected_balance_30d: number
  coverage_pct: number | null
  level: 'healthy' | 'moderate' | 'low' | 'unknown'
  as_of: string
  projection: RadarPoint[]
  runway_days: number | null
  projected_zero_date: string | null
}

export const api = {
  getSummary: () => request<Summary>('/dashboard/summary'),
  getInsights: () => request<{ insights: string }>('/dashboard/insights', { method: 'POST' }),
  getRadar: () => request<CashflowRadar>('/cashflow/radar'),
  getRadarNarrative: () => request<{ radar: CashflowRadar; narrative: string }>('/cashflow/radar/insights', { method: 'POST' }),
  chat: (question: string) => request<{ answer: string }>('/chat', { method: 'POST', body: JSON.stringify({ question }) }),

  listTransactions: () => request<Transaction[]>('/transactions'),
  createTransaction: (body: Record<string, unknown>) =>
    request<Transaction>('/transactions', { method: 'POST', body: JSON.stringify(body) }),
  updateTransaction: (id: number, body: Record<string, unknown>) =>
    request<Transaction>(`/transactions/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteTransaction: (id: number) => request<void>(`/transactions/${id}`, { method: 'DELETE' }),

  listCommissions: () => request<Commission[]>('/commissions'),
  createCommission: (body: Record<string, unknown>) =>
    request<Commission>('/commissions', { method: 'POST', body: JSON.stringify(body) }),
  deleteCommission: (id: number) => request<void>(`/commissions/${id}`, { method: 'DELETE' }),
}