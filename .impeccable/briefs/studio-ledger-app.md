# StudioLedger app surface brief

## Scope and visitor mode

Whole-interface redesign of the StudioLedger SPA (Dashboard, Transactions, Commissions, Assistant tabs). Visitor mode: **Operate** — a freelance artist logs money and reads their studio's health. Single-user, no auth, portfolio project.

## Audience and job

A freelance artist (illustrator/painter/crafter) at a daylight desk, juggling commissions plus Etsy/Patreon/Ko-fi income. Job: log income/expenses and commissions quickly, know their effective $/hr, and see the next 30 days. AI is a helper, never the headline.

## Chosen direction

**The watercolor swatch palette** (pick card; roll key `cd953953`, kind `pick`). The interface is the artist's mixing chart: warm paper ground, ink and a true tabular mono for every figure, a handful of real pigment families carrying meaning, the assistant as a pinned paper note rather than a dashboard hero.

## Direction contract

THESIS: Money takes the material of the artist's own palette — the surface is a mixing-chart wash on warm paper where each income source is a pigment and every figure is inked in mono; it refuses the dark-glass "AI SaaS" field and the hero-metric template, and refuses to let the assistant sit above the ledger it serves.

OWN-WORLD: Warm ivory paper ground (ink, graphite, hairline pencil rules), one trusted mono for all numbers (IBM Plex Mono), a warm humanist UI face for everything else (Karla); pigment family = income source (commission indigo, Etsy ochre, Patreon rose, other viridian; income warm, spend cool, one vermilion action accent used sparingly). Cards are swatch slips: paper, hairline border, faint warm shadow, small tracked pigment labels; chart bars read as washes (rounded, vertical pigment gradient); tables are ruled ledger lines; pills are tinted pigment chips; a faint paper grain keeps it physical, never busy.

STORY: The artist opens their ledger and instantly reads what the work is worth — committed, colored by where it came from — finds today's slip, logs the piece in an hour, and when they want an opinion the assistant writes a note onto the page. They believe their numbers are theirs, correct, and drawn from what they logged; the assistant is a bonus pencil, not the product.

FIRST VIEWPORT: A ruled page: header row with the four-pigment brush-mark logo + "StudioLedger" and tagline "the little ledger for what your art makes"; pigment-chip tab bar (Dashboard, Transactions, Commissions, Assistant — assistant last, tucked). Four margin-note stat blocks across the top in mono ink; a two-column chart spread (income by source as pigment washes, monthly ink trend); cash-flow slice and the assistant's note card placed after the charts, at the bottom of the page, its "Make me a note" button the single primary action below the fold.

FORM: Pick card — watercolor swatch palette, my ranked position 1 of 7, seed cd953953 (kind `pick`).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Memorable moment

"Make me a note": the assistant's commentary pencils itself onto the page (fade + slight rise + ink reveal) instead of loading like a dashboard panel.

## Unresolved decisions

- None blocking; copy refresh only where the brief calls for it (tagline, tab label "Assistant", coach card copy, auto-tag chip wording).