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

import type { components, operations } from './types/api'

type Schemas = components['schemas']
type OperationResponse<
  Operation extends keyof operations,
  Status extends keyof operations[Operation]['responses'],
> = operations[Operation]['responses'][Status] extends { content: { 'application/json': infer Response } }
  ? Response
  : never

export type Source = Schemas['Source']
export type Category = Schemas['Category']
export type TxType = Schemas['TransactionCreate']['type']
export type TransactionCreate = Schemas['TransactionCreate']
export type TransactionUpdate = Schemas['TransactionUpdate']
export type Transaction = Schemas['TransactionRead']
export type CommissionCreate = Schemas['CommissionCreate']
export type CommissionStatus = Schemas['CommissionStatus']
export type Commission = Schemas['CommissionRead']
export type CommissionSummary = Schemas['CommissionSummary']
export type Summary = Schemas['DashboardSummary']
export type RadarPoint = Schemas['RadarPoint']
export type CashflowRadar = Schemas['CashflowRadarRead']
export type Insights = Schemas['InsightsResponse']
export type ChatAnswer = Schemas['ChatResponse']
export type CashflowInsights = Schemas['CashflowInsightsResponse']

export async function streamChat(question: string, onDelta: (text: string) => void): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
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
  const reader = res.body?.getReader()
  if (!reader) throw new Error('Streaming is not supported in this browser')
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) return
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const event of events) {
      const line = event.trim()
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6)
      if (data === '[DONE]') return
      try {
        const payload = JSON.parse(data) as { delta?: string }
        if (payload.delta) onDelta(payload.delta)
      } catch {
        /* ignore malformed chunk */
      }
    }
  }
}

export const api = {
  getSummary: () => request<OperationResponse<'dashboard_summary_dashboard_summary_get', 200>>('/dashboard/summary'),
  getInsights: () => request<OperationResponse<'dashboard_insights_dashboard_insights_post', 200>>('/dashboard/insights', { method: 'POST' }),
  getRadar: () => request<OperationResponse<'cashflow_radar_endpoint_cashflow_radar_get', 200>>('/cashflow/radar'),
  getRadarNarrative: () =>
    request<OperationResponse<'cashflow_insights_cashflow_radar_insights_post', 200>>('/cashflow/radar/insights', {
      method: 'POST',
    }),
  chat: (question: string) => request<OperationResponse<'chat_chat_post', 200>>('/chat', {
    method: 'POST',
    body: JSON.stringify({ question }),
  }),
  streamChat,

  listTransactions: () => request<OperationResponse<'list_transactions_transactions_get', 200>>('/transactions'),
  createTransaction: (body: TransactionCreate) =>
    request<OperationResponse<'create_transaction_transactions_post', 201>>('/transactions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateTransaction: (id: number, body: TransactionUpdate) =>
    request<OperationResponse<'update_transaction_transactions__transaction_id__patch', 200>>(`/transactions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  deleteTransaction: (id: number) => request<void>(`/transactions/${id}`, { method: 'DELETE' }),

  listCommissions: () => request<OperationResponse<'list_commissions_commissions_get', 200>>('/commissions'),
  getCommissionSummary: () =>
    request<OperationResponse<'commissions_summary_commissions_summary_get', 200>>('/commissions/summary'),
  createCommission: (body: CommissionCreate) =>
    request<OperationResponse<'create_commission_commissions_post', 201>>('/commissions', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateCommissionStatus: (id: number, status: CommissionStatus) =>
    request<OperationResponse<'update_commission_commissions__commission_id__patch', 200>>(`/commissions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  deleteCommission: (id: number) => request<void>(`/commissions/${id}`, { method: 'DELETE' }),
}