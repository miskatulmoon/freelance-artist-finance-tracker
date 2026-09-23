# Shipping rasters — provenance

Each capture below was produced with Playwright from the running Vite build
(dev server on `:5173` proxying FastAPI on `:8000`) at the Parchment & Clay
redesign (user-supplied Figma design pack applied). Captured 2026-09-23.

| File | Viewport | Shows | Tool |
|---|---|---|---|
| `desktop.png` | 1440×900 | Ledger after "Open your ledger": clay-wash rail, Fraunces header, stat grid, wash-gradient charts, margin note — page fits the viewport (scrollHeight 900). | Playwright chromium, networkidle + settle |
| `mobile.png` | 390×844 (full page 1953px) | Same ledger, inset-paper bottom tab bar, single column; tables scroll via `.table-wrap`. | Playwright chromium |
| `assistant-desktop.png` | 1440×900 (full page 900px) | Corner assistant note panel (Fraunces italic head, chat, suggestion pills) beside the ledger. | Playwright chromium, after `.a-fab` click |
| `assistant-mobile.png` | 390×844 (full page 1953px) | Bottom tab bar + assistant panel open above it (12px gutters). | Playwright chromium |

All four verified: correct pixel dimensions via `sips`, non-blank (large PNG
payloads), and the underlying DOM validated mechanically in `verify-design.js` —
36 checks green on the new design (rail width/bg, Fraunces/DM Mono/Caveat font
loading, chip washes, badge radius, panel geometry, zero horizontal overflow at
both viewports, widget open/minimize/aria round-trip).

Design authority: `Enhance StudioLedger Design/src/App.tsx` (Figma make export)
plus its palette in that pack's `src/index.css`. The screenshots in that folder
could not be viewed (no image input this session); the port was driven from the
export's markup and tokens and checked mechanically.