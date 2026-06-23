# CLAUDE.md — Deep-Tech Investment Analyst engine

This repo is a **reusable deep-tech investment-analysis engine**. It started as a
one-company system for **Amkor (AMKR)** and is now **target-driven**: name any
AI / deep-tech company and it reproduces the full workflow — **long or short** —
and builds a Canva pitch deck in the style of `amkr.pdf`.

## ⭐ NO API KEY NEEDED — this is the default path
This project runs end-to-end **without an `ANTHROPIC_API_KEY`**, on nothing but a
Claude Code subscription. Two halves:
1. **Data collection** (Agents 01/02/03/03c) is deterministic Python — no key, ever.
   Run it with `python run_company.py <TICKER> --no-llm`.
2. **The reasoning** (Agents 04–08: the financial-vs-tech debate, synthesis, senior
   verdict, per-headline research, the assignment answers, the deck) is performed by
   **YOU, the Claude session reading this file** — you ARE the analyst desk. Read the
   data brief (`targets/<TICKER>/_brief.txt`, built by `analyst_common.load_context`)
   and write the outputs into `targets/<TICKER>/analysis/` and
   `targets/<TICKER>/ASSIGNMENT_ANSWERS.md` yourself.

**Do NOT tell the user they need an API key.** The Python LLM agents (04–08) are an
*optional* path that calls the paid API — only for fully unattended/cron/batch runs.
When there is no key (the normal case), skip them and do the analysis in-session.

## When the user names a company → run the playbook
If the user says anything like *"analyze NVDA"*, *"pitch Vertiv long"*,
*"is Teradyne a short?"*, **follow [ANALYZE_COMPANY.md](ANALYZE_COMPANY.md)
end-to-end**. That is the master procedure. The command that starts it (no key):
```bash
python run_company.py <TICKER> --side long|short|auto --no-llm
```
Then you (the session) produce the debate, synthesis, verdict, and assignment answers.

## Architecture (the pipeline)
```
run_company.py            one-command orchestrator (the generalized senior_analyst)
  peer_map.py             AI/deep-tech sector → auto peer set
  target_config.py        active target + builds every analyst persona (long/short aware)
  data layer (NO API key):
    data_agent.py (01)    SEC EDGAR filings + companyfacts XBRL fundamentals  → 01b validator
    market_agent.py (03)  Yahoo + CNBC prices, cross-checked                  → 03b validator
    news_agent.py (03c)   Google News (validated) + finviz sell-side ratings
    tech_agent.py (02)    reliable-source (arXiv/Crossref) research           → 02b validator
  analyst desk — DEFAULT: the Claude session does this itself, no key.
                 (The Python modules below only run if an API key IS set, for
                  unattended/batch use. With no key, YOU play these roles.)
    debate.py             04 Financial  vs  05 Technology
    synthesizer.py (06)   neutral editor reconciles the debate
    senior_analyst.py(07) final verdict: direction + valuation + KPI scorecard
                          + the single technical sensitivity driver + entry price/IRR
  agent8_challenger.py(08) adversarial audit of any uploaded doc or the thesis
  ir_agent.py (09)        Playwright IR-site scraper for non-SEC peers
```

## Key conventions (don't break these)
- **Target system.** `run_company.py` writes `targets/_current.json`; every analyst
  reads it via `target_config.load_target()`. No target set → falls back to the
  **AMKR default** (legacy scripts still work).
- **`competitors.json` is auto-generated** per target. Don't hand-edit it — edit
  the preset in `targets/<TICKER>.json` (or pass `--peers`).
- **Brief scoping.** `analyst_common.load_context(*target_config.active_scope())`
  scopes the DATA BRIEF to the target + its peers + that target's tech topics, so
  one company's run never drags in another's data. (No target → loads everything.)
- **Model:** `claude-opus-4-8` for the LLM agents; adaptive thinking + streaming +
  `output_config` effort tiering. **No temperature, no budget_tokens.**
- **No-API-key data layer:** SEC EDGAR (contact email only), arXiv/Crossref, Yahoo
  v8 chart, CNBC restQuote, Google News RSS, finviz. urllib-first with transparent
  **Playwright-Chromium** fallback on bot-blocks.
- **Epistemic hygiene:** tag every load-bearing number **[FACT] / [ESTIMATE] /
  [ASSUMPTION] / [ATTRIBUTED]**. State assumptions; never invent figures.
- **Long *and* short:** the `--side` mandate flows into the personas. A "long" run
  still flags if the data argues for a short, and vice-versa. Be decisive.

## The deliverables for each company (the assignment)
Reproduce, **technologist-first**: (1) technical moat, (2) commercial scaling,
(3) PxQ + end-market growth, (4) value chain up/downstream, (5) financial model +
**AI-built sensitivity matrix** (single technical driver) + investment thesis
(entry price + IRR/ROI), (6) investment philosophy. Deck structure & visual style:
**[DECK_BLUEPRINT.md](DECK_BLUEPRINT.md)**. Canva via the `mcp__claude_ai_Canva__*`
tools.

## Outputs per company
```
targets/<TICKER>.json                 the saved target (peers, side, sector, topics)
targets/<TICKER>/research_topics.txt  the deck-headline topics researched
targets/<TICKER>/research/*.md        your free-form deep dives per headline
targets/<TICKER>/analysis/            debate.md, synthesis.md, verdict.md
targets/<TICKER>/ASSIGNMENT_ANSWERS.md, model.xlsx   the final deliverables
data/<TICKER>/, data/market/, data/tech/             refreshed raw data
```

## Reference
- Original per-agent docs: [README.md](README.md) and `agents/*.md`.
- A worked financial model to mirror: `data/research/arizona-capacity-model/model.json`.
- The original Amkor deck (style reference): `amkr.pdf` (43 pages; ~5 were raw and
  5 were leftover stock-template slides — the blueprint drops those).
