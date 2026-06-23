# Agent 01 — Data Agent

**Status:** ✅ Built and tested (live against AMKR)
**Script:** [`../data_agent.py`](../data_agent.py)
**Owner:** Roy (roybaibuch@gmail.com)

---

## Goal

Pull **all SEC EDGAR filings from the last year** for any companies the user asks
for, and save them under the `AMKOR/data/` folder for later analysis.

## Inputs

| Input | How | Default |
|-------|-----|---------|
| Companies | CLI args (tickers or names) or interactive prompt | — (required) |
| Lookback window | `--days N` | `365` |
| Report types | `--forms 10-K 10-Q 8-K ...` | all forms |
| Force browser path | `--force-playwright` | off |
| Contact email | env var `SEC_CONTACT` | `roybaibuch@gmail.com` |

## Data source

- **SEC EDGAR** — the official, free U.S. government filings database.
- **No API key exists or is needed.** EDGAR only requires a contact email in the
  request `User-Agent` header (rule: max ~10 requests/sec).

## How it fetches (two paths)

1. **PRIMARY — `urllib` (SEC API):** plain HTTP using Python's standard library.
   No installs required. This is the normal path.
2. **FALLBACK — Playwright (real browser):** triggers **automatically** if the
   plain HTTP path is blocked (HTTP 403 / 401 / 429). Requires a one-time setup:
   ```
   python -m pip install playwright
   python -m playwright install chromium
   ```

## How to run

```bash
python data_agent.py AAPL MSFT NVDA          # by ticker
python data_agent.py "Amkor Technology"       # by company name
python data_agent.py AMKR --forms 10-K 10-Q   # only certain report types
python data_agent.py AMKR --days 730           # last 2 years
python data_agent.py                          # asks interactively
```

## Structured fundamentals (SEC companyfacts XBRL)

In addition to the filing documents, Agent 01 pulls the SEC **companyfacts** API
(`data.sec.gov/api/xbrl/companyfacts/CIK##########.json`) — also **no key** — and
extracts a clean annual history (last 5 fiscal years) into `financials.json`:

- revenue + YoY growth, gross / operating / net **margins**, net income, diluted EPS
- R&D, operating cash flow, capex, **free cash flow**
- cash, long-term debt, equity

Works for US filers (10-K, US-GAAP) **and** foreign filers (20-F, IFRS — e.g. ASE
in TWD). Foreign-specific tags that don't map (e.g. some capex) show `n/a` rather
than crashing. Pure non-SEC filers (Shanghai/Shenzhen listings) have no
companyfacts and are skipped gracefully. **This is what feeds real margins/EPS to
the analyst agents (04–08)** — it closed the "we can't see the numbers" gap.

## Output layout

```
AMKOR/data/
  _last_run.json                               # summary of the whole run
  <TICKER>/
    manifest.json                              # every filing pulled for this company
    financials.json                            # 5yr revenue/margins/EPS/cash-flow (companyfacts)
    <date>_<form>_<accession>/
        <primary_document>.htm                 # the actual report (10-K, 10-Q, 8-K...)
        _meta.json                             # form, filing date, report date, accession
```

## Pipeline (what the script does internally)

1. Download SEC's `company_tickers.json` and build a ticker → CIK lookup.
2. Resolve each requested company to its CIK (exact ticker, else name substring match).
3. Fetch the company's `submissions/CIK##########.json`.
4. Filter filings to the lookback window (and form types, if given).
5. Download each filing's **primary document** + write metadata.
6. Write a per-company `manifest.json` and a global `_last_run.json`.

## Verified run

`python data_agent.py AMKR --forms 10-K 10-Q 8-K` →
**20 filings** retrieved (1× 10-K, 3× 10-Q, 16× 8-K), saved to `AMKOR/data/AMKR/`.

## Known limitations / future tweaks

- Currently downloads only the **primary document** of each filing (the main
  report), not every exhibit.
- Could add: pull exhibits, extract the structured XBRL financial facts
  (`companyfacts` API), or export a flat CSV index across all companies.
