import { useQuery } from '@tanstack/react-query'
import { api } from '../api'
import type { CashflowRadar } from '../api'

export const SOURCE_COLORS: Record<string, string> = {
  commission: '#a84b2f',
  etsy: '#a8833a',
  patreon: '#8a6070',
  other_income: '#546b57',
}

export const LEVEL_COLORS: Record<CashflowRadar['level'], string> = {
  healthy: '#546b57',
  moderate: '#a8833a',
  low: '#a84b2f',
  unknown: '#6f6350',
}

export const WASH = {
  commission: '#a84b2f',
  etsy: '#a8833a',
  patreon: '#8a6070',
  other_income: '#546b57',
  income: '#a8833a',
  expense: '#5a6b96',
} as const

export const TOOLTIP_STYLE = {
  background: '#f8fafc',
  border: '1px solid #d9e2ec',
  borderRadius: 4,
  color: '#241e16',
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 12,
}

export const LABEL_TICK = { fontFamily: "'Fraunces', Georgia, serif", fontSize: 11, fontStyle: 'italic' as const, fill: '#6f6350' }
export const MONO_TICK = { fontFamily: "'DM Mono', monospace", fontSize: 10, fill: '#6f6350' }

export function fmtDay(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function useDashboard() {
  const query = useQuery({
    queryKey: ['dashboard', 'summary', 'radar'],
    queryFn: async () => {
      const [summary, radar] = await Promise.all([api.getSummary(), api.getRadar()])
      return { summary, radar }
    },
    staleTime: 1000 * 60 * 5,
    retry: 2,
  })

  return {
    summary: query.data?.summary ?? null,
    radar: query.data?.radar ?? null,
    loading: query.isPending,
    error: query.error?.message ?? '',
    isError: query.isError,
    reload: query.refetch,
  }
}
