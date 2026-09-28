import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import { Dashboard } from './Dashboard'

// Mock useDashboard hook
vi.mock('../hooks/useDashboard', () => ({
  useDashboard: () => ({
    summary: {
      per_source_net: {},
      monthly_trend: [],
      top_merchants: [],
      total_fees: 0,
      hourly_rate: null,
    },
    radar: { level: 'unknown' },
    loading: false,
    error: '',
    isError: false,
    reload: vi.fn(),
  }),
}))

describe('Dashboard', () => {
  it('shows empty state when no data', async () => {
    const queryClient = new QueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    )
    expect(await screen.findByText(/Your ledger is empty/i)).toBeInTheDocument()
  })
})
