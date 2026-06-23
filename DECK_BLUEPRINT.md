# DECK BLUEPRINT — the reusable pitch-deck skeleton

This is the **company-agnostic** version of `amkor.pdf`, reverse-engineered slide
by slide. When you analyze a new company, you (or Claude) rebuild *these same
slides* for the new company, in *this same visual style*, on Canva.

It encodes three things:
1. **The visual style** to reproduce on Canva.
2. **The slide structure** (the 43-page arc) with the *headline pattern* and the
   *deep-research question* behind each slide.
3. **Which slides answer which assignment question** (so nothing is missed).

> The AMKR deck had ~5 raw placeholder pages and 5 leftover stock-template pages
> (the "Salford & Co." slides). This blueprint **drops those** and standardizes
> every slide on the polished analytical style. Target length: **~28–34 real
> slides** + an appendix.

---

## 1. Visual style guide (reproduce on Canva)

| Element | Spec |
|---|---|
| **Aspect** | 16:9 widescreen |
| **Background** | pale blue-white wash `#F4F8FE` on every slide |
| **Primary text / headlines** | deep navy `#1F2D5A`, heavy bold sans (Montserrat / Open Sans / Inter) |
| **Accent blue** | corporate medium blue `#1B6CB5` |
| **Chart palette (categorical)** | sky `#5B9BD5`, coral `#F2B6A0`, sage `#A8C97F`, amber `#F2B23E`, lavender `#C9C2E0`, teal `#3FA39B` |
| **Semantic colors** | green `#2E7D32` = offered today / positive; amber `#E69500` = coming next / medium; red `#C0392B` = not offered / risk / "the gap" |
| **Corner motif** | soft periwinkle `#C9D8F0` triangle wedges, bottom-left and/or top-right |
| **Layout** | title **top-left**, bold navy headline + *gray italic subhead* directly beneath; charts/diagrams dominate the body; small gray italic **source footnote** at the bottom |
| **Logo** | company logo top-left or top-right, consistent corner |
| **Typography rule** | minimal text per slide; let the visual carry the point (assignment: "Visual-First") |

**ELI5 rule (assignment):** every technical slide must be understandable to a
non-expert at a glance — use an analogy or a simple diagram, not jargon.

---

## 2. Slide structure (the arc) — rebuild per company

Each slide below lists: **headline pattern** → *deep-research question to answer*
→ `[visual type]`. Replace `{CO}` with the company, `{TECH}` with its core
technology, `{SECTOR}` with its sector.

### Section A — Title (1 slide)
1. **"{CO}: <one-line hook>"** → the single sentence that captures the thesis. `[title + hero image + logo]`

### Section B — The Problem / Why this matters (3–5 slides)
2. **The old way and why it's hitting a wall** → what fundamental limit (physics, cost, scaling, bottleneck) creates the opportunity? `[icon/diagram]`
3. **The enabling technology** → what is the key technical shift? `[reference diagram]`
4. **Cost / performance curve** → quantify the wall (e.g. cost per unit of performance over time). `[bar/line chart]`
5. **The pivot** → "stop doing X, start doing Y" — the new approach in one diagram. `[before/after]`

### Section C — The Solution / Core Architecture (3–5 slides) → **ASSIGNMENT Q1: The Technical Moat**
6. **ELI5: how {TECH} works** → explain the architecture simply enough for a non-expert. `[labeled schematic]`
7. **The evolution timeline** → where {TECH} sits in 70 yrs of progress; what's mature vs frontier. `[timeline]`
8. **The architecture cross-section** → the actual engineering, labeled. `[exploded/cross-section diagram]`
9. **The specific engineering choice that is the moat** → *what* is hard to copy, and *why*. `[annotated diagram + 1-line proof]`
10. **TAM / market size** → how big is the end market, and its CAGR? `[rising area/line chart + source]`

### Section D — The Company (3–4 slides)
11. **Company overview** → founded / HQ / employees / revenue, 4 stat tiles. `[2×2 stat grid]`
12. **The business model in one line** → what {CO} actually sells and how it makes money. `[flow/icon]`
13. **Value chain: upstream → {CO} → downstream** → suppliers, the company's required step, customers. `[3-box flow]` → **ASSIGNMENT: value chain**
14. **"The journey of a {product}"** → the end-to-end pipeline with {CO}'s step highlighted. `[numbered step row, {CO} step green]`

### Section E — Roadmap & Portfolio (2–3 slides)
15. **The next-gen waves** → the 3–4 technologies coming next; mark where {CO} leads / lags / has a gap. `[4-card layout, semantic colors]`
16. **What {CO} offers — now / next / not (yet)** → portfolio by readiness; be honest about gaps. `[3-section readiness table]`

### Section F — Business Footprint (2–3 slides)
17. **Revenue mix** → by segment / end-market. `[donut]`
18. **Footprint / capacity** → sites, capacity, geography (or for non-manufacturers: the equivalent scale metric). `[ranked table + bar]`
19. **Customers** → who buys, concentration, named anchors; color by source confidence. `[stat cards + chips]`

### Section G — PxQ & Growth (3–4 slides) → **ASSIGNMENT: PxQ + how the end market grows**
20. **PxQ by segment** → Price × Quantity: where does revenue concentrate; barbell of slow-big vs fast-small? `[bubble: x=CAGR, y=$rev, size=rev]`
21. **Where the growth actually is** → YoY growth by segment vs the total. `[bar + dashed total line]`
22. **Future PxQ to 203X** → grow each segment at its market CAGR; does it reconcile with management's target? `[two stacked bars: now vs future]`
23. **Customer / revenue concentration** → anchor %, top-2, top-10 — the real risk. `[3 big stats + grouped list]`

### Section H — Moat & Competition (3–4 slides) → **ASSIGNMENT Q2: Commercial Scaling**
24. **The moat, stated plainly** → switching cost, scarcity, scale, relationships — and *how narrow or wide*. `[text + proof]`
25. **Trusted-partner / track record** → logo wall or evidence of durable relationships. `[logo grid]`
26. **Competitive landscape, ranked by threat** → who can take the best work and what holds each back. `[tiered cards, red/amber]`
27. **Commercial scaling: engineering choice → business outcome** → why the tech choice drives **profit, margin, market share** (with numbers). `["THE CHOICE" + 3 outcome cards + proof chain]`

### Section I — Catalyst / Special Situation (2–4 slides, optional)
28. **The catalyst** → the specific event/investment/contract that re-rates the thesis (e.g. a new facility, a design win, a reshoring tailwind). `[render/map + numbers]`
29. **Why now** → the macro/structural reason the catalyst lands now. `[flow/map]`
30. **The gap it fills** → the structural hole only {CO} fills. `[3-box flow + "THE GAP" callout]`

### Section J — Financial Model & Valuation (3–4 slides) → **ASSIGNMENT Q3**
31. **The cycle / margin history** → are you buying at the top or bottom of the range? `[20-yr bars + margin line]`
32. **Health scorecard** → liquidity, leverage, FCF, capex intensity, ROIC — Strong/Neutral/Weak. `[scorecard]`
33. **Sensitivity matrix** → the **single technical driver** (yield / power-eff / ASP-mix / attach rate / latency / capacity ramp) vs valuation; show the value swing. `[heatmap/matrix]` ← **ASSIGNMENT: AI-built sensitivity matrix**
34. **Valuation & investment thesis** → entry price, expected **IRR/ROI**, holding period, and the logic. `[scenario bands: bear/base/bull + entry line]` ← **ASSIGNMENT: thesis**

### Section K — Close (2 slides)
35. **Investment philosophy** → your one-paragraph philosophy (the assignment's open question). `[statement slide]`
36. **Open questions / what would change the thesis** → intellectual honesty. `[bullet list]`

### Appendix (optional)
- Governance / ownership; detailed comps table; data-quality & source notes.

---

## 3. Assignment coverage map (don't skip any)

| Assignment requirement | Slides |
|---|---|
| **Q1 — The Technical "Moat"** (visualize architecture; the engineering choice that wins) | 6–9, 24 |
| **Q2 — Commercial Scaling** (specs → profit/margin/share) | 27, 20–22 |
| **PxQ + how the end market grows** | 20–22, 10 |
| **Value chain upstream & downstream** | 13–14 |
| **Q3 — Financial model & valuation** | 31–34 |
| **Required: AI-built sensitivity matrix** (single technical driver) | 33 |
| **Investment thesis** (entry price + IRR/ROI + logic) | 34 |
| **ELI5 principle** | every technical slide |
| **Visual-first / minimal text** | every slide |
| **Open question — investment philosophy** | 35 |

---

## 4. The per-headline deep-research list

`run_company.py` writes a `targets/<TICKER>/research_topics.txt` from these
headline themes and runs `tech_agent.py --batch` on them (the scholarly,
reliable-source layer). For each deck headline, the deep research must answer:

1. **Core architecture / moat** — the key engineering choice and why it's hard to copy.
2. **Value chain** — upstream suppliers and downstream customers.
3. **TAM & growth** — end-market size and CAGR (cite Yole/IDTechEx/Gartner-class sources).
4. **Competitive landscape** — main competitors and the technology comparison.
5. **Roadmap** — next-generation products and where the tech is heading.
6. **PxQ economics** — ASP and unit-volume trends.
7. **Capacity / supply / footprint**.
8. **Margin & cost structure drivers**.
9. **Demand drivers** — AI / data-center capex, end-market pull.
10. **Bear case & key technical risks**.

Claude should *also* do a free-form web/MCP deep dive per headline (the
`tech_agent` layer is scholarly-only and can be noisy), and tag every
load-bearing number with a confidence flag: **[FACT] / [ESTIMATE] / [ASSUMPTION]
/ [ATTRIBUTED]**, exactly as the AMKR deck did.
