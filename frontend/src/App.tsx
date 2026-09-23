import { useState } from 'react'
import { AssistantWidget } from './components/AssistantWidget'
import { Commissions } from './components/Commissions'
import { Dashboard } from './components/Dashboard'
import { Landing } from './components/Landing'
import { NavItems, SectionTitle, Sidebar } from './components/Sidebar'
import type { Section } from './components/Sidebar'
import { Transactions } from './components/Transactions'

export default function App() {
  const [entered, setEntered] = useState(false)
  const [section, setSection] = useState<Section>('ledger')

  if (!entered) return <Landing onEnter={() => setEntered(true)} />

  return (
    <div className="shell">
      <Sidebar section={section} onChange={setSection} />
      <main className="content">
        <div className="page">
          <SectionTitle section={section} />
          {section === 'ledger' && <Dashboard />}
          {section === 'slips' && <Transactions />}
          {section === 'commissions' && <Commissions />}
        </div>
      </main>
      <nav className="tabbar" aria-label="Ledger sections">
        <NavItems section={section} onChange={setSection} vertical={false} />
      </nav>
      <AssistantWidget />
    </div>
  )
}