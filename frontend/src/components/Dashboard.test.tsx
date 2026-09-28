import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import { Dashboard } from './Dashboard'

// Mock useDashboard hook
vi.mock('../hooks/useDashboard', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../hooks/useDashboard')>()

  return {
    ...actual,
    useDashboard: () => ({
      summary: {
        per_source_net: {},
        monthly_trend: [],
        top_merchants: [],
        total_fees: 0,
        hourly_rate: null,
      },
      radar: {
        level: 'unknown',
        balance: 0,
        burn_per_day: 0,
        burn_next_30d: 0,
        committed_next_30d: 0,
        projected_balance_30d: 0,
        coverage_pct: null,
        as_of: '2025-01-01',
        projection: [],
        runway_days: null,
        projected_zero_date: null,
      },
      loading: false,
      error: '',
      isError: false,
      reload: vi.fn(),
    }),
  }
})

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
