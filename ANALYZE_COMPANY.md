# ANALYZE_COMPANY — the one file you open to analyze any AI / deep-tech company

**Open this folder in VS Code, open this file, and tell Claude the company.**
It reproduces the entire AMKOR workflow for *any* AI / deep-tech name — long or
short — and builds a Canva pitch deck in the same style as `amkr.pdf`.

> **How to trigger it (just type the name):**
>
> > "Analyze **NVDA** as a **long**."
> > "Run the workflow on **Vertiv**, I'm thinking **short**."
> > "Pitch **Teradyne** — decide long or short for me."
>
> Claude will follow the 6 steps below from start to finish.

---

## What you get for each company
1. A refreshed **data brief** (SEC filings + fundamentals + market + news + analyst ratings) for the company **and an auto-built peer set**.
2. **Deep research on every deck headline** (the 10 research themes in `DECK_BLUEPRINT.md`).
3. A **long *or* short investment view** from the analyst debate → synthesis → **senior verdict** (with entry price + expected IRR/ROI + the single technical sensitivity driver).
4. Answers to **all 6 assignment questions**.
5. A **Canva deck** rebuilt in the `amkr.pdf` visual style.

---

## ⭐ Runs with NO API key (the default)
You do **not** need an `ANTHROPIC_API_KEY` — only a Claude Code subscription.
The data layer is deterministic Python (no key). The *reasoning* (Agents 04–08:
debate, synthesis, verdict, deck answers) is done by **Claude in this session** —
Claude IS the analyst desk. The Python LLM agents are an optional, key-only path
for unattended/batch runs. **Default to `--no-llm` and let Claude do the analysis.**

## STEP 0 — One-time setup (only if not done)
```bash
python -m pip install playwright    # 'anthropic' only needed for the optional key path
python -m playwright install chromium
python -m pip install pymupdf       # optional: render a reference deck PDF to images
# No API key required for the default (in-session) path.
```

## STEP 1 — Pick the target and side
Decide the **ticker** and the **side**: `long`, `short`, or `auto` (let the desk decide).
If it's not in `peer_map.py`'s sectors, pass peers explicitly with `--peers`.

## STEP 2 — Run the engine (one command, no key)
```bash
python run_company.py NVDA --side long --no-llm
#   --side long|short|auto      the mandate
#   --no-llm                    data + research only — the DEFAULT (no API key)
#   --peers AMD AVGO TSM ...     override the auto peer set
#   --sector ai-compute          force a sector bucket (python peer_map.py lists them)
#   --dry-run                    write the plan only, no network
```
This writes the target config, regenerates `competitors.json` for the cohort,
refreshes the data layer, and deep-researches every deck headline. (Drop `--no-llm`
**only** if an API key is set and you want the Python agents to run unattended.)

**Claude's job during this step:** run the command, watch for failures (blocked
scrapes auto-fall-back to Playwright), and if a peer is wrong, re-run with `--peers`.
Then **build the data brief and play Agents 04–08 yourself** (Step 3 onward) — read
`targets/<TICKER>/_brief.txt` and write `analysis/debate.md`, `synthesis.md`,
`verdict.md`, and `ASSIGNMENT_ANSWERS.md`. (To regenerate the brief file:
`python -c "import analyst_common as ac, target_config as tc; open('targets/<TICKER>/_brief.txt','w',encoding='utf-8').write(ac.load_context(*tc.active_scope()))"`.)

## STEP 3 — Deepen the per-headline research
`run_company.py` runs the *scholarly* layer (`tech_agent`, arXiv/Crossref). Now
Claude does a **free-form deep dive per `DECK_BLUEPRINT.md` headline** using
WebSearch / WebFetch / the playwright MCP, and writes findings to
`targets/<TICKER>/research/<headline>.md`. Tag every load-bearing number
**[FACT] / [ESTIMATE] / [ASSUMPTION] / [ATTRIBUTED]**.

Use Agent 08 (challenger) to stress-test any document or the thesis:
```bash
python agent8_challenger.py path/to/file --senior
```

## STEP 4 — Answer the 6 assignment questions
Write `targets/<TICKER>/ASSIGNMENT_ANSWERS.md` covering, **technologist-first**:

1. **The Technical "Moat"** — visualize the core architecture; the specific engineering choice that creates the advantage. (ELI5.)
2. **Commercial Scaling** — translate the tech spec into profit / margin / market share, with numbers.
3. **PxQ + end-market growth** — Price × Quantity, and how the end market compounds.
4. **Value chain** — upstream suppliers and downstream customers.
5. **Financial model & valuation** — incl. the **AI-built Sensitivity Matrix** naming the single technical driver (yield / power-eff / ASP-mix / attach rate / latency / capacity) that most moves the valuation; and the **investment thesis**: entry price + expected **IRR/ROI** + holding period + logic.
6. **Investment philosophy** — your one-paragraph answer to the open question.

The senior verdict in `targets/<TICKER>/analysis/verdict.md` already drafts the
direction, valuation, KPI scorecard, sensitivity driver, and entry/IRR — build on it.

## STEP 5 — Build the financial model (Excel)
The assignment requires an Excel model with a sensitivity matrix. Build
`targets/<TICKER>/model.xlsx` (or `.csv` you import to Excel): revenue build
(PxQ), margin path, the **sensitivity matrix** (driver on one axis, valuation on
the other), and the valuation → entry price → IRR/ROI. Use
`data/research/arizona-capacity-model/model.json` as a worked example of the AMKR
model's structure.

## STEP 6 — Build the Canva deck (same style as amkr.pdf)
Rebuild the slides in `DECK_BLUEPRINT.md` for this company, in the style guide's
colors/fonts/layout. Use the **Canva MCP**:

1. `mcp__claude_ai_Canva__get-design-content` / `search-designs` — find a base if reusing one.
2. `mcp__claude_ai_Canva__generate-design-structured` — generate the deck from a structured outline. Feed it:
   - the **slide structure** (Section A–K of `DECK_BLUEPRINT.md`, ~28–34 slides, placeholders dropped),
   - the **visual style** (navy `#1F2D5A`, pale-blue `#F4F8FE` bg, the chart palette, top-left bold headline + gray italic subhead, corner periwinkle triangles),
   - per slide: the headline, the one-line subhead, and the chart/diagram spec.
3. For data charts, generate the PNGs first (the matplotlib scripts in `data/presentation/make_*.py` are templates — re-point them at `targets/<TICKER>/` data), then place them on the slides.
4. `mcp__claude_ai_Canva__export-design` — export to PDF/PPTX.

> Canva can't *edit* an existing gamma/deck via MCP beyond what the tools expose;
> generate fresh and let the user fine-tune in the Canva editor.

---

## The mental model (what's under the hood)
```
run_company.py <TICKER> --side long|short
   ├─ peer_map.py            auto-builds the competitor cohort
   ├─ target_config.py       sets the active target (drives every analyst persona)
   ├─ data_agent.py (01)     SEC filings + XBRL fundamentals      ─┐
   ├─ market_agent.py (03)   Yahoo+CNBC prices, cross-checked      │ no API key
   ├─ news_agent.py (03c)    reliable news + sell-side ratings     │ needed
   ├─ tech_agent.py (02)     deep research on each deck headline  ─┘
   └─ analyst desk (needs ANTHROPIC_API_KEY):
        debate.py (04 Financial vs 05 Tech) → synthesizer.py (06) → senior verdict (07)
```
Validators (01b/02b/03b) gate the data automatically. See `CLAUDE.md` for the
full engine rules and `README.md` for the original agent reference.

## Switching / re-running
- Switch target any time: `python run_company.py VRT --side short`.
- Re-run the original Amkor target: `python run_company.py AMKR`.
- Saved targets live in `targets/<TICKER>.json`; the active one is `targets/_current.json`.
- `competitors.json` is **auto-generated** per target — don't hand-edit it; edit the target preset instead.
