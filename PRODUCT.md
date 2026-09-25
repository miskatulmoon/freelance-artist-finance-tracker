# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A single freelance artist (illustrator, painter, craftsperson) who juggles commissioned work with shop-style income (Etsy/Patreon/Ko-fi) and occasional paid content. They sit at a studio desk, usually in daylight, and treat money-tracking like part of the craft: quick to log, honest to review, useful at pricing time. The app is deliberately single-user with no auth (portfolio project scope).

## Product Purpose

A friendly, honest finance record for freelance artists: log transactions and commissions, see what work is actually worth, and stay ahead of cash-flow swings. The artist's own numbers are the product; every number is computed deterministically from what they logged.

## Positioning

All money math is plain, correct, deterministic Python (net income, effective $/hr, burn rate, 30-day forecast). The LLM only narrates and categorizes — it can tag an entry, explain a trend, or answer a natural-language question about the real figures, but it is an assistant beside the ledger, never the source of truth. The LLM provider is swappable (any OpenAI-compatible endpoint) with a keyword-fallback client so the app stays correct if the model is down.

## Operating Context

The artist logs a commission when it is agreed (client, piece, price, hours), records income and expenses near when they happen (source, category, optional Etsy/PayPal fees), reviews their effective hourly rate when pricing the next piece, and checks the next-30-days cash-flow radar before taking a big commitment. The interface is a studio desk object: calm, warm, paper-and-paint, not a corporate dashboard.

## Capabilities and Constraints

- Log income/expenses with source or category; optional fee deduction yields net.
- Auto-categorization: an entry left untagged asks the LLM to tag it (shown as a small badge).
- Commission tracker: agreed terms (client, price, hours, due date) lock at logging; only progress updates afterwards. Completing a piece writes its income slip into the ledger automatically — reopening or cancelling retracts it — and expected / earned / lost income are tallied by status.
- Commissions with hours → effective $/hr per piece and across the studio.
- Cash-flow radar: committed income vs. 30-day burn, with healthy/moderate/low flag.
- AI chat answers questions strictly from computed figures.
- Single-user, no auth; SQLite; seeded demo dataset via `backend/seed.py`; 57 offline tests with a mocked LLM; Vite proxies `/api` to FastAPI on :8000.
- Frontend: React 19 + Vite + Recharts; backend: FastAPI + SQLModel.

## Brand Commitments

- Name remains **StudioLedger**.
- Tagline will be refreshed so it leads with the artist's work and studio, not "AI Finance".
- User-confirmed design direction: **daylight studio, paper-and-paint feel** — light, warm, calm.
- AI features stay fully functional but are treated as a bonus/assistant, not the primary story: the chat tab gets a human label, coach/foresight copy is softened, and the assistant sits beside the ledger rather than headlining it.

## Evidence on Hand

- Working full-stack app; seeded demo dataset (see README "Getting started"); 31 passing tests with a deterministic FakeLLM.
- No real user testimonials, no published marketing copy; do not fabricate either.

## Product Principles

- The ledger is the product; the AI is a helper, never the authority.
- Correctness over cleverness: every displayed figure must trace to logged data.
- Artist-first tone and material: the surface should feel like the artist's own workbench, not a finance portal.
- Single-user and deliberately small scope; polish the demo surface, not multi-user plumbing.

## Accessibility & Inclusion

No product-specific requirement was established. Follow WCAG 2.1 AA contrast and keyboard operability by default on the new light surface.