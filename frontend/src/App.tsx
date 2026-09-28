import { useEffect, useState } from 'react'
import { AssistantWidget } from './components/AssistantWidget'
import { Commissions } from './components/Commissions'
import { Dashboard } from './components/Dashboard'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Landing } from './components/Landing'
import { NavItems, SectionTitle, Sidebar } from './components/Sidebar'
import type { Section } from './components/Sidebar'
import { Transactions } from './components/Transactions'

export default function App() {
  const [entered, setEntered] = useState(() => {
    try {
      return sessionStorage.getItem('entered') === 'true'
    } catch {
      return false
    }
  })
  const [section, setSection] = useState<Section>('ledger')

  useEffect(() => {
    try {
      sessionStorage.setItem('entered', String(entered))
    } catch {
      /* ignore */
    }
  }, [entered])

  const handleEnter = () => setEntered(true)

  if (!entered) return <Landing onEnter={handleEnter} />

  return (
    <ErrorBoundary>
      <div className="shell">
      <Sidebar section={section} onChange={setSection} onBack={() => setEntered(false)} />
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
    </ErrorBoundary>
  )
}