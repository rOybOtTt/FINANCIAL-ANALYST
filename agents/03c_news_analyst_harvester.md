# Agent 03c — News & Analyst Harvester

**Status:** ✅ Built and tested (live, 14 companies)
**Script:** [`../news_agent.py`](../news_agent.py)
**Part of:** the Agent 03 market-intel family
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

For Amkor **and every competitor**, collect **analyst reports/coverage** and
**news** from **legit sources only**, and save them.

## What it collects (per company)

1. **News** — Google News RSS (~100 raw items/company), each item's **publisher
   validated by the Source Validator (02b)**; only reliable outlets are kept.
   Query uses the company name (+ US ticker for US-listed); the Yahoo suffix is
   dropped for foreign names so search isn't polluted.
2. **Analyst ratings (sell-side)** — the firm / action / rating-change / price-
   target history scraped from **finviz via Playwright** (e.g. *Melius
   Hold→Buy $60, UBS Buy→Neutral $55, Goldman/JP Morgan/Morgan Stanley/KeyBanc
   initiations*). Available for **US-listed / ADR** tickers; foreign listings are
   skipped gracefully.
3. **Analyst-coverage news** — the subset of news flagged with analyst keywords
   (upgrade/downgrade/price target/initiates/rating…).

## Legit sources

Reads [`../reliable_sources.json`](../reliable_sources.json), which now includes
financial-news + analyst outlets (Reuters, Bloomberg, WSJ, FT, CNBC, Barron's,
Seeking Alpha, TipRanks, MarketBeat, Benzinga, Zacks, Morningstar, Nasdaq,
Investing.com…) **and the research firms cited in the AMKR guide files** (Yole,
IDTechEx, DIGITIMES, TrendForce, Counterpoint, Omdia, Mordor, Grand View,
MarketsandMarkets). Anything not recognised as reliable is dropped.

## Usage

```bash
python news_agent.py                 # all companies in competitors.json
python news_agent.py AMKR MU TSM     # explicit tickers
python news_agent.py --news 40       # max reliable news items per company (default 40)
python news_agent.py --no-analysts   # skip the finviz analyst-ratings scrape
```

## Output (per company)

```
data/market/<TICKER>/
  news.json             # all reliable news (title, source, url, date, analyst flag)
  analyst_ratings.json  # finviz sell-side ratings history (US-listed only)
  news_report.md        # human-readable: ratings table + analyst news + reliable news
data/market/_news_run.json   # run summary
```

## Verified run (full roster, 14 companies)

Rich coverage for the majors — AMKR 40 news + 10 ratings; Micron 40+10; TSMC
40+10; Intel 40+10; ASE 25+10; ChipMOS 11+8. Asian-listed peers got news but no
finviz ratings (not US-listed): JCET 31, KYEC 25, Powertech 16, SK Hynix 15,
Tongfu 13, Samsung 11. Huatian/USI are thin (little English coverage — a genuine
reality, not a bug).

## Limits / honest notes

- **finviz ratings are US-listed/ADR only.** Foreign-listed peers (China/Korea/
  Taiwan local lines) have no finviz table; their analyst coverage comes only via
  the news feed.
- **Full proprietary sell-side PDFs are paywalled** and not collected; what's
  saved is the *ratings/price-target history* + published analyst-coverage news.
- Yahoo's analyst endpoint is crumb-blocked, so finviz is used instead.
