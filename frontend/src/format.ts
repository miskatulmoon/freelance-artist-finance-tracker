export function fmtMoney(n: number | null | undefined): string {
  if (n === null || n === undefined || Number.isNaN(n)) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n)
}

export function fmtMoneySigned(n: number): string {
  const s = fmtMoney(Math.abs(n))
  return n >= 0 ? `+${s}` : `−${s}`
}

export function fmtMonth(month: string): string {
  const [y, m] = month.split('-')
  const date = new Date(Number(y), Number(m) - 1, 1)
  return date.toLocaleDateString('en-US', { month: 'short' })
}

export function statusClass(status: string): string {
  if (status === 'healthy') return 'pill level-healthy'
  if (status === 'low') return 'pill level-low'
  if (status === 'moderate') return 'pill level-moderate'
  return 'pill'
}

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}