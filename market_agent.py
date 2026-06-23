"""
AMKOR - Market Intel Agent  (Agent 03)
======================================

For our company (Amkor) AND each competitor, pulls:
  - FINANCIALS from two independent sources (Yahoo Finance + CNBC) so the data
    can be cross-validated, plus
  - NEWS from reliable newspapers / financial outlets (Yahoo Finance RSS),
    filtered through the Source Validator (02b) so only trusted sources survive.

Then the Market Data Validator (03b) runs automatically and confirms the two
financial sources agree and the news sources are reliable.

USAGE
-----
  python market_agent.py                       # uses competitors.json
  python market_agent.py AMKR ASX IMOS         # explicit tickers
  python market_agent.py --news 6              # up to 6 news items per company
  python market_agent.py --force-playwright    # drive everything through a browser

DATA SOURCES (no API key required)
  A) Yahoo chart  : query1.finance.yahoo.com/v8/finance/chart/<TICKER>
  B) CNBC quote   : quote.cnbc.com/quote-html-webservice/...
  News            : feeds.finance.yahoo.com/rss/2.0/headline?s=<TICKER>
Plain HTTP (urllib) is used first; it falls back to a real Chromium browser
(Playwright) automatically when a source blocks it, or always with --force-playwright.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import quote_plus

import source_validator as sv

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_DIR = os.path.join(HERE, "data", "market")
COMPETITORS = os.path.join(HERE, "competitors.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0 Safari/537.36")

YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1d&interval=1d"
CNBC_QUOTE = ("https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/"
              "symbol?symbols={t}&requestMethod=itv&fund=1&exthrs=1&output=json")
YAHOO_NEWS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={t}&region=US&lang=en-US"


# --------------------------------------------------------------------------
# Fetch: urllib primary, Playwright fallback
# --------------------------------------------------------------------------

class FetchBlocked(Exception):
    pass


def _urllib_get(url):
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    req = Request(url, headers={"User-Agent": UA})
    try:
        with urlopen(req, timeout=20) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                import gzip
                data = gzip.decompress(data)
            return data.decode("utf-8", errors="ignore")
    except HTTPError as e:
        if e.code in (401, 403, 429, 202):
            raise FetchBlocked(f"HTTP {e.code}")
        raise
    except URLError as e:
        raise FetchBlocked(str(e.reason))


class _BrowserReq:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(headless=True)
        self._ctx = self._b.new_context(user_agent=UA)

    def get(self, url):
        r = self._ctx.request.get(url, timeout=25000)
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status}")
        return r.text()

    def close(self):
        try:
            self._b.close(); self._pw.stop()
        except Exception:
            pass


class Fetcher:
    def __init__(self, force=False):
        self.force = force
        self.browser = None

    def _ensure(self):
        if self.browser is None:
            try:
                self.browser = _BrowserReq()
            except ImportError:
                print("\n[!] Playwright not installed:")
                print("      python -m pip install playwright")
                print("      python -m playwright install chromium\n")
                sys.exit(1)
        return self.browser

    def get(self, url):
        if self.force or self.browser is not None:
            return self._ensure().get(url)
        try:
            return _urllib_get(url)
        except FetchBlocked as e:
            print(f"      [!] blocked ({e}); switching to Playwright")
            return self._ensure().get(url)

    def close(self):
        if self.browser:
            self.browser.close()


# --------------------------------------------------------------------------
# Financial sources
# --------------------------------------------------------------------------

def fin_yahoo(ticker, fetcher):
    try:
        raw = fetcher.get(YAHOO_CHART.format(t=quote_plus(ticker)))
        meta = json.loads(raw)["chart"]["result"][0]["meta"]
    except Exception as e:
        return {"error": str(e)}
    return {
        "price": meta.get("regularMarketPrice"),
        "currency": meta.get("currency"),
        "previous_close": meta.get("chartPreviousClose"),
        "day_high": meta.get("regularMarketDayHigh"),
        "day_low": meta.get("regularMarketDayLow"),
        "week52_high": meta.get("fiftyTwoWeekHigh"),
        "week52_low": meta.get("fiftyTwoWeekLow"),
        "volume": meta.get("regularMarketVolume"),
        "name": meta.get("longName") or meta.get("shortName"),
        "exchange": meta.get("fullExchangeName"),
    }


def _cnbc_num(x):
    if x is None:
        return None
    s = re.sub(r"[,%+]", "", str(x))
    try:
        return float(s)
    except ValueError:
        return None


def fin_cnbc(ticker, fetcher):
    try:
        raw = fetcher.get(CNBC_QUOTE.format(t=quote_plus(ticker)))
        q = json.loads(raw)["FormattedQuoteResult"]["FormattedQuote"][0]
    except Exception as e:
        return {"error": str(e)}
    return {
        "price": _cnbc_num(q.get("last")),
        "previous_close": _cnbc_num(q.get("previous_day_closing")),
        "pe": _cnbc_num(q.get("pe")),
        "change_pct": q.get("change_pct"),
        "volume": _cnbc_num(q.get("volume")),
        "name": q.get("name"),
    }


def consolidate(yahoo, cnbc):
    """Build the agreed metric set, preferring Yahoo, filling from CNBC."""
    def pick(*vals):
        for v in vals:
            if v is not None:
                return v
        return None
    price = pick(yahoo.get("price"), cnbc.get("price"))
    prev = pick(yahoo.get("previous_close"), cnbc.get("previous_close"))
    change_pct = None
    if price is not None and prev:
        change_pct = round((price - prev) / prev * 100, 2)
    return {
        "name": pick(yahoo.get("name"), cnbc.get("name")),
        "price": price,
        "currency": yahoo.get("currency"),
        "previous_close": prev,
        "change_pct": change_pct,
        "pe": cnbc.get("pe"),
        "day_low": yahoo.get("day_low"),
        "day_high": yahoo.get("day_high"),
        "week52_low": yahoo.get("week52_low"),
        "week52_high": yahoo.get("week52_high"),
        "volume": pick(yahoo.get("volume"), cnbc.get("volume")),
        "exchange": yahoo.get("exchange"),
    }


# --------------------------------------------------------------------------
# News
# --------------------------------------------------------------------------

_ITEM = re.compile(r"<item>(.*?)</item>", re.S)
_TAG = lambda name, s: (re.search(rf"<{name}>(.*?)</{name}>", s, re.S) or [None, ""])[1]


def fetch_news(ticker, fetcher, registry, max_items):
    try:
        raw = fetcher.get(YAHOO_NEWS.format(t=quote_plus(ticker)))
    except Exception as e:
        print(f"      news fetch failed: {e}")
        return []
    kept = []
    for block in _ITEM.findall(raw):
        title = re.sub(r"<!\[CDATA\[|\]\]>", "", _TAG("title", block)).strip()
        link = _TAG("link", block).strip()
        pub = _TAG("pubDate", block).strip()
        if not link:
            continue
        v = sv.validate(link, registry=registry)
        if v["verdict"] == "UNRELIABLE":
            continue
        kept.append({"title": title, "url": link, "published": pub,
                     "source": v["registry_name"] or v["domain"],
                     "reliability": v["verdict"], "score": v["score"]})
        if len(kept) >= max_items:
            break
    return kept


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def load_companies(args_tickers):
    if args_tickers:
        return [{"ticker": t.upper(), "name": t.upper(), "role": "competitor"}
                for t in args_tickers]
    with open(COMPETITORS, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["companies"]


def price_check(yahoo, cnbc):
    ya, cn = yahoo.get("price"), cnbc.get("price")
    if ya is None or cn is None:
        return "single-source", None
    diff = abs(ya - cn) / ya if ya else 1
    return ("AGREE" if diff <= 0.02 else "MISMATCH"), round(diff * 100, 3)


def run(companies, max_news, force_playwright):
    registry = sv.load_registry()
    os.makedirs(MARKET_DIR, exist_ok=True)
    fetcher = Fetcher(force_playwright)

    print(f"Companies : {', '.join(c['ticker'] for c in companies)}")
    print(f"Fetcher   : {'Playwright (forced)' if force_playwright else 'urllib (-> Playwright on block)'}")
    print(f"News/co   : up to {max_news}\n")

    stamp = datetime.now(timezone.utc).isoformat()
    summary = []
    for c in companies:
        tk = c["ticker"]
        print(f"### {tk}  ({c.get('name','')}, {c.get('role','')})")

        yahoo = fin_yahoo(tk, fetcher)
        cnbc = fin_cnbc(tk, fetcher)
        metrics = consolidate(yahoo, cnbc)
        verdict, diff = price_check(yahoo, cnbc)
        news = fetch_news(tk, fetcher, registry, max_news)

        if metrics.get("price") is not None:
            print(f"    price {metrics['price']} {metrics.get('currency') or ''} "
                  f"| PE {metrics.get('pe')} | chg {metrics.get('change_pct')}% "
                  f"| cross-source: {verdict}" + (f" ({diff}%)" if diff is not None else ""))
        else:
            print("    [!] no price data")
        print(f"    {len(news)} reliable news item(s)")

        snapshot = {
            "ticker": tk, "name": c.get("name"), "role": c.get("role"),
            "generated_utc": stamp,
            "metrics": metrics,
            "financials": {"yahoo": yahoo, "cnbc": cnbc,
                           "price_cross_check": {"result": verdict, "diff_pct": diff}},
            "news": news,
        }
        out_dir = os.path.join(MARKET_DIR, tk.replace(".", "_"))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "snapshot.json"), "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        _write_md(out_dir, snapshot)
        summary.append({"ticker": tk, "price": metrics.get("price"),
                        "cross_check": verdict, "news": len(news)})
        print()

    fetcher.close()

    with open(os.path.join(MARKET_DIR, "_last_run.json"), "w", encoding="utf-8") as f:
        json.dump({"generated_utc": stamp, "results": summary}, f, indent=2)

    # auto-run the validator (03b)
    try:
        from market_validator import validate_run
        ok, _ = validate_run(MARKET_DIR)
        if not ok:
            print("\n[!] Market validator reported FAILURES - see above.")
    except Exception as e:
        print(f"\n[!] Market validator could not run: {e}")


def _write_md(out_dir, snap):
    m = snap["metrics"]
    cc = snap["financials"]["price_cross_check"]
    lines = [
        f"# {snap['ticker']} - {m.get('name') or snap.get('name')}",
        f"_{snap.get('role','')} | generated {snap['generated_utc']}_", "",
        "## Financial snapshot",
        f"- Price: **{m.get('price')} {m.get('currency') or ''}** "
        f"(change {m.get('change_pct')}%)",
        f"- Cross-source check (Yahoo vs CNBC): **{cc['result']}**"
        + (f" (diff {cc['diff_pct']}%)" if cc['diff_pct'] is not None else ""),
        f"- P/E: {m.get('pe')}",
        f"- Previous close: {m.get('previous_close')}",
        f"- Day range: {m.get('day_low')} - {m.get('day_high')}",
        f"- 52-week range: {m.get('week52_low')} - {m.get('week52_high')}",
        f"- Volume: {m.get('volume')}",
        f"- Exchange: {m.get('exchange')}", "",
        "## Reliable news", "",
    ]
    if snap["news"]:
        for n in snap["news"]:
            lines.append(f"- [{n['title']}]({n['url']})")
            lines.append(f"  - {n['source']} ({n['reliability']} {n['score']}/100) | {n['published']}")
    else:
        lines.append("_No reliable news items found._")
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description="AMKOR Market Intel Agent (03).")
    p.add_argument("tickers", nargs="*", help="Tickers (default: competitors.json).")
    p.add_argument("--news", type=int, default=5, help="Max news items per company (default 5).")
    p.add_argument("--force-playwright", action="store_true", help="Use the browser from the start.")
    args = p.parse_args()
    companies = load_companies(args.tickers)
    run(companies, args.news, args.force_playwright)


if __name__ == "__main__":
    main()
