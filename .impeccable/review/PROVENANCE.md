# Shipping rasters — provenance

Each capture below was produced with Playwright from the running build
(branch state as of this design pass) and validated mechanically: warm-light
mean ≈ 239/255, ink pixels present (min ≈ 37), zero blank regions, document
top visible, dimensions matching the named viewport.

| File | Viewport | Shows | Tool |
|---|---|---|---|
| `desktop.png` | 1440×900 (full page 1016px tall) | Ledger tab: stat grid, pigment wash chart, note from assistant at bottom | Playwright chromium, `networkidle` + 1.2s settle |
| `mobile.png` | 390×844 (full page 2266px tall) | Same, single-column; tables scroll inside `.table-wrap` | Playwright chromium |
| `assistant-desktop.png` | 1440×900 | Assistant tab with note + chat log | After clicking the Assistant tab |
| `assistant-mobile.png` | 390×844 | Same | After clicking the Assistant tab |

Captured 2026-09-23 against Vite `:5173` proxying the FastAPI server on `:8000`.