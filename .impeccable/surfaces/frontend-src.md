---
version: 1
slug: "frontend-src"
primary_target: "frontend-src"
related_targets: ["frontend/src/App.tsx","frontend/src/index.css","frontend/src/components/Dashboard.tsx","frontend/src/components/Transactions.tsx","frontend/src/components/Commissions.tsx","frontend/src/components/Landing.tsx","frontend/src/components/Sidebar.tsx","frontend/src/components/AssistantWidget.tsx","frontend/src/components/BrandMark.tsx"]
---

---
version: 3
slug: "frontend-src"
primary_target: "frontend/src"
related_targets: ["frontend/src/App.tsx","frontend/src/index.css","frontend/src/components/Dashboard.tsx","frontend/src/components/Transactions.tsx","frontend/src/components/Commissions.tsx","frontend/src/components/Landing.tsx","frontend/src/components/Sidebar.tsx","frontend/src/components/AssistantWidget.tsx","frontend/src/components/BrandMark.tsx"]
---

# StudioLedger app surface brief

## Scope and visitor mode

The StudioLedger SPA in the Parchment & Clay redesign (user-supplied Figma design pack applied): an entry page, a left-nav shell (Ledger, Slips, Commissions), and the assistant as a corner widget. Entry: **Persuade** (one action, then in). Sections: **Operate** — a freelance artist logs money and reads their studio's health. Single-user, no auth, portfolio project.

## Audience and job

A freelance artist (illustrator/painter/crafter) at a daylight desk, juggling commissions plus Etsy/Patreon/Ko-fi income. Job: log income/expenses and commissions quickly, know their effective $/hr, and see the next 30 days. AI is a helper, never the headline.

## Chosen direction

**Parchment & Clay**, a daylight mixing chart: the paintbox world rethought in the user's Figma make (parchment ground, clay-red accent, Fraunces figures, DM Mono measurements). The interface is the artist's mixing chart; navigation is the rail of a ledger, and the assistant is a corner pencil you can set down or tuck away.

## Direction contract

THESIS: StudioLedger is opened from a quiet parchment splash page (one action — Open your ledger) and then lives behind a narrow inset-paper left rail — Ledger, Slips, Commissions — while the assistant is demoted out of navigation to a pen-nib the artist lifts and tucks into the corner; it refuses the corporate dark dashboard, the cluttered top tab strip, and any world where AI is a required destination instead of an optional note.

OWN-WORLD: A daylight studio. Warm parchment ground with a faint tooth; vivid paper for cards and the assistant panel; inset paper for the rail, inputs, and hover washes. Pigment family of clay, ochre, mauve, sage, and slate, each with an 11–14% wash fill and an ink-blocked text tone (≥ 4.5:1); one clay action accent. Four voices with four jobs: Fraunces figures and page titles (its italic is the margin voice and the table header), DM Mono for every measurement and label, DM Sans for prose and controls, Caveat for the hand (tagline, auto-stamp, margin glyph). Authored 1.5px line-stroke icons only — no emoji glyphs.

STORY: The artist lands on a paper splash with one action and steps into a calm two-panel desk (rail + page); they move between the three sections from a fixed rail (a bottom tab bar on phones), read Fraunces money in flat vivid cards over dashed rules, hear the ledger in the margin note, and lift the corner pencil whenever they want the assistant, tucking it away when done.

FIRST VIEWPORT: Desktop: a 180px inset-paper rail carries a bar-tile mark (clay/ochre/slate), a Fraunces wordmark, a Caveat tagline, three DM Sans nav items with the active one in a clay wash, and a quiet pigment-dot footer; the page opens under a Fraunces 28 section header, dashed rule, into flat 6px cards. The agent panel is a "corner pencil" fab that unfolds as a 360px note with a Fraunces italic head. Mobile (≤760px): the rail becomes a fixed inset bottom tab bar, and the assistant sits as a pen-nib fab above it, opening into a margin-fitted note panel.

FORM: User-supplied Figma design pack (the "Enhance StudioLedger Design" make export) replaces the prior swatch world; applied in-shell, no new concept roll — the redesign is recorded as DESIGN.md's Parchment & Clay world.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Memorable moment

The corner pencil: the assistant opens with the note-ink reveal — a note being set down on the desk — and tucks back to a pen-nib; the splash washes in once; and the Fraunces italic margin note under the charts is the one aside that speaks by hand, always on the real figures.

## Unresolved decisions

- None blocking. Design authority is the user's Figma make export; the port keeps all live-data wiring and the assistant's chat/insights behavior intact.
