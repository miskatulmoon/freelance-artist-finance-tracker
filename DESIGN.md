---
name: StudioLedger
description: the little ledger for what your art makes
colors:
  accent: "#a84b2f"
  accent-hover: "#8e3f26"
  accent-soft: "rgba(168, 75, 47, 0.12)"
  paper: "#ede8df"
  paper-vivid: "#f6f2ec"
  paper-inset: "#e0d9ce"
  ink: "#241e16"
  ink-soft: "#5c5044"
  graphite: "#6f6350"
  hairline: "#e8e0d4"
  rule: "#d4c9b8"
  pig-commission: "#a84b2f"
  pig-etsy: "#a8833a"
  pig-patreon: "#8a6070"
  pig-other: "#546b57"
  pig-income: "#a8833a"
  pig-spend: "#5a6b96"
  wash-commission: "#edd8d0"
  wash-etsy: "#e8d9ae"
  wash-other: "#d3e2d4"
  wash-patreon: "#e4d4dc"
  wash-spend: "#d4daed"
  tone-commission: "#8a3a20"
  tone-etsy: "#60460f"
  tone-patreon: "#6e3f54"
  tone-other: "#3f5f44"
  tone-income: "#60460f"
  tone-spend: "#40536f"
typography:
  display:
    fontFamily: "'Fraunces', Georgia, serif"
    fontSize: "28px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: -0.02em
  headline:
    fontFamily: "'Fraunces', Georgia, serif"
    fontSize: "30px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: -0.02em
  title:
    fontFamily: "'DM Mono', ui-monospace, monospace"
    fontSize: "10px"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: 0.12em
  body:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "'DM Mono', ui-monospace, monospace"
    fontSize: "10px"
    fontWeight: 500
    letterSpacing: 0.08em
  hand:
    fontFamily: "Caveat, 'Segoe Script', cursive"
    fontSize: "22px"
    fontWeight: 500
    lineHeight: 1.15
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#fff8f5"
    rounded: "{rounded.sm}"
    padding: "8px 18px"
    typography: "{typography.body}"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-ghost:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-soft}"
    rounded: "20px"
    padding: "8px 14px"
  tab:
    backgroundColor: "transparent"
    textColor: "{colors.ink-soft}"
    rounded: "5px"
    padding: "9px 12px"
  tab-active:
    backgroundColor: "{colors.wash-commission}"
    textColor: "{colors.tone-commission}"
    rounded: "5px"
    padding: "9px 12px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "7px 10px"
  pill:
    backgroundColor: "{colors.wash-commission}"
    textColor: "{colors.tone-commission}"
    rounded: "2px"
    padding: "2px 8px"
  card:
    backgroundColor: "{colors.paper-vivid}"
    rounded: "{rounded.md}"
    padding: "20px"
  note:
    backgroundColor: "{colors.paper-vivid}"
    rounded: "{rounded.lg}"
    padding: "16px 18px"
---

# Design System: StudioLedger

## Overview

**Creative North Star: "Parchment & Clay"**

StudioLedger is the little ledger that lives on an artist's desk — a daylight-scene mixing chart in warm parchment, clay-red actions, and the tube colors of real pigments. Money reads in a calm serif figure as if set by a small letterpress inside the desk; the measurements around it — dates, hours, rates, chip labels — are typed in a quiet mono; and the only hand script is the artist's own margin notes, the tagline, and the rubber-stamped "auto".

The voice is warm, candid, unhurried, and a little worn-in. Density is calm: a narrow inset-paper rail (180px) holds the three sections, and one column of flat cards carries the numbers to a ~1100px measure. Figures are set large enough to read across the room. The interface never performs "artiness": it behaves like a ledger that happens to be painted in clay and ochre. The AI does not headline anything; it is a corner pencil you lift when you want it and tuck away when you do not — never a navigation item, never between the artist and the ledger.

The composition gap from the previous AI-SaaS build is deliberate: no dark slate, no glow, no orbit-graph hero. StudioLedger is a light scene (daylight studio), and the palette carries that scene, never the category.

**Key Characteristics:**

- Warm parchment tooth over the whole scene; cards one step vivid, the rail one step inset, flat by tone with a soft lift for the things that float (mark, panel, fab).
- Income sources as tube colors in the clay–ochre–mauve–sage family; income washes golden, spending washes slate-cool.
- Money set in Fraunces display (tabular via system rendering), measurements in DM Mono, hand prose in Caveat, everything spoken in DM Sans.
- Ink-blocked pigment text kept ≥ 4.5:1 on every wash.
- One action colour — the clay red — per card area; pigment tints belong to sources and statuses only.
- Single authored motion moment: the assistant's note reveals like ink settling onto paper.

## Colors

A parchment-and-clay palette: two warm papers for ground and surfaces, an inset paper for the rail, an ink family for type and rules, a set of pigment tubes for money sources and status, and one clay accent that marks the single action on any card.

### Primary
- **Clay Red** (#a84b2f): the one action colour. Filled primary buttons, focus rings, the caret, tax delete links. It stays rare — one action per card — so its weight survives.

### Secondary
- **Ochre Gold** (#a8833a): Etsy/shop income — bars, chips, legend dots; also the "moderate" cash-flow level and the income wash.
- **Clay** (#a84b2f): commission income — bars, chips, legend dots; also the "low" cash-flow level.
- **Mauve** (#8a6070): Patreon income — bars, chips.
- **Sage** (#546b57): other income — bars, chips; also the "healthy" cash-flow level and the auto-tag stamp tint.
- **Slate** (#5a6b96): expense/spend — bars, chips, and the expense wash.

### Neutral
- **Parchment** (#ede8df): page ground and input surfaces. **Vivid Paper** (#f6f2ec): cards and the assistant panel. **Inset Paper** (#e0d9ce): the side rail, base chips, chat bubbles from the artist, table-row hover.
- **Ink** (#241e16): display and figure text. **Soft Ink** (#5c5044): body prose. **Graphite** (#6f6350): captions, hints, dim cells (AA on parchment and vivid).
- **Hairline** (#e8e0d4): dashed band rules under headers. **Ledger Rule** (#d4c9b8): card borders, table header rules, rail edge.

### Named Rules
**The Wash Rule.** A pigment belongs to a source, a status, or a sign — never to decoration. Chips render a pigment at its wash fill (11–14%) with an ink-blocked deep tone (all ≥ 4.5:1 on the wash). If a color is not a source, a status, or the one accent, it is not on the page.

**The One-Action Rule.** One filled button per card area. Clay marks the single thing you can do right now; everything else is ghost, link, or the paper itself.

## Typography

**Display Font:** Fraunces (with Georgia/serif fallback)
**Body Font:** DM Sans (with system-ui fallback)
**Mono/Label Font:** DM Mono (with ui-monospace fallback)
**Hand Font:** Caveat (with 'Segoe Script' fallback)

**Character:** Four voices, four jobs. Fraunces — a humanist serif with warm italic — sets every figure and every page title; its italic is the margin-note voice and the table header. DM Sans is the neutral Dutch humanist that carries all prose and controls. DM Mono is the small measuring hand — it labels cards, chips, dates, hours, and rates. Caveat is the personal hand: the tagline, the "auto" stamp, the margin glyph, and nothing else.

### Hierarchy
- **Display** (Fraunces 400, 28–38px, 1.0, -0.02em): the section title and the landing name. Set once per page.
- **Headline** (Fraunces 400, 30px, 1.0, -0.02em): the stat-card figure — the biggest read, always money.
- **Title** (DM Mono 500, 10px, 1.3, +0.12em, uppercase): card h3s — the quiet label that sets the figure free.
- **Body** (DM Sans 400, 13px, 1.55): prose, descriptions, table cells.
- **Label** (DM Mono 500, 10px, +0.08em, uppercase): form field labels and the table's mono cells.
- **Hand** (Caveat 500, 22px): the tagline and the margin note.

### Named Rules
**The Figure-And-Measure Rule.** A number that means money is Fraunces (KPI figures, table amounts, cash-flow) sized by hierarchy. A measurement that is not money — dates, hours, rates, tags — is DM Mono with tabular numerals. A personal aside (tagline, note, stamp, margin glyph) is Caveat. Everything else is DM Sans. So the eye sorts the page without reading it: big serif = the money, small mono = the measurements, hand = the artist.

## Layout

Two panels on the desk: a fixed inset-paper left rail (180px) for the brand, the wordmark, the tagline, and the three-section navigation; and a single ~1100px paper page beside it (`max-width: 1100px`, centered, `padding: 26px 30px 56px`), closed by a dashed hairline under the section header. Below 760px the rail steps down to a fixed bottom tab bar so the sections stay thumb-high; the page padding opens at the base to clear it. Cards sit in a `12px`-gap grid that holds to one column at ≤560px, two at ≤900px, and fills the three/four-col pattern above. Wide tables never break the page: on narrow screens they scroll inside their own `.table-wrap` (overflow-x, touch scrolling) rather than stretching the document. Density is set to let figures and rows breathe — 7–18px of padding, more air above a heading than below it.

## Elevation & Depth

Flat-by-tone, not flat-by-default. Cards are flat (border only); depth carries the few things that genuinely float:

- **Soft Paper Lift** (`0 1px 2px rgba(36,30,22,.07), 0 8px 20px rgba(36,30,22,.06)`): the brand mark tile, the assistant panel, the corner fab, the splash logo.
- **Hover Raise** (`0 6px 22px rgba(36,30,22,.12)`): the fab under cursor.
- **Row Wash** (`--paper-inset`): hover wash behind table rows.

### Named Rules
**The No-Costume Rule.** No hard offset block shadows, no glow, no arbitrary blur pills. If an element needs to lift, it gets a soft shadow or a warmer paper — nothing that fights the desk scene.

## Shapes

Radius is tight and print-like: **extra-small** 4px (inputs, buttons, chips), **small** 6px (cards, the landing CTA), **large** 8px (the assistant panel). Exceptions carry intent: the commission status badge and the assistant's pills round to 20px so interaction reads as stitched soft fiber, and the nav-item active state is a 5px inset wash, not a pill. The distinctive silhouettes: a washed bar whose fill fades 90%→45% down the column, a ledger table ruled with dashed hairlines that stop at the last row, and the auto-tag stamp — hand script inside a toothy 1px border, rotated -1deg, as if pressed by hand.

## Components

### Buttons
- **Shape:** near-square 4px, padding 8px 18px, weight 500.
- **Primary:** Clay filled, ivory-cream text (#fff8f5); hover deepens to `#8e3f26`; active presses 1px; disabled fades to 0.55.
- **Ghost:** parchment fill, rule border, soft-ink text, 20px radius in the widget/suggestions; hover moves text to ink and border to graphite.
- **Link-danger:** plain Clay text in DM Mono 11px with an underline on hover — deletion is a whisper, twice in a row (delete the record, never the page).

### Chips
- **Type/tag chip:** DM Mono 10px, uppercase, +0.06em, 2px radius, padding 2px 8px. Income chips wash sage, expense chips wash clay, and source/category chips wash from their pigment — always a wash fill and a deep ink-blocked tone.
- **Status badge (commissions):** DM Mono 10px lowercase, rounded 20px. In-progress washes ochre, agreed washes slate, completed washes sage, cancelled sits on inset.

### Navigation (side rail & bottom tab bar)
- The rail is inset paper on the left; Ledger, Slips, and Commissions carry authored 1.5px line-stroke icons (an open ledger, a receipt slip, a brush) in one consistent weight. A nav item is soft-ink DM Sans 13px; hover raises to ink on parchment; active is a clay wash at 5px radius with the deep-clay tone, `aria-current="page"`.
- Below 760px the rail becomes a fixed inset-paper bottom tab bar of three equal items; the assistant only ever appears as the corner pencil, never in navigation.
- The section header rules the page under a dashed hairline; its title is Fraunces 28px 400.

### Cards / Containers
- **Corner Style:** 6px. **Background:** vivid paper. **Shadow:** none (flat, bordered). **Border:** 1px ledger rule. **Internal Padding:** 20px.
- The headline figure (`.big`) is Fraunces 400 30px ink; the card's h3 title sits above in DM Mono caps, leaving the number unmistakable.

### Inputs / Fields
- **Style:** parchment fill, rule border, 4px radius, 7px 10px padding, DM Sans 13; placeholder in graphite; caret in clay.
- **Focus:** border turns ink, plus a 3px clay-tinted ring (`--accent-soft`).

### Charts
- Bars fade like a paint wash: each source column is a vertical gradient 90% → 45% opacity of its pigment, corner radius [2,2,0,0]. Axis labels are Fraunces 11 italic (categories) and DM Mono 10 (numbers); the cursor wash is inset paper; the tooltip is a vivid-paper card with a rule border, 4px radius, DM Sans 12. Monthly trend separates income (ochre wash) from expense (slate wash) and labels them in DM Mono under the chart.

### Margin note
- Under the charts, a hand note: a Caveat clay glyph ("✦") and Fraunces 14 italic 300 soft-ink copy, computed honestly from the ledger (the strongest income source on record). It is the only decorative aside on the page and it always cites the real figures.

### Assistant widget (corner pencil)
- A pen-nib fab pinned to the bottom-right corner (44px circle, vivid paper, rule border, Soft Paper Lift; the authored nib in soft-ink, warming to ink, rotating a quarter turn when open). Open, it unfolds as a 360px vivid-paper note panel — `min(520px, viewport − 120px)` deep, 8px radius — with a Fraunces italic head ("A note from your assistant"), parchment/inset chat bubbles (14/14/4/14), the suggestion pills and "Read me the state of the studio" at 20px radius, and a pill Ask control. The note-ink reveal is its one entrance. On phones it sits above the tab bar as a margin-fitted sheet (12px gutters).

### Stamp (auto-tag)
- A hand-stamped "auto": Caveat 600 13px in the sage tone, 9% sage background, 40% sage border, 4px radius, rotated -1deg, sitting on the slip's row beside the merchant.

### Tables (ruled ledger)
- Dashed hairline borders under every row, the last dropped so the ledger closes; headers Fraunces 12 italic 300 graphite (never uppercase); dates/hours/rates in DM Mono; amounts right-aligned in Fraunces 15 ink; rows wash inset on hover and scroll inside `.table-wrap` under 560px.

## Do's and Don'ts

### Do:
- **Do** tint chips and bars from the source pigment (`#a84b2f`, `#a8833a`, `#8a6070`, `#546b57`) with an 11–14% wash fill and a deep ink-blocked text tone (each ≥ 4.5:1 on its wash).
- **Do** set money in Fraunces and measurements (dates, hours, rates) in DM Mono at the right edge of their columns.
- **Do** write the tagline, the auto stamp, and the margin glyph in Caveat; every figure in Fraunces; everything else in DM Sans.
- **Do** reserve clay (#a84b2f) for the one action on a card and the selection/focus signals.
- **Do** close each ruled band with a dashed hairline under the section header.

### Don't:
- **Don't** darken the scene. The ground stays parchment (#ede8df); no dark mode, no slate mountains, no glow — the scene is a daylight studio.
- **Don't** promote the assistant out of the corner. AI is the quiet note and the corner pencil — never a navigation item, never between the artist and the ledger.
- **Don't** use a system display face, gradient text, or emoji glyphs as icons; the mark is an authored SVG bar tile in clay, ochre, and slate.
- **Don't** add kickers/eyebrows above headings, five-card icon rows, or hero-metric hero templates — the stat grid carries the story.
- **Don't** set hard offset shadows (`4px 4px 0`) or zero-blur shadows; lift comes from the Soft Paper Lift token or tone.
- **Don't** let a table, chart, or any surface push the page wider than the viewport — wrap tight, scroll wide.