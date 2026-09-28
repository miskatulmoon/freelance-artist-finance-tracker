import { expect, test } from '@playwright/test'

test('commission agreed → completed autologs income', async ({ page }) => {
  let commissions: any[] = [
    { id: 1, title: 'Portrait', client: 'Acme', price: 500, hours: 5, due_date: '2025-12-01', status: 'agreed' }
  ]
  let transactions: any[] = []

  await page.route('**/api/commissions**', async (route) => {
    const req = route.request()
    if (req.method() === 'GET') {
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
            amount: commissions[idx].price,
            net_amount: commissions[idx].price,
            description: `Commission completed: ${commissions[idx].title}`,
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

  await expect(page.getByRole('heading', { name: 'Commissions' })).toBeVisible()
  await expect(page.getByText('Portrait')).toBeVisible()

  // Change status to completed
  const statusControl = page.locator('[data-testid="commission-status-1"]')
  await statusControl.click()
  await page.getByRole('option', { name: 'completed' }).click()

  // Verify autologged income appears in Slips
  await page.getByRole('button', { name: 'Slips' }).click()
  await expect(page.getByRole('heading', { name: 'Slips' })).toBeVisible()
  await expect(page.getByText('Commission completed: Portrait')).toBeVisible()
  await expect(page.getByText('$500.00')).toBeVisible()
})
