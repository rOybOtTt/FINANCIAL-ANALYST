# Agent 03 — Market Intel Agent

**Status:** ✅ Built and tested (live, incl. foreign listings)
**Script:** [`../market_agent.py`](../market_agent.py)
**Paired validator:** [Agent 03b — Market Data Validator](03b_market_validator.md)
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

For **our company (Amkor) and each competitor**, pull recent **news from
reliable newspapers / financial outlets** and **financial figures** (from Yahoo
Finance and a second source), then **validate the data** by cross-checking the
two financial sources and filtering news to trusted publishers only.

## Companies

Defined in [`../competitors.json`](../competitors.json) (our company + OSAT
peers: ASE, ChipMOS, JCET, Powertech, Tongfu). Override on the command line:

```bash
python market_agent.py                    # uses competitors.json
python market_agent.py AMKR ASX IMOS      # explicit tickers
python market_agent.py --news 6           # up to 6 news items per company
python market_agent.py --force-playwright # drive everything through a browser
```

Foreign listings work via Yahoo suffixes (e.g. `600584.SS`, `6239.TW`, `002156.SZ`).

## Data sources (no API key)

| Role | Source | Provides |
|------|--------|----------|
| Financials A | Yahoo chart `query1.finance.yahoo.com/v8/finance/chart/<T>` | price, prev close, day & 52-wk range, volume, name, exchange |
| Financials B | CNBC `quote.cnbc.com/.../restQuote` | price, **P/E**, change %, prev close |
| News | Yahoo Finance RSS `feeds.finance.yahoo.com/rss/2.0/headline?s=<T>` | headlines + links |

Plain HTTP (`urllib`) is used first and **falls back to a real Chromium browser
(Playwright)** automatically when a source blocks it (or always with
`--force-playwright`). Yahoo's authenticated `v7/quote` endpoint needs a crumb
and is intentionally avoided; the open endpoints above are stable.

## The "validate the data" core

- **Cross-source price check:** Yahoo price vs CNBC price must agree within 2%.
  Result is recorded as `AGREE` / `MISMATCH` / `single-source`.
- **News reliability:** every headline's URL is run through the **Source
  Validator (02b)**; `UNRELIABLE` outlets are dropped before saving.
- The **Market Data Validator (03b)** then re-checks everything at the end (auto).

## Output

```
data/market/
  _last_run.json                 # summary of the run
  _validation_report.json        # written by Agent 03b
  <TICKER>/
    snapshot.json                # full data: metrics, both raw sources, cross-check, news
    report.md                    # human-readable financial snapshot + reliable news
```

## Verified run

`python market_agent.py` (full default set) →
AMKR, ASX, IMOS, JCET (CNY), Powertech (TWD), Tongfu (CNY) all returned
financials with cross-source price **AGREE (0.0% diff)**; news filtered to
reliable outlets; validator overall **WARN** only because the Shenzhen-listed
Tongfu had no English-language reliable news (correctly a warning, not a fail).

## Future tweaks

- Add market cap / revenue / margins (needs a fundamentals source with a crumb
  or a Playwright scrape of the Yahoo statistics page).
- Add a third price source for triangulation when two disagree.
- Add analyst price-target / recommendation pull (Yahoo "Analysis" tab via browser).
