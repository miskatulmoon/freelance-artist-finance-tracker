import { BrandMark } from './BrandMark'
import studioArtwork from '../assets/albert-klein-ZWWJ8fd8ayw-unsplash.jpg'
import studioBrushes from '../assets/olga-deeva-Q0cWddzY--0-unsplash.jpg'

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
      <div className="landing-art-stack" aria-hidden="true">
        <div className="landing-art landing-art-primary">
          <img src={studioBrushes} alt="" />
          <span>made by hand, tracked with care</span>
        </div>
        <div className="landing-art landing-art-secondary">
          <img src={studioArtwork} alt="" />
          <span>colour, texture, rhythm</span>
        </div>
      </div>
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