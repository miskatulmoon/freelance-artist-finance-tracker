import studioArtwork from '../assets/albert-klein-ZWWJ8fd8ayw-unsplash.jpg'
import studioBrushes from '../assets/olga-deeva-Q0cWddzY--0-unsplash.jpg'
import studioPaints from '../assets/pexels-beytlik-11170403.jpg'
import studioDesk from '../assets/pexels-michael-burrows-7147451.jpg'
import studioSketch from '../assets/pexels-tara-winstead-6692154.jpg'
import studioTools from '../assets/pexels-yesimcolak-32620533.jpg'
import studioCanvas from '../assets/gabriella-clare-marino-fxgLyOP69fw-unsplash.jpg'
import studioWall from '../assets/wesley-tingey-XvlbhiTzfWA-unsplash.jpg'
import studioHands from '../assets/pexels-luian-c-1229000-39257084.jpg'
import studioShelf from '../assets/pexels-margarita-141441249-16495458.jpg'
import sllogo from '../assets/new_sl_logo.png'
import { BrushIcon, LedgerIcon, ForecastIcon } from './icons'

const FEATURES = [
  {
    label: 'Commission tracker',
    desc: 'Log clients, pieces, hours, and know your real hourly rate.',
    icon: <BrushIcon />,
  },
  {
    label: 'Shop income',
    desc: 'Etsy, Patreon, and every other source in one place.',
    icon: <LedgerIcon />,
  },
  {
    label: 'Cash-flow forecast',
    desc: 'See the next 30 days before they surprise you.',
    icon: <ForecastIcon />,
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
        <div className="landing-art landing-art-tertiary">
          <img src={studioPaints} alt="" />
          <span>naptime!</span>
        </div>
        <div className="landing-art landing-art-quaternary">
          <img src={studioDesk} alt="" />
          <span>the desk where it happens</span>
        </div>
        <div className="landing-art landing-art-quinary">
          <img src={studioSketch} alt="" />
          <span>sketches before invoices</span>
        </div>
        <div className="landing-art landing-art-senary">
          <img src={studioTools} alt="" />
          <span>tools of the trade</span>
        </div>
        <div className="landing-art landing-art-septenary">
          <img src={studioCanvas} alt="" />
          <span>fresh canvas, old habits</span>
        </div>
        <div className="landing-art landing-art-octonary">
          <img src={studioWall} alt="" />
          <span>the gallery wall</span>
        </div>
        <div className="landing-art landing-art-nonary">
          <img src={studioHands} alt="" />
          <span>meow I'm posing</span>
        </div>
        <div className="landing-art landing-art-denary">
          <img src={studioShelf} alt="" />
          <span>stocked &amp; ready</span>
        </div>
        <div className="landing-art landing-art-secondary">
          <img src={studioArtwork} alt="" />
          <span>colour, texture, rhythm</span>
        </div>
      </div>
      <div className="landing-core">
        <span className="landing-mark">
          <img src={sllogo} alt="" />
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
              <span className="landing-feat-icon">{f.icon}</span>
              <div className="landing-feat-label">{f.label}</div>
              <div className="landing-feat-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}