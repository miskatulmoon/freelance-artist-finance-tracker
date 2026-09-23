---
version: 1
slug: "frontend-src"
primary_target: "frontend-src"
related_targets: ["frontend/src/App.tsx","frontend/src/index.css","frontend/src/components/Dashboard.tsx","frontend/src/components/Landing.tsx","frontend/src/components/Sidebar.tsx","frontend/src/components/AssistantWidget.tsx"]
---

---
version: 2
slug: "frontend-src"
primary_target: "frontend/src"
related_targets: ["frontend/src/App.tsx","frontend/src/index.css","frontend/src/components/Dashboard.tsx","frontend/src/components/Transactions.tsx","frontend/src/components/Commissions.tsx","frontend/src/components/Landing.tsx","frontend/src/components/Sidebar.tsx","frontend/src/components/AssistantWidget.tsx"]
---

# StudioLedger app surface brief

## Scope and visitor mode

The StudioLedger SPA after the product-shell pass: an entry page, a left-nav shell (Ledger, Slips, Commissions), and the assistant as a corner widget. Entry: **Persuade** (one action, then in). Sections: **Operate** — a freelance artist logs money and reads their studio's health. Single-user, no auth, portfolio project.

## Audience and job

A freelance artist (illustrator/painter/crafter) at a daylight desk, juggling commissions plus Etsy/Patreon/Ko-fi income. Job: log income/expenses and commissions quickly, know their effective $/hr, and see the next 30 days. AI is a helper, never the headline.

## Chosen direction

**The watercolor swatch palette** (pick card; roll key `cd953953`, kind `pick`), extended in-shell: same warm paper world, now framed by a ruled left rail and a tuck-away corner pencil. The interface is the artist's mixing chart; navigation is the rail of a ledger, and the assistant is a note you can set down or put away.

## Direction contract

THESIS: StudioLedger is opened from a quiet paper entry page (one action — Open your ledger) and then lives behind a ruled left rail — Ledger, Slips, Commissions — while the assistant is demoted out of navigation to a pen-nib the artist lifts and tucks into the corner; it refuses the buy-now landing, the cluttered top tab strip, and any world where AI is a required destination instead of an optional note.

OWN-WORLD: The world is unchanged: warm ivory paper ground, ink + graphite + hairline rules, IBM Plex Mono for every figure, Karla for prose, Caveat for the hand (tagline, note heads, stamp); pigment family per income source; one vermilion action accent. The new shells draw only from these tokens: the rail is vivid paper over paper ground with a rule hairline and a single vermilion active state; the corner assistant is a vivid note with a soft paper lift whose minimize control is the quiet inset pill; nav icons are authored 1.5px line strokes in ink tones.

STORY: The artist lands on a paper entry page and opens the ledger; the desk becomes two panels — a fixed rail and the page. They move between the three sections from the rail (a bottom tab bar on phones), read their numbers, and lift the corner pencil whenever they want the assistant, tucking it away when done.

FIRST VIEWPORT: A vivid-paper left rail (236px) carries the brand mark + wordmark + tagline, three stroke-icon nav items (Ledger, Slips, Commissions) with the active one tinted vermilion, and a quiet pigment-dot footer; the content page rules under a section header (title + hint) and opens into the mono-ink stat grid. Mobile (≤760px): the rail becomes a fixed bottom tab bar, and the assistant sits as a pen-nib fab above it, opening into a margin-fitted note panel.

FORM: Pick card — watercolor swatch palette, seed cd953953 (kind `pick`), extended in-shell; no new concept roll.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Memorable moment

The corner pencil: the assistant opens with the note-ink reveal — a note being set down on the desk — and tucks back to a pen-nib fab; entry washes in once only, on the paper page.

## Unresolved decisions

- None blocking. The in-page "A note from your assistant" card was moved into the widget per user choice; copy stands as seeded and stylistically consistent.
