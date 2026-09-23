export function BrandMark({ w = 26 }: { w?: number }) {
  const h = (w / 26) * 40
  return (
    <svg width={w} height={h} viewBox="0 0 26 40" fill="none" aria-hidden="true">
      <rect x="1" y="8" width="7.4" height="32" rx="2.2" fill="#5a6b96" opacity="0.88" />
      <rect x="9.3" y="0" width="7.4" height="40" rx="2.2" fill="#a84b2f" opacity="0.9" />
      <rect x="17.6" y="14" width="7.4" height="26" rx="2.2" fill="#a8833a" opacity="0.85" />
    </svg>
  )
}