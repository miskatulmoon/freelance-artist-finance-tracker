import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Transactions } from './Transactions'
import { api } from '../api'

vi.mock('../api', () => ({
  api: {
    listTransactions: vi.fn(),
    createTransaction: vi.fn(),
    deleteTransaction: vi.fn(),
  },
}))

const mockedApi = vi.mocked(api)

function fillRequiredFields() {
  fireEvent.change(screen.getByLabelText('Amount ($)'), { target: { value: '125.50' } })
  fireEvent.change(screen.getByLabelText('Description'), { target: { value: 'Portrait deposit' } })
}

describe('Transactions form', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    vi.resetAllMocks()
    mockedApi.listTransactions.mockResolvedValue([])
  })

  it('uses native validation and does not submit incomplete forms', async () => {
    render(<Transactions />)
    await waitFor(() => expect(mockedApi.listTransactions).toHaveBeenCalledOnce())

    const form = screen.getByRole('heading', { name: 'Log a slip' }).closest('form')
    expect(form).not.toBeNull()
    expect((screen.getByLabelText('Amount ($)') as HTMLInputElement).value).toBe('')
    expect((screen.getByLabelText('Description') as HTMLInputElement).value).toBe('')

    fireEvent.click(screen.getByRole('button', { name: 'Add' }))

    expect(mockedApi.createTransaction).not.toHaveBeenCalled()
    expect(form).toBeInvalid()
  })

  it('shows the API error and keeps the entered values', async () => {
    mockedApi.createTransaction.mockRejectedValueOnce(new Error('Ledger is offline'))
    render(<Transactions />)
    await waitFor(() => expect(mockedApi.listTransactions).toHaveBeenCalledOnce())
    fillRequiredFields()

    fireEvent.click(screen.getByRole('button', { name: 'Add' }))

    expect(await screen.findByText('Ledger is offline')).toBeInTheDocument()
    expect(screen.getByLabelText('Amount ($)')).toHaveValue(125.5)
    expect(screen.getByLabelText('Description')).toHaveValue('Portrait deposit')
  })

  it('submits the form, resets it, and reloads the ledger', async () => {
    mockedApi.createTransaction.mockResolvedValueOnce({
      id: 1,
      type: 'income',
      amount: 125.5,
      net_amount: 125.5,
      description: 'Portrait deposit',
      date: '2026-09-25',
      fee_amount: null,
      source: 'commission',
      category: null,
      merchant: null,
      auto_categorized: false,
    })
    render(<Transactions />)
    await waitFor(() => expect(mockedApi.listTransactions).toHaveBeenCalledOnce())
    fillRequiredFields()

    fireEvent.click(screen.getByRole('button', { name: 'Add' }))

    await waitFor(() => expect(mockedApi.createTransaction).toHaveBeenCalledWith({
      type: 'income',
      amount: 125.5,
      description: 'Portrait deposit',
      date: expect.any(String),
      merchant: null,
      source: 'commission',
    }))
    await waitFor(() => expect(mockedApi.listTransactions).toHaveBeenCalledTimes(2))
    expect((screen.getByLabelText('Amount ($)') as HTMLInputElement).value).toBe('')
    expect((screen.getByLabelText('Description') as HTMLInputElement).value).toBe('')
  })
})
