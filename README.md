# FINANCIAL-ANALYST

*A reusable **deep-tech investment-analysis engine**: name any AI / deep-tech company
and it reproduces the full workflow — long **or** short — collecting the data with no
API key and producing a debate → synthesis → senior verdict, an Excel model with an
AI-built sensitivity matrix, and a pitch deck. (Originally built for Amkor / **AMKR**;
now target-driven — see a worked example for **NVDA** under `targets/NVDA/`.)*

A set of agents that collect and analyze data about companies.

## Agents

| # | Agent | Purpose | Status | Spec |
|---|-------|---------|--------|------|
| 01 | Data Agent | Pull last-year SEC EDGAR filings **+ companyfacts fundamentals** (revenue/margins/EPS/cash flow) | ✅ Built | [agents/01_data_agent.md](agents/01_data_agent.md) |
| 01b | Validator Agent | Auto-validates the saved filings after Agent 01 runs | ✅ Built | [agents/01b_validator_agent.md](agents/01b_validator_agent.md) |
| 02 | Tech Agent | Research a tech topic using only reliable sources (arXiv/Crossref + Playwright) | ✅ Built | [agents/02_tech_agent.md](agents/02_tech_agent.md) |
| 02b | Source Validator | Scores whether each found source is reliable; gates Agent 02 | ✅ Built | [agents/02b_source_validator.md](agents/02b_source_validator.md) |
| 03 | Market Intel Agent | Pull financials (Yahoo+CNBC) + reliable news for us & each competitor | ✅ Built | [agents/03_market_agent.md](agents/03_market_agent.md) |
| 03b | Market Data Validator | Cross-checks the two financial sources + news reliability; gates Agent 03 | ✅ Built | [agents/03b_market_validator.md](agents/03b_market_validator.md) |
| 03c | News & Analyst Harvester | Reliable news + sell-side analyst ratings for Amkor & all competitors | ✅ Built | [agents/03c_news_analyst_harvester.md](agents/03c_news_analyst_harvester.md) |
| 04 | Financial Analyst | Reads all data (01/02/03), answers from the financial side, debates 05 | ✅ Built¹ | [agents/04_financial_analyst.md](agents/04_financial_analyst.md) |
| 05 | Tech Analyst | Reads all data (01/02/03), answers from the tech side, debates 04 | ✅ Built¹ | [agents/05_tech_analyst.md](agents/05_tech_analyst.md) |
| 06 | Synthesizer | Summarizes the 04↔05 debate into one balanced answer | ✅ Built¹ | [agents/06_synthesizer.md](agents/06_synthesizer.md) |
| 07 | Senior Analyst | Orchestrates everything; valuation & KPI verdict; can activate all agents | ✅ Built¹ | [agents/07_senior_analyst.md](agents/07_senior_analyst.md) |
| 08 | Challenger | Reads files you upload, routes to layers, challenges each, reports | ✅ Built¹ | [agents/08_challenger.md](agents/08_challenger.md) |
| 09 | IR Harvester | Scrapes investor-relations sites (Playwright) for non-SEC companies | ✅ Built | [agents/09_ir_harvester.md](agents/09_ir_harvester.md) |

¹ Agents 04–07 are **LLM agents** (Claude `claude-opus-4-8`). They need an API key:
`$env:ANTHROPIC_API_KEY = 'sk-ant-...'`. The data layer (01–03) needs no key.

## The analyst pipeline (Agent 07)

```
data agents (01/02/03)  ->  DATA BRIEF  ->  DEBATE (04 vs 05)  ->  SYNTHESIS (06)  ->  SENIOR VERDICT (07)
```

```bash
python senior_analyst.py "Is Amkor fairly valued vs ASE?"          # full pipeline
python senior_analyst.py "KPI momentum vs peers?" --rounds 2        # deeper debate
python senior_analyst.py "..." --refresh-market                     # refresh data first
python senior_analyst.py "..." --dry-run                            # no API key needed
```

## Layout

```
AMKOR/
  README.md              # this file
  data_agent.py          # Agent 01  (auto-runs Agent 01b when finished)
  validator_agent.py     # Agent 01b
  tech_agent.py          # Agent 02  (calls Agent 02b on every source)
  source_validator.py    # Agent 02b
  market_agent.py        # Agent 03  (auto-runs Agent 03b when finished)
  market_validator.py    # Agent 03b
  news_agent.py          # Agent 03c  (reliable news + sell-side analyst ratings)
  analyst_common.py      # shared: Claude client + DATA BRIEF loader for 04-07
  financial_analyst.py   # Agent 04
  tech_analyst.py        # Agent 05
  debate.py              # the 04 <-> 05 argument engine
  synthesizer.py         # Agent 06
  senior_analyst.py      # Agent 07  (main entry; orchestrates 01-06)
  agent8_challenger.py   # Agent 08  (reads uploads, challenges layers, reports)
  ir_agent.py            # Agent 09  (scrapes IR sites for non-SEC companies)
  uploads/               # drop files here for Agent 08
  reliable_sources.json  # curated registry shared by 02 / 02b / 03
  competitors.json       # our company + competitor tickers for Agent 03
  ir_sources.json        # IR-site config for Agent 09 (non-SEC companies)
  agents/                # one markdown spec per agent
  data/                  # output: filings, tech research, market snapshots, reports, validations
```

## Quick start

```bash
python data_agent.py AMKR --forms 10-K 10-Q 8-K
```
