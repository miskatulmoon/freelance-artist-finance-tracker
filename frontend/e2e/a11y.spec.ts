import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('a11y', () => {
  test('landing page has no critical violations', async ({ page }) => {
    await page.goto('/')
    const results = await new AxeBuilder({ page }).analyze()
    expect(results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious')).toEqual([])
  })

  test('dashboard page has no critical violations', async ({ page }) => {
    await page.route('**/api/dashboard/summary**', async route => {
      await route.fulfill({ json: {
        balance: 1000,
        per_source_net: { commission: 500 },
        monthly_trend: [],
        top_merchants: [],
        total_fees: 0,
        hourly_rate: 100
      }})
    })
    await page.route('**/api/cashflow/radar**', async route => {
      await route.fulfill({ json: {
        balance: 1000,
        burn_per_day: 50,
        burn_next_30d: 1500,
        committed_next_30d: 0,
        projected_balance_30d: -500,
        coverage_pct: null,
        level: 'moderate',
        as_of: new Date().toISOString(),
        projection: Array.from({ length: 31 }, (_, i) => ({ day: i, date: new Date().toISOString(), balance: 1000 - i*50 })),
        runway_days: 20,
        projected_zero_date: null
      }})
    })

    await page.goto('/')
    await page.getByRole('button', { name: 'Open your ledger' }).click()
    await page.getByRole('button', { name: 'Ledger' }).click()
    await page.waitForLoadState('networkidle')
    const results = await new AxeBuilder({ page }).exclude('nav.tabbar').analyze()
    expect(results.violations.filter(v => v.impact === 'critical' || v.impact === 'serious')).toEqual([])
  })
})
