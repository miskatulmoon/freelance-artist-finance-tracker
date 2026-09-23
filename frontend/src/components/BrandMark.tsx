export function BrandMark({ w = 26 }: { w?: number }) {
  const h = (w / 26) * 32
  return (
    <svg width={w} height={h} viewBox="0 0 26 32" fill="none" aria-hidden="true">
      <rect x="1" y="8" width="7.4" height="23" rx="3.7" fill="#5b52c4" />
      <rect x="9.3" y="8" width="7.4" height="23" rx="3.7" fill="#bd8a2e" />
      <rect x="17.6" y="8" width="7.4" height="23" rx="3.7" fill="#c75d8a" />
      <ellipse cx="4.5" cy="7" rx="6" ry="3.4" fill="#5b52c4" opacity="0.55" />
      <ellipse cx="13" cy="7" rx="5.6" ry="3.2" fill="#bd8a2e" opacity="0.55" />
      <ellipse cx="21.2" cy="7" rx="5.6" ry="3.2" fill="#c75d8a" opacity="0.55" />
    </svg>
  )
}