import { useState } from 'react'
import { Chat } from './components/Chat'
import { Commissions } from './components/Commissions'
import { Dashboard } from './components/Dashboard'
import { Transactions } from './components/Transactions'

type Tab = 'dashboard' | 'transactions' | 'commissions' | 'chat'

const TABS: { id: Tab; label: string }[] = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'transactions', label: 'Transactions' },
  { id: 'commissions', label: 'Commissions' },
  { id: 'chat', label: 'AI Chat' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard')

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>
            <span className="brand">StudioLedger</span> · AI Finance for Freelance Artists
          </h1>
        </div>
        <div className="subtitle">commissions · Etsy · Patreon</div>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t.id} className={tab === t.id ? 'active' : ''} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'dashboard' && <Dashboard />}
      {tab === 'transactions' && <Transactions />}
      {tab === 'commissions' && <Commissions />}
      {tab === 'chat' && <Chat />}
    </div>
  )
}