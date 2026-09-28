import { expect, test } from '@playwright/test'

test('commission agreed → completed autologs income', async ({ page }) => {
  let commissions: any[] = [
    {
      id: 1,
      piece: 'Portrait',
      client: 'Acme',
      amount: 500,
      hours_spent: 5,
      expected_date: '2025-12-01',
      status: 'agreed',
      transaction_id: null,
      income_autologged: false,
      effective_rate: 100,
    },
  ]
  let transactions: any[] = []

  await page.route('**/api/commissions**', async (route) => {
    const req = route.request()
    if (req.method() === 'GET') {
      if (new URL(req.url()).pathname.endsWith('/summary')) {
        await route.fulfill({
          json: {
            expected_income: 500,
            earned_income: 0,
            lost_income: 0,
            counts: { agreed: 1, in_progress: 0, completed: 0, cancelled: 0 },
            active_count: 1,
          },
        })
        return
      }
      await route.fulfill({ json: { items: commissions, total: commissions.length, limit: 100, offset: 0 } })
      return
    }
    if (req.method() === 'PATCH') {
      const body = req.postDataJSON()
      const id = Number(req.url().split('/').pop())
      const idx = commissions.findIndex(c => c.id === id)
      if (idx >= 0) {
        commissions[idx] = { ...commissions[idx], status: body.status }
        if (body.status === 'completed' && !transactions.find(t => t.commission_id === id)) {
          transactions.push({
            id: 100 + id,
            type: 'income',
            amount: commissions[idx].amount,
            net_amount: commissions[idx].amount,
            description: `Commission completed: ${commissions[idx].piece}`,
            date: new Date().toISOString().slice(0,10),
            fee_amount: null,
            source: 'commission',
            category: 'income',
            merchant: commissions[idx].client,
            auto_categorized: false,
            commission_id: id
          })
        }
      }
      await route.fulfill({ json: commissions[idx] })
      return
    }
    await route.continue()
  })

  await page.route('**/api/transactions**', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ json: { items: transactions, total: transactions.length, limit: 100, offset: 0 } })
      return
    }
    await route.continue()
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'Open your ledger' }).click()
  await page.getByRole('button', { name: 'Commissions' }).click()

  await expect(page.getByRole('heading', { name: 'Commissions', exact: true })).toBeVisible()
  await expect(page.getByRole('cell', { name: 'Portrait', exact: true })).toBeVisible()

  // Change status to completed
  const statusControl = page.getByLabel('Progress for Acme — Portrait')
  await statusControl.selectOption('completed')

  // Verify autologged income appears in Slips
  await page.getByRole('button', { name: 'Slips' }).click()
  await expect(page.getByRole('heading', { name: 'Slips', exact: true })).toBeVisible()
  await expect(page.getByText('Commission completed: Portrait')).toBeVisible()
  await expect(page.getByText('$500.00').first()).toBeVisible()
})
