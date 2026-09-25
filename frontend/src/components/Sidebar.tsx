import { BrushIcon, LedgerIcon, SlipsIcon } from './icons'
import sllogo from '../assets/sllogo.png'

export type Section = 'ledger' | 'slips' | 'commissions'

const NAV: { id: Section; label: string; icon: React.ReactNode }[] = [
  { id: 'ledger', label: 'Ledger', icon: <LedgerIcon /> },
  { id: 'slips', label: 'Slips', icon: <SlipsIcon /> },
  { id: 'commissions', label: 'Commissions', icon: <BrushIcon /> },
]

const SUBTITLES: Record<Section, string> = {
  ledger: 'commissions · Etsy · Patreon',
  slips: 'income & expenses, one line apiece',
  commissions: 'each piece, from agreed to paid',
}

const PIGMENTS: { label: string; color: string }[] = [
  { label: 'commission', color: 'var(--pig-commission)' },
  { label: 'etsy', color: 'var(--pig-etsy)' },
  { label: 'patreon', color: 'var(--pig-patreon)' },
  { label: 'other', color: 'var(--pig-other)' },
]

export function NavItems({
  section,
  onChange,
  vertical,
}: {
  section: Section
  onChange: (s: Section) => void
  vertical: boolean
}) {
  const items = NAV.map((n) =>
    vertical ? (
      <button
        key={n.id}
        type="button"
        className="side-item"
        aria-current={section === n.id ? 'page' : undefined}
        onClick={() => onChange(n.id)}
      >
        {n.icon}
        <span>{n.label}</span>
      </button>
    ) : (
      <button
        key={n.id}
        type="button"
        className="tabbar-item"
        aria-current={section === n.id ? 'page' : undefined}
        onClick={() => onChange(n.id)}
      >
        {n.icon}
        <span>{n.label}</span>
      </button>
    ),
  )
  return <>{items}</>
}

export function Sidebar({ section, onChange }: { section: Section; onChange: (s: Section) => void }) {
  return (
    <aside className="side">
      <header className="side-brand">
        <span className="brand-mark">
          <img src={sllogo} alt="" />
        </span>
        <div>
          <h1>StudioLedger</h1>
          <div className="tagline">the little ledger for what your art makes</div>
        </div>
      </header>
      <nav className="side-nav" aria-label="Ledger sections">
        <NavItems section={section} onChange={onChange} vertical />
      </nav>
      <footer className="side-foot" aria-hidden="true">
        {PIGMENTS.map((p) => (
          <span key={p.label} className="pigment-dot" style={{ background: p.color }} />
        ))}
      </footer>
    </aside>
  )
}

export function SectionTitle({ section }: { section: Section }) {
  return (
    <header className="content-head">
      <h1>{NAV.find((n) => n.id === section)!.label}</h1>
      <div className="subtitle">{SUBTITLES[section]}</div>
    </header>
  )
}