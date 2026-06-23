"""
AMKOR - Data Agent
==================

Pulls all SEC EDGAR filings from the last year for the companies you ask for,
and saves them under  AMKOR/data/<TICKER>/ .

EDGAR does NOT require an API key. The SEC's official API is free; it only
requires that you identify yourself with a contact email in the request header.

  - PRIMARY path : SEC official API over plain HTTP (urllib, no installs needed)
  - FALLBACK path: Playwright (a real browser) -- used automatically only if the
                   plain HTTP requests get blocked (e.g. HTTP 403 / rate limit).

USAGE
-----
  python data_agent.py AAPL MSFT NVDA
  python data_agent.py "Amkor Technology"
  python data_agent.py AAPL --days 365 --forms 10-K 10-Q 8-K
  python data_agent.py AAPL --force-playwright

  # no arguments -> it will ask you interactively
  python data_agent.py

ENV (optional)
--------------
  SEC_CONTACT   Contact email sent in the User-Agent header.
                Defaults to roybaibuch@gmail.com
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

CONTACT = os.environ.get("SEC_CONTACT", "roybaibuch@gmail.com")
USER_AGENT = f"AMKOR Data Agent ({CONTACT})"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik10}.json"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"
ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data"

SEC_MIN_INTERVAL = 0.25  # seconds between SEC requests (SEC asks <=10/sec)


# --------------------------------------------------------------------------
# Fetcher abstraction  (urllib primary, Playwright fallback)
# --------------------------------------------------------------------------

class FetchBlocked(Exception):
    """Raised when SEC blocks plain HTTP so we can switch to Playwright."""


class UrllibFetcher:
    """Plain HTTP using the Python standard library. No external installs."""

    name = "urllib (SEC API)"

    def __init__(self):
        self._last = 0.0

    def _throttle(self):
        wait = SEC_MIN_INTERVAL - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()

    def _open(self, url):
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError
        self._throttle()
        req = Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": url.split("/")[2],
        })
        try:
            resp = urlopen(req, timeout=30)
        except HTTPError as e:
            if e.code in (403, 401, 429):
                raise FetchBlocked(f"HTTP {e.code} for {url}")
            raise
        except URLError as e:
            raise FetchBlocked(f"URL error for {url}: {e.reason}")
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            import gzip
            data = gzip.decompress(data)
        return data

    def get_bytes(self, url):
        return self._open(url)

    def get_json(self, url):
        return json.loads(self._open(url).decode("utf-8"))


class PlaywrightFetcher:
    """Fetch via a real Chromium browser. Bypasses simple bot blocks."""

    name = "Playwright (browser)"

    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self._ctx = self._browser.new_context(user_agent=USER_AGENT)
        self._api = self._ctx.request
        self._last = 0.0

    def _throttle(self):
        wait = SEC_MIN_INTERVAL - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()

    def _open(self, url):
        self._throttle()
        resp = self._api.get(url, timeout=30000)
        if not resp.ok:
            raise RuntimeError(f"Playwright fetch failed HTTP {resp.status} for {url}")
        return resp.body()

    def get_bytes(self, url):
        return self._open(url)

    def get_json(self, url):
        return json.loads(self._open(url).decode("utf-8"))

    def close(self):
        try:
            self._browser.close()
            self._pw.stop()
        except Exception:
            pass


def make_playwright_fetcher():
    try:
        return PlaywrightFetcher()
    except ImportError:
        print("\n[!] Playwright is not installed. To enable the browser fallback:")
        print("      python -m pip install playwright")
        print("      python -m playwright install chromium\n")
        sys.exit(1)


# --------------------------------------------------------------------------
# EDGAR logic
# --------------------------------------------------------------------------

def slugify(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")


def load_ticker_map(fetcher):
    """ticker -> (cik_int, title). Also lets us match by company name."""
    raw = fetcher.get_json(TICKERS_URL)
    by_ticker = {}
    rows = raw.values() if isinstance(raw, dict) else raw
    for row in rows:
        by_ticker[row["ticker"].upper()] = (int(row["cik_str"]), row["title"])
    return by_ticker


def resolve_company(query, ticker_map):
    """Resolve a ticker symbol or company name to (cik_int, ticker, title)."""
    q = query.strip().upper()
    if q in ticker_map:
        cik, title = ticker_map[q]
        return cik, q, title
    # name search (case-insensitive substring)
    ql = query.strip().lower()
    matches = [
        (tk, cik, title)
        for tk, (cik, title) in ticker_map.items()
        if ql in title.lower()
    ]
    if not matches:
        return None
    # prefer the shortest title (closest match), stable
    matches.sort(key=lambda m: len(m[2]))
    tk, cik, title = matches[0]
    return cik, tk, title


def get_filings(fetcher, cik_int):
    """Return the recent-filings table from the submissions JSON."""
    cik10 = str(cik_int).zfill(10)
    data = fetcher.get_json(SUBMISSIONS_URL.format(cik10=cik10))
    recent = data.get("filings", {}).get("recent", {})
    keys = ("accessionNumber", "filingDate", "form",
            "primaryDocument", "primaryDocDescription", "reportDate", "items")
    n = len(recent.get("accessionNumber", []))
    rows = []
    for i in range(n):
        rows.append({k: (recent.get(k) or [None] * n)[i] for k in keys})
    return data.get("name", ""), rows


def filter_filings(rows, days, forms):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    forms_up = {f.upper() for f in forms} if forms else None
    out = []
    for r in rows:
        try:
            fdate = datetime.strptime(r["filingDate"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if fdate < cutoff:
            continue
        if forms_up and (r["form"] or "").upper() not in forms_up:
            continue
        out.append(r)
    return out


def download_filing(fetcher, cik_int, ticker, row, dest_root):
    accession = row["accessionNumber"]
    acc_nodash = accession.replace("-", "")
    primary = row["primaryDocument"]
    folder = os.path.join(
        dest_root,
        f"{row['filingDate']}_{slugify(row['form'])}_{accession}",
    )
    os.makedirs(folder, exist_ok=True)

    # save metadata
    with open(os.path.join(folder, "_meta.json"), "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2)

    if not primary:
        return folder, None  # nothing to download (rare)

    url = f"{ARCHIVE_BASE}/{cik_int}/{acc_nodash}/{primary}"
    try:
        blob = fetcher.get_bytes(url)
    except Exception as e:
        print(f"      ! could not download {primary}: {e}")
        return folder, None
    out_path = os.path.join(folder, primary)
    with open(out_path, "wb") as f:
        f.write(blob)
    return folder, out_path


# --------------------------------------------------------------------------
# Exhibits (investor presentations + management scripts live as EX-99.x)
# --------------------------------------------------------------------------

REPORT_FORMS = {"10-K", "20-F", "40-F", "10-Q"}
EARNINGS_8K_ITEMS = {"2.02", "7.01"}   # results of operations + Reg FD (presentations)

# Exhibits carrying presentations / earnings releases / prepared-remarks scripts.
_EXHIBIT_RE = re.compile(
    r"(ex[\-_]?99|exhibit99|present|slide|deck|investor|transcript|script|"
    r"remarks|prepared|earnings|results|[\-_]er[\-_0-9]|er[\-_]?99)", re.I)
_XBRL_SUFFIX = ("_htm.xml", "_lab.xml", "_pre.xml", "_def.xml", "_cal.xml", ".xsd")
_SKIP_EXACT = {"metalinks.json", "filingsummary.xml", "report.css", "show.js", "report.js"}
_SKIP_EXT = (".zip", ".css", ".js", ".gif", ".jpg", ".jpeg", ".png", ".svg", ".xml")


def filing_file_names(fetcher, cik_int, accession):
    acc = accession.replace("-", "")
    url = f"{ARCHIVE_BASE}/{cik_int}/{acc}/index.json"
    data = fetcher.get_json(url)
    return [it.get("name", "") for it in data.get("directory", {}).get("item", [])]


def pick_exhibits(names, primary, accession):
    """From a filing's file list, keep presentation/script/EX-99 exhibits + PDFs."""
    acc_nodash = accession.replace("-", "")
    out = []
    for name in names:
        low = name.lower()
        if not name or low in _SKIP_EXACT:
            continue
        if "index" in low or low == f"{acc_nodash}.txt":
            continue
        if low.endswith(_XBRL_SUFFIX) or low.endswith(_SKIP_EXT):
            continue
        if name == primary:
            continue
        if low.endswith(".pdf"):                       # decks are usually PDFs
            out.append(name)
        elif low.endswith((".htm", ".html", ".txt")) and _EXHIBIT_RE.search(low):
            out.append(name)
    return out


# Strong signals that a foreign 6-K (whose substance is the primary doc, e.g.
# ASE) is an earnings / investor item rather than a routine monthly-revenue note.
SIX_K_STRONG = ("earnings", "investor conference", "presentation")


def _peek_text(fetcher, cik_int, accession, primary, nbytes=150000):
    acc = accession.replace("-", "")
    url = f"{ARCHIVE_BASE}/{cik_int}/{acc}/{primary}"
    blob = fetcher.get_bytes(url)[:nbytes]
    text = blob.decode("utf-8", "ignore")
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return text.lower()


def assess_filing(fetcher, cik_int, row, smart, want_exhibits):
    """Return (keep, exhibit_names). Reports always kept; 8-K filtered by items;
    6-K kept if it carries a substantive exhibit (TSMC pattern) OR its primary
    doc reads as earnings/investor content (ASE pattern)."""
    form = (row["form"] or "").upper()
    primary = row.get("primaryDocument")

    if form in REPORT_FORMS:
        keep = True
    elif form == "8-K":
        items = row.get("items") or ""
        keep = (not smart) or any(it in items for it in EARNINGS_8K_ITEMS)
    elif form == "6-K":
        keep = True  # refined below
    else:
        keep = not smart

    if not keep:
        return False, []

    exhibits = []
    if want_exhibits or form == "6-K":
        try:
            names = filing_file_names(fetcher, cik_int, row["accessionNumber"])
            exhibits = pick_exhibits(names, primary, row["accessionNumber"])
        except Exception:
            exhibits = []

    if smart and form == "6-K" and not exhibits:
        # ASE pattern: substance is the primary doc; content-gate to earnings/investor
        try:
            text = _peek_text(fetcher, cik_int, row["accessionNumber"], primary)
            keep = any(kw in text for kw in SIX_K_STRONG)
        except Exception:
            keep = False
    return keep, exhibits


def download_exhibit(fetcher, cik_int, accession, name, folder):
    acc = accession.replace("-", "")
    url = f"{ARCHIVE_BASE}/{cik_int}/{acc}/{name}"
    blob = fetcher.get_bytes(url)
    out_path = os.path.join(folder, "exhibit_" + os.path.basename(name))
    with open(out_path, "wb") as f:
        f.write(blob)
    return out_path


# --------------------------------------------------------------------------
# Structured fundamentals (SEC companyfacts XBRL - no API key)
# --------------------------------------------------------------------------

# Concept name candidates span US-GAAP (10-K) and IFRS (20-F foreign filers).
FIN_CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "SalesRevenueNet", "Revenue"],
    "gross_profit": ["GrossProfit"],
    "cost_of_revenue": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfSales"],
    "operating_income": ["OperatingIncomeLoss", "ProfitLossFromOperatingActivities"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "eps_diluted": ["EarningsPerShareDiluted", "DilutedEarningsLossPerShare"],
    "rd_expense": ["ResearchAndDevelopmentExpense"],
    "op_cash_flow": ["NetCashProvidedByUsedInOperatingActivities",
                     "CashFlowsFromUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment",
              "PurchaseOfPropertyPlantAndEquipment"],
    "assets": ["Assets"],
    "equity": ["StockholdersEquity", "Equity", "EquityAttributableToOwnersOfParent"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue", "CashAndCashEquivalents"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt", "NoncurrentBorrowings"],
}
INSTANT_KEYS = {"assets", "equity", "cash", "long_term_debt"}   # balance-sheet snapshots
ANNUAL_FORMS = ("10-K", "20-F", "40-F")


def _concept_node(allfacts, names):
    for name in names:
        for tax in ("us-gaap", "ifrs-full"):
            node = allfacts.get(tax, {}).get(name)
            if node:
                return node
    return None


def _merged_annual_series(allfacts, names, instant):
    """Merge the annual series across ALL candidate concepts (US-GAAP + IFRS) in
    priority order, filling years that a higher-priority concept is missing.

    This is essential for issuers that switched their XBRL tag over time. Example:
    NVIDIA reports revenue under RevenueFromContractWithCustomerExcludingAssessedTax
    only through FY2022, then carries the full series under 'Revenues' (incl.
    FY2024 $60.9B, FY2025 $130.5B, FY2026 $215.9B). Taking only the first matching
    concept truncated every recent year. Higher-priority concepts win on overlap,
    so the definition stays consistent where both tags report the same year."""
    merged, ukey_out = {}, None
    for name in names:
        for tax in ("us-gaap", "ifrs-full"):
            node = allfacts.get(tax, {}).get(name)
            if not node:
                continue
            s, ukey = _annual_series(node, instant)
            if s and ukey and ukey != "USD/shares" and ukey_out is None:
                ukey_out = ukey
            for yr, val in s.items():
                merged.setdefault(yr, val)   # first (highest-priority) concept wins
    return merged, ukey_out


def _annual_series(node, instant):
    """{fiscal_year: value} from annual filings, latest-filed wins per year."""
    units = node.get("units", {})
    ukey = next(iter(units), None)
    if not ukey:
        return {}, None
    picked = {}
    for r in units[ukey]:
        form = r.get("form", "")
        if not any(form.startswith(f) for f in ANNUAL_FORMS):
            continue
        end = r.get("end")
        if not end:
            continue
        if not instant:
            start = r.get("start")
            if not start:
                continue
            try:
                d0 = datetime.strptime(start, "%Y-%m-%d").date()
                d1 = datetime.strptime(end, "%Y-%m-%d").date()
            except ValueError:
                continue
            if not (350 <= (d1 - d0).days <= 380):   # keep ~full-year periods only
                continue
        yr = end[:4]
        filed = r.get("filed", "")
        if yr not in picked or filed >= picked[yr][1]:
            picked[yr] = (r.get("val"), filed)
    return {y: v for y, (v, _) in picked.items()}, ukey


def extract_financials(facts, ticker, cik):
    allfacts = facts.get("facts", {})
    series, currency = {}, "USD"
    for key, names in FIN_CONCEPTS.items():
        s, ukey = _merged_annual_series(allfacts, names, key in INSTANT_KEYS)
        series[key] = s
        if key == "revenue" and ukey and ukey != "USD/shares":
            currency = ukey

    base = series.get("revenue") or series.get("net_income") or {}
    years = sorted(base.keys(), reverse=True)[:5]
    rev = series.get("revenue", {})

    def pct(a, b):
        return round(a / b * 100, 1) if (a is not None and b) else None

    annual = {}
    for y in years:
        g = lambda k: series.get(k, {}).get(y)
        revenue, gp, oi, ni = g("revenue"), g("gross_profit"), g("operating_income"), g("net_income")
        ocf, capex = g("op_cash_flow"), g("capex")
        prev_rev = rev.get(str(int(y) - 1)) if y.isdigit() else None
        annual[y] = {
            "revenue": revenue, "revenue_yoy_pct": pct(revenue - prev_rev, prev_rev) if (revenue and prev_rev) else None,
            "gross_profit": gp, "gross_margin_pct": pct(gp, revenue),
            "operating_income": oi, "operating_margin_pct": pct(oi, revenue),
            "net_income": ni, "net_margin_pct": pct(ni, revenue),
            "eps_diluted": g("eps_diluted"), "rd_expense": g("rd_expense"),
            "operating_cash_flow": ocf, "capex": capex,
            "free_cash_flow": (ocf - capex) if (ocf is not None and capex is not None) else None,
            "assets": g("assets"), "equity": g("equity"),
            "cash": g("cash"), "long_term_debt": g("long_term_debt"),
        }
    return {"ticker": ticker, "cik": cik, "entity": facts.get("entityName"),
            "currency": currency, "source": "SEC companyfacts XBRL",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "annual": annual}


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def run(companies, days, forms, force_playwright, skip_validate=False,
        want_exhibits=False, smart_current=False):
    os.makedirs(DATA_DIR, exist_ok=True)

    if force_playwright:
        fetcher = make_playwright_fetcher()
    else:
        fetcher = UrllibFetcher()

    print(f"Contact / User-Agent : {USER_AGENT}")
    print(f"Fetcher              : {fetcher.name}")
    print(f"Lookback             : last {days} days")
    print(f"Forms                : {', '.join(forms) if forms else 'ALL'}")
    print(f"Exhibits             : {'EX-99 presentations/scripts' if want_exhibits else 'off'}")
    print(f"Current-report filter: {'earnings/investor only' if smart_current else 'off'}")
    print(f"Output               : {DATA_DIR}\n")

    def with_fallback(call):
        """Run an SEC call; on block, transparently switch to Playwright."""
        nonlocal fetcher
        try:
            return call(fetcher)
        except FetchBlocked as e:
            print(f"[!] Plain HTTP blocked ({e}). Switching to Playwright...")
            fetcher = make_playwright_fetcher()
            return call(fetcher)

    ticker_map = with_fallback(load_ticker_map)
    print(f"Loaded {len(ticker_map):,} tickers from SEC.\n")

    summary = []
    for company in companies:
        resolved = resolve_company(company, ticker_map)
        if not resolved:
            print(f"### {company}: NOT FOUND on EDGAR. Skipping.")
            summary.append({"query": company, "found": False, "filings": 0})
            continue

        cik, ticker, title = resolved
        print(f"### {company} -> {ticker} | CIK {cik} | {title}")

        name, rows = with_fallback(lambda f: get_filings(f, cik))
        recent = filter_filings(rows, days, forms)
        print(f"    {len(recent)} filing(s) in the last {days} days.")

        # assess each filing (keep + which exhibits) when filtering / pulling exhibits
        if smart_current or want_exhibits:
            assessed = []
            for row in recent:
                keep, exhibits = with_fallback(
                    lambda f: assess_filing(f, cik, row, smart_current, want_exhibits))
                if keep:
                    assessed.append((row, exhibits))
            print(f"    -> {len(assessed)} kept "
                  f"({'reports + earnings/investor' if smart_current else 'all'}; "
                  f"{sum(len(e) for _, e in assessed)} exhibit(s)).")
        else:
            assessed = [(row, []) for row in recent]

        dest_root = os.path.join(DATA_DIR, slugify(ticker))
        os.makedirs(dest_root, exist_ok=True)

        saved = []
        for row, exhibits in assessed:
            tag = f"  [+{len(exhibits)} exhibit]" if exhibits else ""
            print(f"    - {row['filingDate']}  {row['form']:<8} {row['accessionNumber']}{tag}")
            folder, path = with_fallback(
                lambda f: download_filing(f, cik, ticker, row, dest_root)
            )
            ex_saved = []
            for name_ex in exhibits:
                try:
                    ep = with_fallback(
                        lambda f: download_exhibit(f, cik, row["accessionNumber"], name_ex, folder))
                    ex_saved.append(os.path.basename(ep))
                except Exception as e:
                    print(f"        ! exhibit {name_ex} failed: {e}")
            saved.append({**row, "saved_to": path, "exhibits": ex_saved})

        # per-company manifest
        with open(os.path.join(dest_root, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({
                "query": company, "ticker": ticker, "cik": cik,
                "company": title, "lookback_days": days,
                "forms": forms or "ALL",
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "filings": saved,
            }, f, indent=2)

        # structured fundamentals via SEC companyfacts (no key; may 404 for
        # foreign / non-SEC filers, which is handled gracefully)
        fin_years = 0
        try:
            cik10 = str(cik).zfill(10)
            facts = with_fallback(lambda f: f.get_json(COMPANYFACTS_URL.format(cik10=cik10)))
            financials = extract_financials(facts, ticker, cik)
            with open(os.path.join(dest_root, "financials.json"), "w", encoding="utf-8") as f:
                json.dump(financials, f, indent=2)
            fin_years = len(financials["annual"])
            print(f"    fundamentals: {fin_years} fiscal year(s) saved (SEC companyfacts)")
        except Exception as e:
            print(f"    fundamentals: none ({e}) - likely a foreign / non-SEC filer")

        summary.append({"query": company, "ticker": ticker, "cik": cik,
                        "found": True, "filings": len(recent), "fundamentals_years": fin_years})
        print()

    # global run summary
    with open(os.path.join(DATA_DIR, "_last_run.json"), "w", encoding="utf-8") as f:
        json.dump({
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "lookback_days": days, "forms": forms or "ALL",
            "results": summary,
        }, f, indent=2)

    if isinstance(fetcher, PlaywrightFetcher):
        fetcher.close()

    print("Done. Summary:")
    for s in summary:
        if s["found"]:
            print(f"  {s['query']:<24} {s['ticker']:<8} {s['filings']} filing(s)")
        else:
            print(f"  {s['query']:<24} NOT FOUND")

    # --- Auto-activate the Validator Agent (01b) ---------------------------
    if not skip_validate:
        try:
            from validator_agent import validate_run
            ok, _ = validate_run(DATA_DIR)
            if not ok:
                print("\n[!] Validator reported FAILURES - check the report above.")
        except Exception as e:
            print(f"\n[!] Validator could not run: {e}")


def parse_args(argv):
    p = argparse.ArgumentParser(description="AMKOR Data Agent - pull EDGAR filings.")
    p.add_argument("companies", nargs="*", help="Tickers or company names.")
    p.add_argument("--days", type=int, default=365, help="Lookback window (default 365).")
    p.add_argument("--forms", nargs="*", default=None,
                   help="Filter by form type, e.g. 10-K 10-Q 8-K. Default: all.")
    p.add_argument("--force-playwright", action="store_true",
                   help="Use the browser path from the start.")
    p.add_argument("--no-validate", action="store_true",
                   help="Skip auto-running the Validator Agent afterward.")
    p.add_argument("--exhibits", action="store_true",
                   help="Also download EX-99 exhibits (investor presentations / earnings releases / scripts).")
    p.add_argument("--smart-current", action="store_true",
                   help="Keep only earnings/investor-related 8-K (items 2.02/7.01) and 6-K with substantive exhibits.")
    return p.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    companies = args.companies
    if not companies:
        raw = input("Which companies? (tickers or names, comma/space separated)\n> ")
        companies = [c.strip() for c in re.split(r"[,\n]+", raw) if c.strip()]
    if not companies:
        print("No companies given. Exiting.")
        return
    run(companies, args.days, args.forms, args.force_playwright, args.no_validate,
        want_exhibits=args.exhibits, smart_current=args.smart_current)


if __name__ == "__main__":
    main()
