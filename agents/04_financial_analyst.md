# Agent 04 — Financial Analyst

**Status:** ✅ Built (LLM agent — needs `ANTHROPIC_API_KEY` to run)
**Script:** [`../financial_analyst.py`](../financial_analyst.py)
**Model:** `claude-opus-4-8` (adaptive thinking, streaming) via the Anthropic SDK
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Read **all** the data collected by Agents 1/2/3 and answer your question from a
**financial perspective** — valuation, margins, growth, balance sheet, cash flow,
competitive financial position, risks. Also argues the financial side against the
Tech Analyst (05) in a debate.

## How it gets the data

It does **not** re-fetch anything. It reads the shared **DATA BRIEF** built by
[`analyst_common.load_context()`](../analyst_common.py) from:
- `data/market/*/snapshot.json` — financials + reliable news (Agent 03)
- `data/tech/*/findings.json` — reliable tech research (Agent 02)
- `data/<TICKER>/manifest.json` + extracted filing text — SEC filings (Agent 01)

So every analyst argues over **one shared set of facts**.

## Run it

```bash
# 1. set your key (once per shell)
$env:ANTHROPIC_API_KEY = 'sk-ant-...'
# 2. ask
python financial_analyst.py "Is Amkor's valuation justified vs ASE?"
```

Usually you won't call it directly — the **Senior Analyst (07)** orchestrates it.

## What it returns

A structured financial view: (1) financial read of the data, (2) a clear
position, (3) the key numbers behind it, (4) the biggest financial risk to that
view. Every claim is grounded in the DATA BRIEF — it's instructed not to invent
figures.

## In a debate

`analyze(question, brief, opponent_argument=<tech argument>)` makes it rebut the
Tech Analyst: concede genuinely valid points, then counter on valuation, margins,
cash, and cyclicality.

## Notes

- Requires `pip install anthropic` (already installed) and `ANTHROPIC_API_KEY`.
- Effort defaults to `medium` for analyst turns (debate has many calls); the
  Senior Analyst runs the desk at `high`.
- The big data brief is sent as a **cached** system block, so repeated calls in a
  debate reuse the same prefix (cheaper/faster).
