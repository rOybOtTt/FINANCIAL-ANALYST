# Agent 05 — Tech Analyst

**Status:** ✅ Built (LLM agent — needs `ANTHROPIC_API_KEY` to run)
**Script:** [`../tech_analyst.py`](../tech_analyst.py)
**Model:** `claude-opus-4-8` (adaptive thinking, streaming) via the Anthropic SDK
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Read **all** the data collected by Agents 1/2/3 and answer your question from a
**technology perspective** — packaging roadmap (2.5D/3D, chiplets, fan-out,
wafer-level, advanced substrates, HBM packaging), technical moat vs peers,
product mix, R&D, and where the end-markets (AI/HPC/auto/mobile) are heading.
Also argues the technology side against the Financial Analyst (04) in a debate.

## How it gets the data

Same shared **DATA BRIEF** as every analyst — see
[`analyst_common.load_context()`](../analyst_common.py). It does not re-fetch.

## Run it

```bash
$env:ANTHROPIC_API_KEY = 'sk-ant-...'
python tech_analyst.py "Is Amkor's advanced-packaging tech a real moat?"
```

Usually invoked by the **Senior Analyst (07)**, not directly.

## What it returns

(1) technology read of the data, (2) a clear position, (3) the technical evidence
behind it, (4) the biggest technical risk to that view — all grounded in the DATA
BRIEF, no invented technical facts.

## In a debate

`analyze(question, brief, opponent_argument=<financial argument>)` makes it rebut
the Financial Analyst: concede valid points, then counter on roadmap, moat,
product mix, and demand direction.

## Notes

Same runtime requirements, caching, and effort behavior as the Financial Analyst
(04) — see [04_financial_analyst.md](04_financial_analyst.md).
