---
name: StudioLedger
description: the little ledger for what your art makes
colors:
  accent: "#b03a24"
  accent-hover: "#98311e"
  accent-soft: "rgba(176, 58, 36, 0.12)"
  paper: "#f6efe0"
  paper-vivid: "#fdf8ee"
  paper-inset: "#eee4cf"
  ink: "#2b241d"
  ink-soft: "#5a4f41"
  graphite: "#6f6350"
  hairline: "#e2d7bf"
  rule: "#d7caac"
  pig-commission: "#5b52c4"
  pig-etsy: "#bd8a2e"
  pig-patreon: "#c75d8a"
  pig-other: "#2f7d6f"
  pig-income: "#9a6720"
  pig-spend: "#50708e"
  tone-commission: "#49409f"
  tone-etsy: "#896428"
  tone-patreon: "#a74774"
  tone-other: "#22665b"
  tone-income: "#7d5418"
  tone-spend: "#3f5a78"
typography:
  display:
    fontFamily: "Karla, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.01em
  headline:
    fontFamily: "'IBM Plex Mono', ui-monospace, monospace"
    fontSize: "27px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: -0.02em
  title:
    fontFamily: "Karla, system-ui, sans-serif"
    fontSize: "11.5px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0.09em
  body:
    fontFamily: "Karla, system-ui, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Karla, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    letterSpacing: 0.02em
  hand:
    fontFamily: "Caveat, 'Segoe Script', cursive"
    fontSize: "19px"
    fontWeight: 500
    lineHeight: 1.15
rounded:
  sm: "9px"
  md: "12px"
  lg: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "#fff6ec"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
    typography: "{typography.title}"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-ghost:
    backgroundColor: "{colors.paper-vivid}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.sm}"
    padding: "8px 16px"
  tab:
    backgroundColor: "{colors.paper-vivid}"
    textColor: "{colors.ink-soft}"
    rounded: "999px"
    padding: "8px 16px"
  tab-active:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-hover}"
    rounded: "999px"
    padding: "8px 16px"
  input:
    backgroundColor: "{colors.paper-vivid}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "8px 11px"
  pill:
    backgroundColor: "{colors.paper-inset}"
    textColor: "{colors.graphite}"
    rounded: "999px"
    padding: "2px 9px"
  card:
    backgroundColor: "{colors.paper-vivid}"
    rounded: "{rounded.lg}"
    padding: "18px"
  note:
    backgroundColor: "{colors.paper-vivid}"
    rounded: "{rounded.md}"
    padding: "16px 18px"
---

# Design System: StudioLedger

## Overview

**Creative North Star: "The Studio Paintbox"**

StudioLedger is the little ledger that lives on an artist's desk — a daylight-studio relic made of warm ivory paper, hand-inked annotations, and the tube colors of real pigments. Money is not a dashboard's abstraction here; it is something measured by hand, sources labeled in their own paint colors, running totals set in typewriter-style numerals on a ruled page. The whole screen is one long paper ground with painters' wash tints bleeding into the bars.

The voice is warm and candid, unhurried, and a little worn-in: a note from an assistant reads like a friend writing by hand, an auto-categorized slip carries a rubber-stamped "auto", and the tagline is script, not marketing type. Density is calm — a fixed left rail and one column of cards over a ~1120px measure, figures large enough to read across the room — and the interface never performs "artiness": it behaves like a ledger that happens to be painted. The AI does not headline anything; it is a corner pencil you lift when you want it and tuck away when you do not — never a navigation item, never between the artist and the ledger.

The composition gap from the previous AI-SaaS build is deliberate: no dark slate, no glow, no orbit-graph hero. StudioLedger is a light scene (daylight studio), and the palette carries that scene, never the category.

**Key Characteristics:**

- Warm ivory paper ground with a faint woven tooth; card surfaces one step vivid, inset panels one step shadowed.
- Income sources as tube colors (commission violet, Etsy ochre, Patreon rose, other teal); income warm, spending cool.
- All money in IBM Plex Mono with tabular numerals — numbers read as measurements, never as decoration.
- Hand script (Caveat) reserved for the tagline, note heads, and the auto-tag stamp; prose is Karla.
- One action colour (a vermilion red) per card; pigment tints belong to sources and statuses only.
- Single authored motion moment: the assistant's note reveals like ink settling onto paper.
- Ruled ledger edges (hairlines) instead of card borders stronger than the paper line.

## Colors

A paintbox palette: three warm papers for ground and surfaces, an ink family for type and rules, a set of pigment tubes for money sources and status, and one accent red that marks the single action on any card.

### Primary
- **Vermilion Red** (#b03a24): the one action colour. Filled primary buttons, focus rings, the caret, selected-tab tint. It stays rare — one action per card — so its weight survives.

### Secondary
- **Commission Violet** (#5b52c4): commission income — bars, pills, and legend dots.
- **Etsy Ochre** (#bd8a2e): Etsy income — bars, pills, legend dots. Also the "moderate" cash-flow level.
- **Patreon Rose** (#c75d8a): Patreon income — bars, pills, legend dots.
- **Other Income Teal** (#2f7d6f): other income; also the "healthy" cash-flow level and the auto-tag stamp tint.
- **Income Umber** (#9a6720): net income figures and positive deltas — warm, the money coming in.
- **Spending Blue-Teal** (#50708e): expense figures and negative deltas — cool, the money going out.

### Neutral
- **Ivory Paper** (#f6efe0): page ground. **Vivid Paper** (#fdf8ee): card, note, tab, and input surfaces (reading ground). **Inset Paper** (#eee4cf): base pills, chat bubbles from the artist, and the insights box.
- **Ink Brown** (#2b241d): display and figure text, heading of a card. **Soft Ink** (#5a4f41): body and secondary prose. **Graphite** (#6f6350): labels, captions, hints, table headers.
- **Hairline** (#e2d7bf): card and control borders. **Ledger Rule** (#d7caac): header rules, tab underline, and table row lines.

### Named Rules
**The Tube Rule.** A pigment belongs to a source, a status, or a sign — never to decoration. Tints are rendered as the pigment at 11–13% with a 34% border and an ink-blocked text tone (each ≥ 4.5:1 on paper). If a color is not a source, a status, or the one accent, it is not on the page.

**The One-Action Rule.** One filled button per card area. Vermilion marks the single thing you can do right now; everything else is ghost, link, or the paper itself.

## Typography

**Display Font:** Karla (with system-ui fallback)
**Body Font:** Karla (with system-ui fallback)
**Label/Mono Font:** IBM Plex Mono (with ui-monospace fallback)
**Hand Font:** Caveat (with 'Segoe Script' fallback for missing script support)

**Character:** Three voices, each with one job. Karla is the warm, plainspoken humanist face for everything verbal. Plex Mono carries every amount and every age-sensitive figure, tabular, so columns line up like a ruled page. Caveat is the hand on the page — the tagline under the mark, the "note from your assistant" head, the stamped "auto" — the only place a personal hand speaks.

### Hierarchy
- **Display** (Karla 700, 24px, 1.05, -0.01em): the wordmark in the header. At most one font-size step above the page's largest figure.
- **Headline** (Plex Mono 600, 27px, 1.2, -0.02em): the stat-card figure — the biggest read, always money.
- **Title** (Karla 700, 11.5px, 1.3, +0.09em, uppercase): card h3s and column heads; the quiet label that sets the figure free.
- **Body** (Karla 400, 13.5px, 1.55): prose, notes, table cells. Body measure stays 65–75ch down the single column.
- **Label** (Karla 600, 12px, +0.02em): form field labels.
- **Hand** (Caveat 500, 19–22px, 1.15): tagline, note heads, stamp. Never used for data.

### Named Rules
**The Ink-And-Sum Rule.** If it is a number that means money, it is Plex Mono with `tabular-nums`. If it is a personal aside (tagline, note, stamp), it is Caveat. Everything else is Karla. A number rendered in Karla reads as prose; a note rendered in Karla loses the hand that wrote it.

## Layout

Two panels on the desk: a fixed vivid-paper left rail (236px) for the brand and the three-section navigation, and a single ~1120px paper page beside it (`max-width: 1120px`, centered, `padding: 30px 26px 120px`), ruled shut by a hairline under the section header. Below 760px the rail steps down to a fixed bottom tab bar so the sections stay thumb-high; the page padding opens at the base to clear it. Cards sit in a `16px`-gap grid that holds to one column at ≤560px, two at ≤900px, and fills the three/four-col pattern above. Wide tables never break the page: on narrow screens they scroll inside their own `.table-wrap` (overflow-x, touch scrolling) rather than stretching the document. Density is set to let figures and rows breathe — 8–18px of padding, more air above a heading than below it.

## Elevation & Depth

Flat-by-tone, not flat-by-default. Depth comes from layered papers — vivid cards over raw paper, inset panels a step darker — plus a single soft, offset, blurred shadow:

- **Soft Paper Lift** (`0 1px 2px rgba(43,36,29,.07), 0 8px 20px rgba(43,36,29,.06)`): cards, notes, the brand mark, assistant bubbles. Low, warm, desk-like.
- **Row Wash** (`rgba(122,92,46,.07)`): hover wash behind table rows.

### Named Rules
**The No-Costume Rule.** No hard offset block shadows, no glow, no arbitrary blur pills. If an element needs to lift, it gets the soft shadow or a warmer paper — nothing that fights the desk scene.

## Shapes

Radius is gentle but visible: **extra-small** 9px (inputs and buttons), **small/md** 12px (notes, chat bubbles, the insights box), **large** 14px (cards). Pills (tabs and chips) skip the pill at 999px. The distinctive silhouettes: a washed bar whose fill is a paint gradient per source, a ledger table ruled with hairlines that stop at the last row, and the auto-tag stamp — hand script inside a toothy 1px border, rotated -1deg, as if pressed by hand.

## Components

### Buttons
- **Shape:** gently rounded (9px), full-height padding 8px 16px, weight 700.
- **Primary:** Vermilion filled, cream text (#fff6ec); hover deepens to `#98311e`; active presses 1px; disabled fades to 0.55.
- **Ghost:** vivid paper, hairline border, soft-ink text; hover moves text to ink and border to rule.
- **Link-danger:** plain text in accent-hover (12.5px, 600) with an underline on hover — deletion is a whisper, twice in a row (delete the record, never the page).

### Chips (pills)
- **Style:** inset paper base, rule-tinted hairline border, 2px 9px padding, 11.5px weight 600, radius 999. Text graphite by default.
- **Source / status variants:** tint the chip from the source or status pigment — background at 11–13%, border at 34%, text at the ink-blocked tone (≥4.5:1). The money column itself never takes a chip; the pill annotates the figure.

### Navigation (side rail & bottom tab bar)
- Ledger, Slips, and Commissions live in a vivid-paper left rail with authored 1.5px line-stroke icons (an open ledger, a receipt slip, a brush) in one consistent weight. A nav item is quiet ink-soft text; hover warms it to ink on a faint inset wash; active is vermilion — accent-soft fill, vermilion-tinted border, accent-hover text, `aria-current="page"`.
- Below 760px the rail becomes a fixed bottom tab bar of three equal tinted buttons; the assistant only ever appears as the corner pencil, never in navigation.
- The section header rules the page under a hairline, closing the band exactly as the old header did.

### Cards / Containers
- **Corner Style:** large (14px). **Background:** vivid paper. **Shadow:** Soft Paper Lift. **Border:** 1px hairline. **Internal Padding:** 18px.
- The headline figure (`.big`) is Plex Mono 600 27px ink; the card's h3 title sits above in graphite capsules, leaving the number unmistakable.

### Inputs / Fields
- **Style:** vivid paper, hairline border, 9px radius, 8px 11px padding; placeholder in graphite; caret in vermilion.
- **Focus:** border turns ink, plus a 3px vermilion-tinted ring (`rgba(176,58,36,.14)`).

### Notes (assistant note)
- The assistant's picture is a note on the desk, not a pane: vivid paper, 12px radius, soft shadow, and a Caveat head ("A note from your assistant") above short Karla copy. Text arrives through the one authored moment — the **note-ink** reveal (rise 5px, blur 3px → clear, 0.32s `cubic-bezier(.16,1,.3,1)`) — and then rests still. No entrance for anything else.

### Assistant widget (corner pencil)
- The assistant is a pen-nib fab pinned to the bottom-right corner (56px circle, vivid paper, hairline border, Soft Paper Lift; nib in ink-soft, warming to ink). Open, it unfolds as a `380px` vivid-paper note panel — `min(600px, viewport − 120px)` deep — with the Caveat head, a pencil-and-suggestions chat, and an inset-pill minimize control that drops it back to the nib. The note-ink reveal is its one entrance; the nib rotates a quarter turn when expanded. On phones it sits above the tab bar as a margin-fitted sheet (12px gutters).

### Stamp (auto-tag)
- A hand-stamped "auto": Caveat 600 14px in teal tone, background 9% teal, border 40% teal, 1px radius 5, rotated -1deg, sitting on the slip's row beside the merchant.

### Tables (ruled ledger)
- Hairline `rule` borders under every header and row, the last row border dropped so the ledger closes; headers graphite 11px uppercase with 0.07em tracking; amounts right-aligned with `tabular-nums`, `.money` cells in Plex Mono 600 ink. Rows warm-wash on hover and scroll inside `.table-wrap` under 560px.

## Do's and Don'ts

### Do:
- **Do** tint chips and bars from the source pigment (`#5b52c4`, `#bd8a2e`, `#c75d8a`, `#2f7d6f`) with a 12%-ish transparent fill, 34% border, and an ink-blocked text tone.
- **Do** set every money amount in Plex Mono with `tabular-nums` at the right edge of its column.
- **Do** write the tagline, note heads, and the auto stamp in Caveat; everything else in Karla.
- **Do** reserve vermilion (#b03a24) for the one action on a card and the selection/focus signals.
- **Do** keep a `leader` line — `border-bottom: var(--rule)` — under the header and the tabs to close each ruled band.

### Don't:
- **Don't** darken the scene. The ground stays ivory paper (#f6efe0); no dark mode, no slate, no glow — the scene is a daylight studio.
- **Don't** promote the assistant out of the corner. AI is the quiet note and the corner pencil — never a navigation item, never between the artist and the ledger.
- **Don't** use a system display face, gradient text, or emoji glyphs as icons; the mark is an authored SVG brushwork gesture.
- **Don't** add kickers/eyebrows above headings, five-card icon rows, or hero-metric hero templates — the stat grid carries the story.
- **Don't** set hard offset shadows (`4px 4px 0`) or zero-blur shadows; lift comes from the Soft Paper Lift token or tone.
- **Don't** let a table, chart, or any surface push the page wider than the viewport — wrap tight, scroll wide.