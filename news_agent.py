"""
AMKOR - News & Analyst Harvester  (Agent 03c)
=============================================

For our company (Amkor) and every competitor, collects:
  - NEWS from reliable sources (Google News RSS, ~100 items/company, each item's
    publisher validated by the Source Validator 02b -> only legit outlets kept).
  - ANALYST coverage:
      * structured sell-side RATINGS (firm / action / rating change / price
        target) scraped from finviz via Playwright (US-listed / ADR tickers), and
      * the analyst-action NEWS subset (upgrades / downgrades / price targets /
        initiations) filtered from the news feed.

Company set comes from competitors.json (Amkor + all competitors). The legit
research firms cited in the AMKR guide files (Yole, IDTechEx, DIGITIMES,
TrendForce, Counterpoint, Omdia, Mordor, Grand View, MarketsandMarkets) are in
reliable_sources.json so their coverage is recognised as reliable.

Usage:
  python news_agent.py                      # all companies in competitors.json
  python news_agent.py AMKR MU TSM          # explicit tickers
  python news_agent.py --news 40            # max reliable news items per company
  python news_agent.py --no-analysts        # skip finviz analyst-ratings scrape

Output (per company):
  data/market/<TICKER>/
    news.json            # all reliable news items (title, source, url, date, analyst-flag)
    analyst_ratings.json # finviz sell-side ratings history (US-listed only)
    news_report.md       # human-readable news + analyst summary
"""

import argparse
import html as html_mod
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus, urlparse

import source_validator as sv

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_DIR = os.path.join(HERE, "data", "market")
COMPETITORS = os.path.join(HERE, "competitors.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0 Safari/537.36")

GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
FINVIZ = "https://finviz.com/quote.ashx?t={t}"

# Keywords that mark a news item as analyst coverage / a research note.
ANALYST_KW = ("upgrade", "downgrade", "price target", "initiat", "reiterat",
              "analyst", "rating", "overweight", "underweight", "outperform",
              "underperform", "buy rating", "sell rating", "hold rating",
              "raises", "lowers", "cuts target", "boosts", "coverage")

# Tickers with a non-US suffix won't be on finviz; only try the US-listed/ADR ones.
def _us_listed(ticker):
    return "." not in ticker


# --------------------------------------------------------------------------
# News (Google News RSS, validated)
# --------------------------------------------------------------------------

def _clean(t):
    return html_mod.unescape(re.sub(r"<[^>]+>", "", t or "")).strip()


def fetch_news(name, ticker, registry, max_items):
    from urllib.request import Request, urlopen
    # strip parenthetical aliases from the name for a cleaner search query
    qname = re.sub(r"\s*\(.*?\)", "", name).strip() or name
    if _us_listed(ticker):
        query = f"{qname} ({ticker}) stock"          # US: name + ticker
    else:
        query = f"{qname} semiconductor"             # foreign: name only (Yahoo suffix would hurt)
    url = GNEWS.format(q=quote_plus(query))
    try:
        xml = urlopen(Request(url, headers={"User-Agent": UA}), timeout=25).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"      news fetch failed: {e}")
        return []
    kept = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title = _clean((re.search(r"<title>(.*?)</title>", block, re.S) or [None, ""])[1])
        link = _clean((re.search(r"<link>(.*?)</link>", block, re.S) or [None, ""])[1])
        pub = _clean((re.search(r"<pubDate>(.*?)</pubDate>", block, re.S) or [None, ""])[1])
        sm = re.search(r'<source url="([^"]*)"[^>]*>(.*?)</source>', block, re.S)
        src_url = sm.group(1) if sm else ""
        src_name = _clean(sm.group(2)) if sm else ""
        if not src_url:
            continue
        v = sv.validate(src_url, registry=registry)
        if v["verdict"] == "UNRELIABLE":
            continue
        low = title.lower()
        is_analyst = any(k in low for k in ANALYST_KW)
        kept.append({"title": title, "url": link, "published": pub,
                     "source": v["registry_name"] or src_name or v["domain"],
                     "domain": v["domain"], "reliability": v["verdict"],
                     "score": v["score"], "analyst_item": is_analyst})
        if len(kept) >= max_items:
            break
    return kept


# --------------------------------------------------------------------------
# Analyst ratings (finviz via Playwright)
# --------------------------------------------------------------------------

class _Browser:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(headless=True)
        self._ctx = self._b.new_context(user_agent=UA)

    def ratings_table_text(self, ticker):
        pg = self._ctx.new_page()
        try:
            pg.goto(FINVIZ.format(t=ticker), timeout=30000, wait_until="domcontentloaded")
            pg.wait_for_timeout(3500)
            try:
                return pg.eval_on_selector("table.js-table-ratings", "el => el.innerText")
            except Exception:
                return ""
        finally:
            pg.close()

    def close(self):
        try:
            self._b.close(); self._pw.stop()
        except Exception:
            pass


def parse_ratings(text):
    """finviz ratings table innerText -> list of {date, action, firm, rating, price_target}."""
    out = []
    for line in (text or "").splitlines():
        cells = [c.strip() for c in line.split("\t") if c.strip() != ""]
        if len(cells) < 3:
            continue
        if cells[0].lower() in ("date",) or cells[1].lower() == "action":
            continue
        # pad to 5 columns
        cells = (cells + ["", "", "", "", ""])[:5]
        out.append({"date": cells[0], "action": cells[1], "firm": cells[2],
                    "rating": cells[3], "price_target": cells[4]})
    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def load_companies(args_tickers):
    if args_tickers:
        return [{"ticker": t.upper(), "name": t.upper(), "role": "competitor"} for t in args_tickers]
    with open(COMPETITORS, encoding="utf-8") as f:
        return json.load(f)["companies"]


def write_report(out_dir, company, news, ratings):
    lines = [f"# {company['ticker']} - {company.get('name','')}  (news & analysts)",
             f"_{company.get('role','')} | generated {datetime.now(timezone.utc).isoformat()}_", ""]
    if ratings:
        lines += ["## Analyst ratings (finviz sell-side history)", "",
                  "| Date | Action | Firm | Rating | Price target |",
                  "|------|--------|------|--------|--------------|"]
        for r in ratings[:25]:
            lines.append(f"| {r['date']} | {r['action']} | {r['firm']} | {r['rating']} | {r['price_target']} |")
        lines.append("")
    analyst_news = [n for n in news if n["analyst_item"]]
    if analyst_news:
        lines += ["## Analyst-coverage news", ""]
        for n in analyst_news:
            lines.append(f"- [{n['title']}]({n['url']}) — {n['source']} ({n['published']})")
        lines.append("")
    lines += [f"## Reliable news ({len(news)} items)", ""]
    for n in news:
        flag = " _(analyst)_" if n["analyst_item"] else ""
        lines.append(f"- [{n['title']}]({n['url']}) — {n['source']} "
                     f"({n['reliability']} {n['score']}){flag} | {n['published']}")
    with open(os.path.join(out_dir, "news_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run(companies, max_news, do_analysts):
    registry = sv.load_registry()
    os.makedirs(MARKET_DIR, exist_ok=True)
    browser = None
    stamp = datetime.now(timezone.utc).isoformat()
    summary = []

    print(f"Companies : {', '.join(c['ticker'] for c in companies)}")
    print(f"News/co   : up to {max_news}   Analyst ratings: {'on' if do_analysts else 'off'}\n")

    try:
        for c in companies:
            tk = c["ticker"]
            print(f"### {tk}  ({c.get('name','')})")
            news = fetch_news(c.get("name", tk), tk, registry, max_news)
            n_analyst = sum(1 for n in news if n["analyst_item"])
            print(f"    {len(news)} reliable news item(s) ({n_analyst} analyst-related)")

            ratings = []
            if do_analysts and _us_listed(tk):
                if browser is None:
                    try:
                        browser = _Browser()
                    except ImportError:
                        print("    [!] Playwright not installed; skipping analyst ratings.")
                        do_analysts = False
                if browser is not None:
                    try:
                        ratings = parse_ratings(browser.ratings_table_text(tk))
                        print(f"    {len(ratings)} sell-side analyst rating(s) (finviz)")
                    except Exception as e:
                        print(f"    analyst ratings failed: {e}")
            elif do_analysts:
                print("    (analyst ratings: skipped - not US-listed)")

            out_dir = os.path.join(MARKET_DIR, tk.replace(".", "_"))
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "news.json"), "w", encoding="utf-8") as f:
                json.dump({"ticker": tk, "name": c.get("name"), "generated_utc": stamp,
                           "count": len(news), "news": news}, f, indent=2)
            if ratings:
                with open(os.path.join(out_dir, "analyst_ratings.json"), "w", encoding="utf-8") as f:
                    json.dump({"ticker": tk, "source": "finviz", "generated_utc": stamp,
                               "count": len(ratings), "ratings": ratings}, f, indent=2)
            write_report(out_dir, c, news, ratings)
            summary.append({"ticker": tk, "news": len(news),
                            "analyst_news": n_analyst, "ratings": len(ratings)})
            print()
            time.sleep(0.5)
    finally:
        if browser:
            browser.close()

    with open(os.path.join(MARKET_DIR, "_news_run.json"), "w", encoding="utf-8") as f:
        json.dump({"generated_utc": stamp, "results": summary}, f, indent=2)

    print("=== SUMMARY ===")
    for s in summary:
        print(f"  {s['ticker']:<10} news={s['news']:<3} analyst-news={s['analyst_news']:<3} ratings={s['ratings']}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="AMKOR News & Analyst Harvester (03c).")
    p.add_argument("tickers", nargs="*", help="Tickers (default: competitors.json).")
    p.add_argument("--news", type=int, default=40, help="Max reliable news items per company (default 40).")
    p.add_argument("--no-analysts", action="store_true", help="Skip finviz analyst-ratings scrape.")
    args = p.parse_args()
    companies = load_companies(args.tickers)
    run(companies, args.news, not args.no_analysts)


if __name__ == "__main__":
    main()
