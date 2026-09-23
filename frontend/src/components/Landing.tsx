import { BrandMark } from './BrandMark'

const FEATURES = [
  {
    label: 'Commission tracker',
    desc: 'Log clients, pieces, hours, and know your real hourly rate.',
  },
  {
    label: 'Shop income',
    desc: 'Etsy, Patreon, and every other source in one place.',
  },
  {
    label: 'Cash-flow forecast',
    desc: 'See the next 30 days before they surprise you.',
  },
]

export function Landing({ onEnter }: { onEnter: () => void }) {
  return (
    <main className="landing">
      <div className="landing-core">
        <span className="landing-mark">
          <BrandMark w={44} />
        </span>
        <h1>StudioLedger</h1>
        <div className="tagline">the little ledger for what your art makes</div>
        <p className="landing-intro">
          Commissions, shop sales, and every receipt in between — kept in one calm book on your desk.
        </p>
        <button className="btn landing-enter" onClick={onEnter}>
          Open your ledger
        </button>
        <div className="landing-feats" aria-label="What StudioLedger does">
          {FEATURES.map((f) => (
            <div className="landing-feat" key={f.label}>
              <div className="landing-feat-label">{f.label}</div>
              <div className="landing-feat-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}