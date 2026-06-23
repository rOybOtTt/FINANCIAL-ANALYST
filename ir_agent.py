"""
AMKOR - IR Harvester  (Agent 09)
================================

For companies that do NOT file with the SEC (so Agent 01/EDGAR can't reach them),
this agent scrapes their Investor-Relations website with Playwright and downloads
the investor documents - annual reports, investor presentations, earnings
releases, fact books, transcripts - as PDFs.

Targets are configured in  ir_sources.json  (JCET, Powertech, Samsung by default;
SPIL is omitted because it merged into ASE, whose SEC filings already cover it).

Usage:
  python ir_agent.py                      # all companies in ir_sources.json
  python ir_agent.py samsung jcet         # only these (by slug or name)
  python ir_agent.py --max 12             # cap docs per company
  python ir_agent.py --list               # just discover/list candidate links, don't download

Output:
  data/ir/<slug>/
    <document>.pdf            # downloaded investor docs
    links.json               # ALL candidate links found (for transparency / fixing)
    manifest.json            # what was downloaded

NOTE: IR sites vary wildly and some block bots or render via JS. This is a
best-effort harvester - if a site yields little, fix its seed_urls in
ir_sources.json, or download the PDFs manually into uploads/ for Agent 08.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
IR_DIR = os.path.join(HERE, "data", "ir")
CONFIG = os.path.join(HERE, "ir_sources.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0 Safari/537.36")


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def slugify_name(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "doc"


class Browser:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(headless=True)
        self._ctx = self._b.new_context(user_agent=UA)

    def links(self, url):
        """Return (final_url, [(text, href), ...]) for a page."""
        pg = self._ctx.new_page()
        try:
            pg.goto(url, timeout=30000, wait_until="domcontentloaded")
            pg.wait_for_timeout(4000)   # let JS-rendered doc links (e.g. SK Hynix) appear
            anchors = pg.eval_on_selector_all(
                "a", "els => els.map(e => [e.innerText, e.href])")
            return pg.url, anchors
        finally:
            pg.close()

    def download(self, url):
        r = self._ctx.request.get(url, timeout=45000)
        if not r.ok:
            raise RuntimeError(f"HTTP {r.status}")
        return r.body()

    def close(self):
        try:
            self._b.close(); self._pw.stop()
        except Exception:
            pass


def ensure_browser():
    try:
        return Browser()
    except ImportError:
        print("\n[!] Playwright not installed. Enable it with:")
        print("      python -m pip install playwright")
        print("      python -m playwright install chromium\n")
        sys.exit(1)


DOC_EXT = (".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx")
NAV_KW = ("financial report", "annual report", "presentation", "earnings", "investor",
          "results", "quarter", "download", "filing", "fact", "report")

_NOW_YEAR = datetime.now(timezone.utc).year
ALLOWED_YEARS = {str(_NOW_YEAR), str(_NOW_YEAR - 1)}   # "last year" window


def is_doc(href):
    low = href.lower().split("?")[0]
    if low.endswith(DOC_EXT):
        return True
    # download-handler endpoints that stream a file (e.g. Powertech .ashx)
    return low.endswith(".ashx") or "/handlers/" in low


def doc_filename(url, text):
    """A sensible, unique-ish filename for a doc/handler URL."""
    from urllib.parse import parse_qs
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if ext in DOC_EXT:
        return os.path.basename(parsed.path)
    qs = parse_qs(parsed.query)
    fid = (qs.get("id") or [""])[0][:8]
    col = (qs.get("col") or [""])[0]
    stem = (slugify_name(text) if text and len(text.strip()) > 2
            else slugify_name(os.path.splitext(os.path.basename(parsed.path))[0]))
    return "_".join(p for p in (stem, col, fid) if p) + ".pdf"


def looks_like_doc(blob, url):
    if blob[:5] == b"%PDF-" or blob[:2] == b"PK":   # PDF, or zip-based office doc
        return True
    return url.lower().split("?")[0].endswith((".doc", ".txt", ".htm", ".html"))


def year_ok(text, url):
    """Keep undated links; for dated ones require a recent year (handles
    YYYYMMDD filenames via the no-preceding-digit guard)."""
    yrs = re.findall(r"(?<!\d)(?:19|20)\d{2}", url + " " + (text or ""))
    return (not yrs) or any(y in ALLOWED_YEARS for y in yrs)


def is_follow(text, href, base_domain):
    if is_doc(href):
        return False
    netloc = urlparse(href).netloc.lower()
    if netloc and base_domain not in netloc:
        return False
    blob = (text or "").lower() + " " + href.lower()
    return any(k in blob for k in NAV_KW)


def harvest(company, keywords, browser, max_docs, list_only):
    name, slug = company["name"], company["slug"]
    print(f"\n### {name}  ({slug})")
    out_dir = os.path.join(IR_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)

    seeds = company.get("seed_urls", [])
    base_domain = ".".join(urlparse(seeds[0]).netloc.split(":")[0].split(".")[-2:]) if seeds else ""
    seen_pages, doc_seen, candidates, follow = set(), set(), [], []

    def collect(final, anchors):
        for text, href in anchors:
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            absu = urljoin(final, href)
            if is_doc(absu):
                if absu not in doc_seen and year_ok(text, absu):
                    doc_seen.add(absu)
                    candidates.append({"text": (text or "").strip()[:120], "url": absu})
            elif is_follow(text, absu, base_domain) and absu not in seen_pages:
                follow.append(absu)

    for url in seeds:
        try:
            final, anchors = browser.links(url)
        except Exception as e:
            print(f"    [!] could not load {url}: {e}")
            continue
        seen_pages.add(url)
        print(f"    loaded {url} -> {len(anchors)} link(s)")
        collect(final, anchors)

    # follow one level into investor/report sub-pages
    for url in follow[:8]:
        if url in seen_pages:
            continue
        seen_pages.add(url)
        try:
            final, anchors = browser.links(url)
        except Exception:
            continue
        print(f"    followed {url}")
        collect(final, anchors)

    # Order by document type (presentations/earnings first), then by discovery
    # order (pages list newest-first, and Python's sort is stable).
    def _prio(c):
        u = c["url"].lower()
        if u.split("?")[0].endswith(".pdf"):
            return 0
        if "conference" in u or "briefing" in u:   # investor presentations
            return 1
        if "quarter" in u:
            return 2
        if "annual" in u:
            return 3
        return 4
    candidates.sort(key=_prio)
    with open(os.path.join(out_dir, "links.json"), "w", encoding="utf-8") as f:
        json.dump({"company": name, "candidates": candidates}, f, indent=2)
    print(f"    {len(candidates)} candidate document link(s).")

    if list_only:
        for c in candidates[:max_docs]:
            print(f"      - {c['text'][:60]:<60} {c['url']}")
        return {"name": name, "slug": slug, "found": len(candidates), "downloaded": 0}

    saved = []
    for c in candidates:
        if len(saved) >= max_docs:
            break
        url = c["url"]
        fname = doc_filename(url, c["text"])
        try:
            blob = browser.download(url)
        except Exception as e:
            print(f"      ! {fname} failed: {e}")
            continue
        if len(blob) < 2000 or not looks_like_doc(blob, url):
            print(f"      ! {fname} not a document / too small ({len(blob)}B), skipped")
            continue
        path = os.path.join(out_dir, fname)
        if os.path.exists(path):       # ensure uniqueness
            stem, ext = os.path.splitext(fname)
            fname = f"{stem}_{len(saved)}{ext}"
            path = os.path.join(out_dir, fname)
        with open(path, "wb") as f:
            f.write(blob)
        saved.append({"file": fname, "url": url, "text": c["text"], "bytes": len(blob)})
        print(f"      + {fname} ({len(blob)//1024} KB)")

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"company": name, "slug": slug,
                   "generated_utc": datetime.now(timezone.utc).isoformat(),
                   "downloaded": saved}, f, indent=2)
    print(f"    downloaded {len(saved)} document(s) -> {out_dir}")
    return {"name": name, "slug": slug, "found": len(candidates), "downloaded": len(saved)}


def main():
    p = argparse.ArgumentParser(description="AMKOR IR Harvester (Agent 09).")
    p.add_argument("companies", nargs="*", help="Slugs or names (default: all).")
    p.add_argument("--max", type=int, default=15, help="Max docs per company (default 15).")
    p.add_argument("--list", action="store_true", help="Only list candidate links; don't download.")
    args = p.parse_args()

    cfg = load_config()
    keywords = cfg.get("keywords", [])
    wanted = {c.lower() for c in args.companies}
    companies = [c for c in cfg["companies"]
                 if not wanted or c["slug"].lower() in wanted or c["name"].lower() in wanted]
    if not companies:
        print("No matching companies in ir_sources.json.")
        return

    os.makedirs(IR_DIR, exist_ok=True)
    browser = ensure_browser()
    summary = []
    try:
        for company in companies:
            try:
                summary.append(harvest(company, keywords, browser, args.max, args.list))
            except Exception as e:
                print(f"    [!] {company['name']} failed: {e}")
                summary.append({"name": company["name"], "slug": company["slug"],
                                "found": 0, "downloaded": 0, "error": str(e)})
    finally:
        browser.close()

    print("\n=== IR HARVEST SUMMARY ===")
    for s in summary:
        extra = f" (ERROR: {s['error']})" if s.get("error") else ""
        print(f"  {s['slug']:<12} found={s.get('found',0):<4} downloaded={s.get('downloaded',0)}{extra}")
    print("\nFix any low results by editing seed_urls in ir_sources.json, or drop "
          "PDFs into uploads/ for Agent 08.")


if __name__ == "__main__":
    main()
