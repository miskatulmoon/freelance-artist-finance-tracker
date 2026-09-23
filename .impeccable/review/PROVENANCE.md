# Shipping rasters — provenance

Each capture below was produced with Playwright from the running Vite build
(dev server on `:5173` proxying FastAPI on `:8000`) at the branch state of
this product-shell pass. Captured 2026-09-23.

| File | Viewport | Shows | Tool |
|---|---|---|---|
| `desktop.png` | 1440×900 | Ledger after "Open your ledger": stat grid, pigment wash chart, monthly trend, cash-flow slice — page fits the viewport (scrollHeight 900). | Playwright chromium, networkidle + settle |
| `mobile.png` | 390×844 (full page 1231px) | Same ledger, bottom tab bar, single column; tables scroll via `.table-wrap`. | Playwright chromium |
| `assistant-desktop.png` | 1440×900 (full page 900px) | Corner assistant panel open beside the ledger (Commissions reachable in rail at background). | Playwright chromium, after `.a-fab` click |
| `assistant-mobile.png` | 390×844 (full page 1903px) | Bottom tab bar + assistant panel open above it (margin-fitted sheet). | Playwright chromium |

All four verified: correct pixel dimensions via `sips`, non-blank (large PNG
payloads), and the underlying DOM validated mechanically in `verify.js` —
26 checks green, including zero horizontal overflow at both viewports and the
widget open/minimize/aria round-trip.