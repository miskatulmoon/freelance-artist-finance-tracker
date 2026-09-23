import { useState } from 'react'
import { Assistant } from './components/Assistant'
import { Commissions } from './components/Commissions'
import { Dashboard } from './components/Dashboard'
import { Transactions } from './components/Transactions'

type Tab = 'dashboard' | 'transactions' | 'commissions' | 'assistant'

const TABS: { id: Tab; label: string }[] = [
  { id: 'dashboard', label: 'Ledger' },
  { id: 'transactions', label: 'Slips' },
  { id: 'commissions', label: 'Commissions' },
  { id: 'assistant', label: 'Assistant' },
]

function BrandMark() {
  return (
    <svg width="26" height="32" viewBox="0 0 26 32" fill="none" aria-hidden="true">
      <rect x="1" y="8" width="7.4" height="23" rx="3.7" fill="#5b52c4" />
      <rect x="9.3" y="8" width="7.4" height="23" rx="3.7" fill="#bd8a2e" />
      <rect x="17.6" y="8" width="7.4" height="23" rx="3.7" fill="#c75d8a" />
      <ellipse cx="4.5" cy="7" rx="6" ry="3.4" fill="#5b52c4" opacity="0.55" />
      <ellipse cx="13" cy="7" rx="5.6" ry="3.2" fill="#bd8a2e" opacity="0.55" />
      <ellipse cx="21.2" cy="7" rx="5.6" ry="3.2" fill="#c75d8a" opacity="0.55" />
    </svg>
  )
}

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard')

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand-row">
          <span className="brand-mark">
            <BrandMark />
          </span>
          <div>
            <h1>
              <span className="brand">StudioLedger</span>
            </h1>
            <div className="tagline">the little ledger for what your art makes</div>
          </div>
        </div>
        <div className="subtitle">commissions · Etsy · Patreon</div>
      </header>

      <nav className="tabs" aria-label="Ledger sections">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? 'active' : ''} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'dashboard' && <Dashboard />}
      {tab === 'transactions' && <Transactions />}
      {tab === 'commissions' && <Commissions />}
      {tab === 'assistant' && <Assistant />}
    </div>
  )
}