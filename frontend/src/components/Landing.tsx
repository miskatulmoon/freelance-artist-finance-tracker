import { BrandMark } from './BrandMark'

const PIGMENTS = [
  { label: 'commission', color: 'var(--pig-commission)' },
  { label: 'etsy', color: 'var(--pig-etsy)' },
  { label: 'patreon', color: 'var(--pig-patreon)' },
  { label: 'other', color: 'var(--pig-other)' },
]

export function Landing({ onEnter }: { onEnter: () => void }) {
  return (
    <main className="landing">
      <div className="landing-core">
        <span className="landing-mark">
          <BrandMark w={30} />
        </span>
        <h1>StudioLedger</h1>
        <div className="tagline">the little ledger for what your art makes</div>
        <p className="landing-intro">
          Commissions, shop sales, and every receipt in between — kept in one calm book on your desk.
        </p>
        <button className="btn landing-enter" onClick={onEnter}>
          Open your ledger
        </button>
        <div className="landing-pigments" aria-hidden="true">
          {PIGMENTS.map((p) => (
            <span className="landing-pigment" key={p.label}>
              <span className="pigment-dot" style={{ background: p.color }} />
              {p.label}
            </span>
          ))}
        </div>
      </div>
    </main>
  )
}