# NVIDIA (NVDA) — Deep-Tech Investment Analysis

**Technologist-first, dual-sided write-up. Maps 1:1 to `DECK_BLUEPRINT.md`.**

> **In-session analysis — no API key.** Produced by the Claude analyst desk reading
> `targets/NVDA/_brief.txt`. Data as-of **2026-06-22**; spot **$209.91** [FACT].
> Every load-bearing number is tagged **[FACT] / [ESTIMATE] / [ASSUMPTION] / [ATTRIBUTED]**.
> No figures are invented — canonical numbers only. Where the bull and bear disagree,
> both readings are shown and reconciled by the senior call.

**The one-line hook (Slide 1):** *NVDA moved the unit of sale from a chip to a coherent
rack — and the whole investment case now collapses onto a single technical number:
the accelerator dollar-share it retains as inference migrates to custom ASICs.*

**Senior call up front:** **LONG-BIASED but two-sided, with entry discipline —
accumulate below ~$195, do not chase at $210.** At ~75% retained share and a $440B
2029 TAM the stock is roughly fairly valued (~+5% IRR at spot); the edge is in the
*entry*, not the thesis. Flip to a paired underweight only on a confirmed share-loss
tell, never on a margin headline alone.

---

## Q1 — The Technical "Moat" (Blueprint slides 6–9, 24)

### ELI5 (slide 6): what NVDA actually sells now
Picture a giant AI model as a single huge brain. One chip can only hold a slice of it,
so the slices have to constantly talk to each other. **NVDA's trick is not making the
fastest single chip — it is wiring 72 chips together so tightly they behave like one
gigantic chip.** Imagine 72 office workers who, instead of emailing, share one desk and
one whiteboard at conversational speed. That shared whiteboard is the moat. A rival can
build a faster single worker (a custom ASIC), but it still can't replicate the
72-at-one-desk room — *and* it can't replace the 18 years of software everyone already
wrote for NVDA's room.

### The specific engineering choice that is the moat (slide 9)
The defensible advantage is **not any single die** — a hyperscaler ASIC can match TOPS/$
on one piece of silicon. It is the **scale-up coherence domain**:

- **Interconnect:** NVLink/NVSwitch fuse 72 GPUs into one **~130 TB/s, ~1.8 TB/s/GPU**
  non-blocking fabric (**>14x PCIe Gen5**), so a trillion-parameter Mixture-of-Experts
  model behaves as a single accelerator with most expert-hops staying in-rack
  [ATTRIBUTED]. SemiAnalysis measured GB200 NVL72 at **up to ~28x MI355X throughput on
  DeepSeek-R1 MoE** [ATTRIBUTED].
- **Software:** ~18 years of CUDA (cuDNN / TensorRT-LLM / NCCL / Triton) makes the
  switching cost *the entire ML software stack* [ATTRIBUTED].
- **Packaging allocation:** CoWoS-L 2.5D packaging (LSI bridges, ~5.5–6x reticle area)
  that NVDA **pre-books at TSMC** [ATTRIBUTED].
- **Cadence:** an annual co-design cycle (Hopper→Blackwell→Rubin→Feynman) re-touches the
  perf/watt frontier every ~12 months — faster than any challenger's design loop
  [ATTRIBUTED].

**Three independent moats — software, interconnect, packaging allocation — sit on top of
each other; a competitor must beat all three at once.**

### The honest counter (the technologist's caveat)
The moat's load-bearing claim — *"ASICs erode inference but NOT frontier-training /
large-MoE economics"* — is the one place the adversarial verification dented the bull
(LONG LB1: **weakened** on all three lenses). Real-world frontier behavior contradicts the
neat line: **Anthropic committed (Nov-2025) toward ~1M Google TPUs by 2027; Meta is
reportedly negotiating TPU leasing from 2026; Gemini trains frontier/MoE entirely on TPU**
[ATTRIBUTED]. So the moat is real at the *inference* margin and at the *frontier core* —
but the frontier is no longer 100% NVDA-only. That is exactly why the whole case reduces
to *retained share* rather than "the moat is binary."

---

## Q2 — Commercial Scaling: specs → profit / margin / share (Blueprint slides 27, 20–22)

**The proof chain — the engineering choice monetizes at a level nothing else in semis
approaches.** FY26 (anchor, all [FACT]):

| Metric | FY26 | Tag |
|---|---|---|
| Revenue | **215.94B (+65.5% YoY)** | [FACT] |
| Gross margin | **71.1%** (peaked 75.0% FY25) | [FACT] |
| Operating margin | **60.4%** | [FACT] |
| Net margin | **55.6%** | [FACT] |
| Net income | **120.07B** | [FACT] |
| Operating cash flow | **102.72B** | [FACT] |
| R&D | 18.50B (8.6% of sales) | [FACT] |
| Cash / LT debt / equity | 10.61B / 7.47B / 157.29B | [FACT] |

That is a **hardware bill-of-materials earning software economics.** The nearest
custom-silicon enabler **AVGO runs ~40% op margin; AMD ~11%** [FACT]. R&D at only 8.6%
of sales means the annual cadence **self-funds**, and a near-unlevered balance sheet means
the OpenAI/neocloud investments are paid from cash flow, not debt — categorically unlike
the Lucent/Nortel vendor-financing template the bears invoke.

**Share-economics caveat (slide 27, honest version):** the verification *weakened but did
not refute* the inference-leakage thesis (SHORT LB2: **weakened**, market lens **high**).
ASIC units grew **+44.6% vs merchant GPU +16.1% in 2026** [ATTRIBUTED]; bears model NVDA
inference share falling from ~90% toward **20–30% by 2028** [ATTRIBUTED]. The cap on the
threat: much of the ASIC "40–65% lower TCO" [ATTRIBUTED] is hyperscalers pricing captive
silicon at *cost* (no ~71% NVDA margin embedded), and only ~4–5 buyers can build captive
ASICs at all. **Blended ASP/GM dilutes if inference share leaks — even if unit count
holds.** That is the single lever this whole report turns on.

---

## Q3 — PxQ + how the end market grows (Blueprint slides 20–22, 10)

**PxQ redefined upward.** NVDA shifted the sellable SKU from a **~$30–35K discrete GPU**
to a **~$3M GB200 NVL72 rack**, with **Vera Rubin NVL72 reportedly up to ~$8.8M**
[ATTRIBUTED] — capturing the tray, NVLink switch, Grace CPU and networking margin a
chip-only vendor never sees.

**Q (volume) and the dollar pie:**
- Revenue compounded **26.97B → 60.92B → 130.50B → 215.94B** [FACT] — ~85B of
  *incremental* revenue in FY26 alone.
- Four hyperscalers guiding **~$725B 2026 capex, +~77% YoY** [ATTRIBUTED].
- Accelerator TAM **~$140B (2024) → >$440B (2030)** [ATTRIBUTED].

**The key PxQ insight:** *the dollar pie can expand faster than NVDA's share erodes.* In
the sensitivity model, holding share at 75% but moving TAM $350B→$550B swings FY29 price
**$194→$305** [ESTIMATE] — nearly as large as the share lever itself. **Even with share
erosion, NVDA's revenue can grow if the market inflects faster.**

---

## Q4 — Value chain: upstream → NVDA → downstream (Blueprint slides 13–14)

```
   UPSTREAM                         NVDA (the required step)                 DOWNSTREAM
 ┌──────────────┐              ┌──────────────────────────────┐         ┌──────────────────┐
 │ TSMC (wafers,│              │ Designs GPU + NVLink/NVSwitch │         │ Hyperscalers:    │
 │ CoWoS-L pkg) │  ───────►    │ fabric; writes CUDA stack;    │ ──────► │ MSFT/AMZN/GOOG/  │
 │ SK Hynix/    │              │ integrates GB200/Rubin RACK;  │         │ META (~$725B '26 │
 │ Micron (HBM) │              │ pre-books TSMC CoWoS-L        │         │ capex) [ATTRIB]  │
 │ ASML/AMAT    │              │ allocation (~60% of 2026)    │         │ + neoclouds      │
 └──────────────┘              └──────────────────────────────┘         │ (CoreWeave) +    │
   The supply CAP:                The value-ADD: turns commodity          │ OpenAI/Anthropic │
   HBM4 + CoWoS-L +               silicon into a coherent rack            └──────────────────┘
   Taiwan + POWER                 with software lock-in                     The CONCENTRATION
   are the bottlenecks                                                      + circularity risk
```

- **Upstream:** TSMC (CoWoS-L), SK Hynix/Micron/Samsung (HBM), ASML/Applied Materials.
  These — plus **power availability** (RAND: power, not chips, is the binding constraint
  [ATTRIBUTED]) — *cap deliverable units regardless of design wins.*
- **NVDA's required step:** integration of silicon + interconnect + CUDA + packaging
  allocation into a rack — the irreplaceable middle.
- **Downstream:** the ~5 hyperscalers, neoclouds, and AI labs. **This is also the risk:**
  the same ~5 customers that are NVDA's revenue concentration are *funding their own
  silicon* (TPU/Trainium/Maia/MTIA via AVGO/MRVL) — the customers are the competitors.

---

## Q5 — Financial model, sensitivity matrix, and the dual thesis (Blueprint slides 31–34)

### Valuation reconciliation — the 32x vs 43x denominator, honestly

| Item | Value | Tag |
|---|---|---|
| Spot price | $209.91 | [FACT] |
| Reported P/E | 32.15 | [FACT] |
| Trailing GAAP EPS (FY26) | $4.90 | [FACT] |
| FY26 net income | $120.07B | [FACT] |
| **Implied diluted shares** (NI ÷ EPS) | **~24.5B** | [ESTIMATE] |
| Market cap (spot × 24.5B) | **~$5.14T** | [ESTIMATE] |
| **Trailing P/E** (209.91 ÷ 4.90) | **42.8x** | [ESTIMATE] |
| **Implied forward EPS** (209.91 ÷ 32.15) | **~$6.53** | [ESTIMATE] |
| Forward/trailing EPS step required | **+33%** | [ESTIMATE] |

**Stated plainly:** the two numbers are not in conflict — they are the same valuation
viewed through two clocks. NVDA trades at **42.8x trailing GAAP** [ESTIMATE on FACT] and
**32.15x a forward number** [FACT] that bakes in ~+33% EPS growth to ~$6.53 [ESTIMATE].
The decisive fact the adversarial work surfaced: **reaching $6.53 forward EPS at the FY26
net margin of 55.6% [FACT] requires only ~$286B revenue, i.e. +33% YoY [ESTIMATE]** —
roughly *half* the +65.5% NVDA just printed and a fraction of FY25's +114% / FY24's +126%
[FACT]. **The forward multiple is built on a below-trend, already-decelerated bar, not a
heroic one.** PEG is **sub-1.0** [ESTIMATE] vs AMD 180.8x, MRVL 103.4x, AVGO 66.2x [FACT]
on slower growth and lower margins.

### 3-yr (FY2029) model assumptions — every input tagged

| Driver | FY2026 anchor | FY2029 base input | Tag |
|---|---|---|---|
| 2029 accelerator TAM | ~$140B (2024) | **$440B** (mid of ~$350–550B) | [ATTRIBUTED] |
| **NVDA retained $ share** (the single driver) | ~80–90% effective | **~75%** (ASIC inference leakage) | [ASSUMPTION] |
| Datacenter = % of revenue | — | **88%** | [ASSUMPTION] |
| Total revenue | $215.94B [FACT] | **~$457B** (+40/28/18% path) | [ESTIMATE] |
| Net margin | 55.6% [FACT] | **54%** | [ASSUMPTION] |
| Diluted shares | ~24.5B [EST] | **~24.4B** | [ASSUMPTION] |
| Net income | $120.07B [FACT] | ~$247B | [ESTIMATE] |
| EPS (FY29) | $4.90 [FACT] | **~$10.1** | [ESTIMATE] |
| Exit P/E | 32.15x [FACT] | **28x** (de-rate as growth normalizes) | [ASSUMPTION] |

> **Margin logic:** LONG LB2 verification *holds* — **Q4 FY26 GM exited at ~75.0% GAAP**
> [ATTRIBUTED, NVDA 8-K], so the 71.1% full-year figure is a **ramp-trough average, not a
> run-rate**. I still haircut to 54% net for prudence against recurring per-architecture
> (Rubin/Feynman) yield troughs and inference-mix dilution — I do **not** model a return
> to the 55.8% peak.

### The AI-built sensitivity matrix — single technical driver (retained accelerator share) × 2029 TAM

Each cell = **implied FY2029 price / 3-yr IRR from $209.91** [ESTIMATE]. Held constant:
net margin 54% [ASSUMPTION], 24.4B shares [ASSUMPTION], exit 28x [ASSUMPTION], datacenter
= 88% of revenue [ASSUMPTION].

| Retained accelerator share ↓ / 2029 TAM → | **$350B** | **$440B** (base) | **$550B** |
|---|---|---|---|
| **55%** (heavy ASIC encroachment) | $143 / **-12.1%** | $179 / **-5.1%** | $224 / **+2.2%** |
| **65%** (meaningful inference leakage) | $168 / **-7.1%** | $212 / **+0.3%** | $265 / **+8.0%** |
| **75%** (base — frontier held, inference shared) | $194 / **-2.5%** | **$244 / +5.2%** | $305 / **+13.3%** |
| **85%** (moat holds, ASICs stay niche) | $220 / **+1.6%** | $277 / **+9.7%** | $346 / **+18.1%** |

**Reading:** the entire **bottom-left quadrant** (share ≤65% AND TAM ≤$440B) prices NVDA
*below* today's $209.91 over three years — the short's home turf. The **top-right
quadrant** (share ≥75% AND TAM ≥$440B) delivers low-double-digit IRRs. The base cell
(75% / $440B) = **$244, +5.2% IRR** — positive but unspectacular: the stock is roughly
fairly valued at spot, with the asymmetry sitting in the tails.

### Tornado read — what actually moves the value (base cell ±)

1. **Retained share (55%→85%):** ~**$98 / 47%** — *the technical driver, dominates.*
2. **2029 TAM ($350B→$550B):** ~**$93** (at 75% row, $194→$305) — nearly co-equal; the
   dollar pie can expand faster than share erodes (the LONG's core point).
3. **Exit multiple (22x→34x):** ~**$121** spread — large but a *sentiment* lever, not a
   fundamental one; weighted least because a de-rate is the likeliest direction.
4. **Net margin (46%→57%):** ~**$58** spread — the **smallest fundamental swing.** The
   bear's whole case rests here, yet it moves value least.

**Punchline:** the bear is loudest on margin (#4, the *smallest* lever) and the short only
truly works if it is *right on share* (#1). Margin compression alone, even to 46% net,
still clears ~$241 at base TAM/multiple — **the margin short is not enough; you need the
share short.**

---

### The LONG thesis
**"The unit of sale moved from a chip to a coherent rack, and the moat moved with it."**

The moat is three stacked, independent layers (software + interconnect + packaging
allocation) a competitor must beat *simultaneously*. It monetizes at FY26 **71.1% GM /
60.4% op / 55.6% net** [FACT] — software economics on a hardware BoM, self-funding R&D,
near-unlevered. The "margin roll" is a Blackwell-ramp/CoWoS-L trough (Q4 FY26 GM exited
~75% GAAP [ATTRIBUTED]), not structural — and the tornado shows margin is the *smallest*
fundamental lever anyway. PxQ redefined upward ($30K GPU → $3M rack → ~$8.8M Rubin rack
[ATTRIBUTED]) into a TAM inflecting to >$440B [ATTRIBUTED]. At 32x forward (sub-1.0 PEG)
vs AMD 180.8x / MRVL 103.4x / AVGO 66.2x [FACT], it is the cheapest, highest-margin,
fastest-growing name in the group.

- **Valuation [ESTIMATE]:** Base **$244–283 / +5% to +10% IRR** (share 75%, TAM $440B,
  nm 54%, 28x). Bull **$346–372 / +18% to +21% IRR** (share 85%, TAM $550B, nm 55%, 30x).
- **Entry / trade [FACT inputs]:** **accumulate ≤$195, full size ≤$180; ~2:1
  reward/risk.** Median sell-side **~$300**, **8/8 Buy** [FACT].
- **Holding period:** ~3 years (to FY2029).
- **What breaks the long:** an FY23-style air-pocket off a $5.1T base; net margin
  sustained below ~50% as inference migrates to ASICs faster than TAM grows; or a
  CoWoS-L/HBM4/Taiwan supply shock. The asymmetry favors the bull only while GM holds the
  high-60s and growth stays >25%.

### The SHORT thesis
**"The rent is already compressing while the multiple still prices perfection."**

Not a fraud short — the moat (NVL72 measured up to 28x MI355X on DeepSeek MoE [ATTRIBUTED])
and CUDA are conceded. It is a **margin-and-multiple / share-leakage** short. GM **peaked
75.0% (FY25) and rolled to 71.1% (FY26) during +65.5% growth** [FACT] — margin fell at the
*top* of the cycle. Inference (~2/3 of compute [ATTRIBUTED]) migrates off merchant GPUs to
custom ASICs at 40–65% lower TCO [ATTRIBUTED]; bears model NVDA inference share falling
toward **20–30% by 2028** [ATTRIBUTED]. FY23 is the proven failure mode (rev +0.2%, GM
64.9%→56.9%, op 37.3%→15.7%, EPS $0.17 [FACT]). Circular financing (>$40B AI-equity
commitments vs $10.61B cash [FACT]; OpenAI ~$14B 2026 loss [ATTRIBUTED]) degrades the
demand signal. On a **42.8x trailing** name [ESTIMATE], a single soft quarter hits hard.

- **Valuation [ESTIMATE]:** Bear **$124–142 / -12% to -16% IRR** (share 55–60%, TAM
  ~$300–350B, nm 48–50%, 22–24x). Target on the thesis: **$140–160.**
- **Entry / trigger:** **tactical, defined-risk — put spread + AVGO/ASIC pair** on a
  share-loss tell: **GM <67% structural &/or DC rev <+25% &/or frontier-MoE moving
  off-NVDA.** Not an outright short (8/8 Buy, median ~$300, deep borrow → squeeze risk).
- **Holding period:** event-driven, ~6–18 months to a confirmed tell.
- **Why honest:** the adversarial work **refuted (high)** SHORT LB1 (margin "structurally
  peaked") on all three lenses — Q4 FY26 GM exited ~75% GAAP [ATTRIBUTED]; and the forward
  EPS bar is *below-trend*, not heroic. The short needs the *share* leg, which only
  *weakened* the bull — it did not break it.

### The senior call (the desk verdict)
**LONG-BIASED but two-sided, with entry discipline — accumulate below ~$195, do not chase
at $210.** What tips it long: the adversarial verification was decisive against the SHORT's
core claim — **SHORT LB1 (margin "structurally peaked") was refuted high on all three
lenses** because Q4 FY26 GM exited ~75% GAAP [ATTRIBUTED], so 71.1% is a ramp-trough
average, and the tornado shows margin is the *smallest* fundamental lever anyway. What
keeps it two-sided: **SHORT LB2 (inference share leakage) only weakened — it survived** —
and the verification surfaced real frontier encroachment (Anthropic→~1M TPUs, Meta
TPU-leasing) that dents the LONG's "ASICs can't touch frontier/MoE" claim. The whole call
therefore collapses onto one technical number: **NVDA's retained accelerator share.** At
~75% retained and a $440B 2029 TAM the stock is roughly fairly valued (~+5% IRR at spot),
so **the edge is in the entry, not the thesis** — buy the share-holds optionality cheaply
below $195, and flip to a paired underweight only on a confirmed share-loss tell, never on
a margin headline alone.

**Peer context [FACT]:** AMD 542.50 / 180.8x / GM 49.5%; AVGO 397.32 / 66.2x / GM 67.8%;
MRVL 301.79 / 103.4x; TSM 469.46 / 39.7x / GM 56.1%; QCOM 228.73 / 24.9x; INTC 139.12 / neg.

---

## Q6 — Investment philosophy (Blueprint slide 35)

**Find the one technical variable the whole valuation hangs on, price the tails, and let
the entry — not the narrative — carry the edge.** Great deep-tech businesses are not won
or lost on the loudest debate (here, margins) but on the quietest structural one (here,
retained dollar-share as workloads migrate). I underwrite long *and* short on the same
fact set, stress the load-bearing claims adversarially until one side *refutes* rather than
merely rebuts, and then size to the asymmetry: when a fairly-valued compounder offers free
optionality below a disciplined entry, you buy the optionality cheaply rather than chasing
the story at spot — and you express the bear case as defined-risk relative value, not a
conviction zero, because being *right on the fundamental and wrong on the price for a year*
is the most expensive mistake in this sector.

---

## Open questions / what would change the thesis (Blueprint slide 36)

- **Does the frontier stay NVDA-anchored?** Anthropic→~1M TPUs and Meta TPU-leasing
  [ATTRIBUTED] are the early tell that large-MoE training is *not* CUDA-locked. A second
  frontier lab going off-NVDA would push the model toward the 65% row.
- **Where does GM settle post-Rubin ramp?** A sustained run-rate below ~67% structural
  (not a single ramp quarter) would validate the bear's structural read.
- **Does hyperscaler capex ROI prove out?** ~$725B 2026 capex [ATTRIBUTED] depends on
  AI-application returns still unproven at that spend; a single capex pause hits a 42.8x
  name violently.
- **Power, not chips.** If power (RAND: the binding constraint [ATTRIBUTED]) caps
  deliverable units, share matters less than the TAM ceiling.

---

## Data-quality & source caveats (honest)

- **In-session, no API key.** Reasoning performed by the Claude desk on the deterministic
  data brief; the LLM agents 04–08 were not run.
- **Spot $209.91, reported P/E 32.15, the FY26 anchor are [FACT].** The valuation bridge
  (**42.8x trailing, ~$6.53 forward EPS, ~24.5B shares, ~$5.14T mcap**) is **[ESTIMATE]**
  derived arithmetically from those facts — not separately reported.
- **The FY2029 model is [ESTIMATE/ASSUMPTION].** TAM ($350–550B), retained share (the
  single driver), net margin (54%), share count and exit multiple (28x) are assumptions;
  the matrix prices/IRRs follow mechanically and are only as good as those inputs.
- **[ATTRIBUTED] items** (Q4 FY26 GM ~75% exit, NVL72 vs MI355X benchmark, ~$725B capex,
  Anthropic/Meta TPU moves, Rubin rack ASP ~$8.8M, ASIC TCO and unit-growth figures,
  circular-financing details) come from third-party sources cross-referenced in the brief,
  not audited financials — treat as directional, not precise.
- **Forward EPS is a market-implied figure**, not guidance: ~$6.53 is simply
  209.91 ÷ 32.15 [ESTIMATE]. The bull's 32x and the bear's 43x are the *same* valuation on
  two clocks; do not double-count.
- **Two-sided by design.** A "long" mandate still flags the short, and vice versa — the
  matrix tails, not a single point estimate, are the decision object.
