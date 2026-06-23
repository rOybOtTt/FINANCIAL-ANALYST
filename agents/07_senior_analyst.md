# Agent 07 — Senior Analyst (orchestrator)

**Status:** ✅ Built (LLM agent — needs `ANTHROPIC_API_KEY` to run)
**Script:** [`../senior_analyst.py`](../senior_analyst.py)
**Model:** `claude-opus-4-8` (adaptive thinking, streaming) via the Anthropic SDK
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

The **head of the desk** and main entry point. For any question it answers
valuation & KPI questions, and it can **activate every other agent** as needed.

## The pipeline it runs

```
(optional) refresh data  ->  DEBATE (04 vs 05)  ->  SYNTHESIS (06)  ->  SENIOR VERDICT (07)
```

1. **Activate data agents (optional):** re-run Agents 01/02/03 to refresh data.
2. **Debate:** Financial Analyst (04) and Tech Analyst (05) open and rebut.
3. **Synthesis:** the Synthesizer (06) summarizes the debate.
4. **Senior verdict:** its own final call, focused on **valuation** and a **KPI
   scorecard** (each KPI marked Strong / Neutral / Weak with the number behind it),
   plus "what would change my mind".

## Usage

```bash
$env:ANTHROPIC_API_KEY = 'sk-ant-...'

python senior_analyst.py "Is Amkor fairly valued vs ASE?"
python senior_analyst.py "Where is Amkor's KPI momentum vs peers?" --rounds 2
python senior_analyst.py "..." --effort xhigh        # deeper reasoning

# activate other agents first to refresh data:
python senior_analyst.py "..." --refresh-market                      # Agent 03
python senior_analyst.py "..." --refresh-edgar AMKR ASX              # Agent 01
python senior_analyst.py "..." --refresh-tech "glass substrates"     # Agent 02

# plumbing check (no API key / no calls):
python senior_analyst.py "..." --dry-run
```

| Flag | Effect |
|------|--------|
| `--rounds N` | Debate rebuttal rounds (default 1) |
| `--effort` | `low\|medium\|high\|xhigh\|max` (default `high`) |
| `--refresh-market` | Re-run Market Intel Agent (03) first |
| `--refresh-edgar T...` | Re-run Data Agent (01) for those tickers first |
| `--refresh-tech "X"` | Re-run Tech Agent (02) for topic X first |
| `--dry-run` | Build the data brief only; **no API calls** |

## "Activate all agents if necessary"

The refresh flags shell out to the data agents (01/02/03), which in turn auto-run
their validators (01b/03b) and gate on reliability (02b). So one Senior Analyst
command can refresh data → validate → debate → synthesize → decide.

## Verified

`--dry-run` confirmed the full data brief assembles (~20K chars: all 6 companies'
financials + news, tech findings, EDGAR filing excerpts) and every module imports
cleanly. The LLM stages require `ANTHROPIC_API_KEY`.

## Notes

- The shared data brief is sent as a **cached** system block, reused across all
  debate/synthesis/verdict calls in a run.
- Model/params follow current guidance: `claude-opus-4-8`, adaptive thinking,
  streaming, effort parameter (no `temperature`/`budget_tokens`).
