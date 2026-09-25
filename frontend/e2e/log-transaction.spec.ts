import { expect, test } from '@playwright/test'

test('logs an income transaction from the slips page', async ({ page }) => {
  let transactions = []

  await page.route('**/api/transactions', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ json: transactions })
      return
    }
    const body = route.request().postDataJSON()
    const created = {
      id: 1,
      type: body.type,
      amount: body.amount,
      net_amount: body.amount,
      description: body.description,
      date: body.date,
      fee_amount: body.fee_amount ?? null,
      source: body.source ?? null,
      category: body.category ?? null,
      merchant: body.merchant ?? null,
      auto_categorized: false,
    }
    transactions = [created]
    await route.fulfill({ status: 201, json: created })
  })

  await page.goto('/')
  await page.getByRole('button', { name: 'Open your ledger' }).click()
  await page.getByRole('button', { name: 'Slips' }).click()

  await expect(page.getByRole('heading', { name: 'Slips', exact: true })).toBeVisible()
  await page.getByLabel('Amount ($)').fill('125.50')
  await page.getByLabel('Description').fill('Portrait deposit')
  await page.getByRole('button', { name: 'Add' }).click()

  const createdRow = page.getByRole('row').filter({ hasText: 'Portrait deposit' })
  await expect(createdRow).toBeVisible()
  await expect(createdRow.getByText('$125.50', { exact: true }).first()).toBeVisible()
})
