"""
AMKOR - Tech Agent  (Agent 02)
==============================

Researches a TECHNOLOGY topic and returns findings ONLY from reliable sources.

Use it whenever you want a technology question answered from a tech perspective
(e.g. "2.5D advanced packaging", "CoWoS", "glass substrates", "HBM4"):

  python tech_agent.py "advanced semiconductor packaging 2.5D"
  python tech_agent.py "glass core substrates" --max 8
  python tech_agent.py "chiplets" --web            # also sweep the open web (Bing)
  python tech_agent.py "chiplets" --force-playwright

How it works
------------
  1. DISCOVERY through curated, no-key scholarly indexes that don't bot-block:
       - arXiv API      (peer-reviewed-adjacent preprints)
       - Crossref API   (journal / publisher articles, by DOI)
     Optionally (--web) also sweeps Bing via Playwright for tier-2 journalism.
  2. SCRAPE each candidate source page. PRIMARY fetch is urllib; it falls back
     to a real Chromium browser (Playwright) automatically when a site blocks it
     (or always, with --force-playwright).
  3. VALIDATE every candidate through the Source Validator (02b). Only
     RELIABLE / BORDERLINE sources are kept; UNRELIABLE ones are dropped.
  4. WRITE a report (markdown + JSON) under  data/tech/<topic-slug>/ .
"""

import argparse
import base64
import html as html_mod
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

import source_validator as sv

HERE = os.path.dirname(os.path.abspath(__file__))
TECH_DIR = os.path.join(HERE, "data", "tech")
UA = "AMKOR Tech Agent (roybaibuch@gmail.com)"

ARXIV_API = ("http://export.arxiv.org/api/query?search_query=all:{q}"
             "&start=0&max_results={n}&sortBy=relevance")
CROSSREF_API = ("https://api.crossref.org/works?query={q}&rows={n}"
                "&select=title,URL,container-title,publisher,abstract,issued")
BING = "https://www.bing.com/search?q={q}"


# --------------------------------------------------------------------------
# Fetching: urllib primary, Playwright fallback. Returns (final_url, html).
# --------------------------------------------------------------------------

class FetchBlocked(Exception):
    pass


def urllib_get(url):
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    req = Request(url, headers={"User-Agent": UA,
                                "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urlopen(req, timeout=25) as r:
            final = r.geturl()
            data = r.read(500_000)
            if r.headers.get("Content-Encoding") == "gzip":
                import gzip
                data = gzip.decompress(data)
            return final, data.decode("utf-8", errors="ignore")
    except HTTPError as e:
        if e.code in (403, 429, 202, 401):
            raise FetchBlocked(f"HTTP {e.code}")
        raise
    except URLError as e:
        raise FetchBlocked(str(e.reason))


class Browser:
    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._b = self._pw.chromium.launch(headless=True)
        self._ctx = self._b.new_context(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0 Safari/537.36"))

    def get(self, url):
        pg = self._ctx.new_page()
        try:
            pg.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(1.2)
            return pg.url, pg.content()
        finally:
            pg.close()

    def close(self):
        try:
            self._b.close(); self._pw.stop()
        except Exception:
            pass


def ensure_browser():
    try:
        return Browser()
    except ImportError:
        print("\n[!] Playwright not installed. Enable the browser path with:")
        print("      python -m pip install playwright")
        print("      python -m playwright install chromium\n")
        sys.exit(1)


class Fetcher:
    def __init__(self, force_playwright=False):
        self.force = force_playwright
        self.browser = None

    def get(self, url):
        if self.force:
            if self.browser is None:
                self.browser = ensure_browser()
            return self.browser.get(url)
        if self.browser is not None:
            try:
                return self.browser.get(url)
            except Exception as e:
                raise FetchBlocked(str(e))
        try:
            return urllib_get(url)
        except FetchBlocked as e:
            print(f"    [!] {url[:50]}... blocked ({e}); using browser")
            self.browser = ensure_browser()
            return self.browser.get(url)

    def close(self):
        if self.browser:
            self.browser.close()


# --------------------------------------------------------------------------
# Discovery backends
# --------------------------------------------------------------------------

def _clean(text):
    return html_mod.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def discover_arxiv(topic, n):
    from urllib.request import Request, urlopen
    url = ARXIV_API.format(q=quote_plus(topic), n=n)
    try:
        xml = urlopen(Request(url, headers={"User-Agent": UA}),
                      timeout=20).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"    arXiv discovery failed: {e}")
        return []
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        t = re.search(r"<title>(.*?)</title>", entry, re.S)
        i = re.search(r"<id>(.*?)</id>", entry, re.S)
        s = re.search(r"<summary>(.*?)</summary>", entry, re.S)
        if not i:
            continue
        out.append({"url": i.group(1).strip(), "channel": "arxiv",
                    "title": _clean(t.group(1)) if t else "",
                    "summary": _clean(s.group(1))[:400] if s else ""})
    return out


def discover_crossref(topic, n):
    from urllib.request import Request, urlopen
    url = CROSSREF_API.format(q=quote_plus(topic), n=n)
    try:
        data = json.loads(urlopen(Request(url, headers={"User-Agent": UA}),
                                  timeout=20).read())
    except Exception as e:
        print(f"    Crossref discovery failed: {e}")
        return []
    out = []
    for it in data.get("message", {}).get("items", []):
        u = it.get("URL")
        if not u:
            continue
        journal = (it.get("container-title") or [""])[0]
        pub = it.get("publisher") or ""
        out.append({"url": u, "channel": "crossref",
                    "title": (it.get("title") or [""])[0],
                    "summary": _clean(it.get("abstract", ""))[:400],
                    "extra": f"{journal} - {pub}".strip(" -")})
    return out


_BING_CK = re.compile(r'href="(https://www\.bing\.com/ck/a\?[^"]+)"')


def _decode_bing(href):
    qs = parse_qs(urlparse(href).query)
    u = qs.get("u", [""])[0]
    if u.startswith("a1"):
        b = u[2:]
        b += "=" * (-len(b) % 4)
        try:
            return base64.urlsafe_b64decode(b).decode("utf-8", "ignore")
        except Exception:
            return None
    return None


def discover_web(topic, n, fetcher):
    """Sweep Bing via the browser. Noisy on purpose - validator filters it."""
    try:
        _, html_text = fetcher.get(BING.format(q=quote_plus(topic)))
    except Exception as e:
        print(f"    web discovery failed: {e}")
        return []
    out, seen = [], set()
    for href in _BING_CK.findall(html_text):
        real = _decode_bing(href)
        if real and real.startswith("http") and real not in seen:
            seen.add(real)
            out.append({"url": real, "channel": "web", "title": "", "summary": ""})
        if len(out) >= n * 3:
            break
    return out


# --------------------------------------------------------------------------
# Page extraction
# --------------------------------------------------------------------------

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
_DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', re.I)
_OGDESC_RE = re.compile(
    r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', re.I)


def extract_title_summary(url, html_text):
    m = _TITLE_RE.search(html_text)
    title = _clean(m.group(1)) if m else url
    d = _DESC_RE.search(html_text) or _OGDESC_RE.search(html_text)
    summary = html_mod.unescape(d.group(1)).strip() if d else ""
    return title, summary


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def run(topic, max_results, force_playwright, use_web):
    registry = sv.load_registry()
    os.makedirs(TECH_DIR, exist_ok=True)
    fetcher = Fetcher(force_playwright)

    print(f"Topic     : {topic}")
    print(f"Fetcher   : {'Playwright (forced)' if force_playwright else 'urllib (-> Playwright on block)'}")
    print(f"Registry  : {len(registry['sources'])} reliable domains")
    print(f"Backends  : arXiv + Crossref" + (" + web(Bing)" if use_web else "") + "\n")

    per = max(max_results, 5)
    print("Discovering candidates...")
    streams = [discover_arxiv(topic, per), discover_crossref(topic, per)]
    if use_web:
        streams.append(discover_web(topic, per, fetcher))
    # interleave channels so no single source crowds out the others
    candidates = []
    for i in range(max(len(s) for s in streams) if streams else 0):
        for s in streams:
            if i < len(s):
                candidates.append(s[i])
    # de-dup by url
    seen, uniq = set(), []
    for c in candidates:
        if c["url"] not in seen:
            seen.add(c["url"]); uniq.append(c)
    print(f"  {len(uniq)} unique candidate(s).\n")

    print("Scraping + validating (Agent 02b)...")
    kept = []
    for c in uniq:
        # quick pre-check on the candidate URL (no page yet)
        pre = sv.validate(c["url"], registry=registry, channel=c["channel"])
        if pre["verdict"] == "UNRELIABLE" and c["channel"] == "web":
            continue  # drop obvious web junk before spending a fetch
        try:
            final_url, page = fetcher.get(c["url"])
        except Exception as e:
            print(f"    skip (fetch failed): {c['url'][:55]} ({e})")
            continue
        verdict = sv.validate(final_url, registry=registry, html=page,
                              channel=c["channel"])
        if verdict["verdict"] == "UNRELIABLE":
            print(f"    drop [{verdict['score']:>3}] {verdict['domain']}")
            continue
        title, summary = extract_title_summary(final_url, page)
        kept.append({
            "title": c["title"] or title,
            "url": final_url,
            "domain": verdict["domain"],
            "source": verdict["registry_name"] or c.get("extra") or c["channel"],
            "channel": c["channel"],
            "tier": verdict["tier"],
            "reliability": verdict["verdict"],
            "score": verdict["score"],
            "summary": c["summary"] or summary,
        })
        print(f"    keep [{verdict['verdict']:<10} {verdict['score']:>3}] "
              f"{verdict['domain']} - {(c['title'] or title)[:55]}")
        if len(kept) >= max_results:
            break

    fetcher.close()

    kept.sort(key=lambda k: (k["tier"] or 9, -k["score"]))

    out_dir = os.path.join(TECH_DIR, slugify(topic))
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()

    with open(os.path.join(out_dir, "findings.json"), "w", encoding="utf-8") as f:
        json.dump({"topic": topic, "generated_utc": stamp,
                   "count": len(kept), "findings": kept}, f, indent=2)

    md = [f"# Tech Research: {topic}", "",
          f"_Generated {stamp} - {len(kept)} reliable source(s)_", ""]
    for k in kept:
        md.append(f"## {k['title']}")
        md.append(f"- **Source:** {k['source']} "
                  f"(tier {k['tier'] or '-'}, {k['reliability']} {k['score']}/100, via {k['channel']})")
        md.append(f"- **URL:** {k['url']}")
        if k["summary"]:
            md.append(f"- **Summary:** {k['summary']}")
        md.append("")
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"\nKept {len(kept)} reliable source(s).")
    print(f"Report -> {os.path.join(out_dir, 'report.md')}")
    if not kept:
        print("\n[!] Nothing passed. Try different wording or add domains to reliable_sources.json.")


def main():
    # Windows consoles default to cp1252; source titles can contain Unicode
    # (e.g. arrows/dashes) that would otherwise crash print(). Fail-safe to UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="AMKOR Tech Agent - reliable-source tech research.")
    p.add_argument("topic", nargs="*", help="Technology topic / question.")
    p.add_argument("--max", type=int, default=6, help="Max reliable sources to keep (default 6).")
    p.add_argument("--web", action="store_true", help="Also sweep the open web (Bing via browser).")
    p.add_argument("--force-playwright", action="store_true", help="Use the browser path from the start.")
    p.add_argument("--batch", metavar="FILE", help="Research every topic in FILE (one per line; # = comment).")
    args = p.parse_args()

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            topics = [ln.strip() for ln in f
                      if ln.strip() and not ln.lstrip().startswith("#")]
        print(f"BATCH: {len(topics)} topic(s) from {args.batch}\n")
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*70}\n[{i}/{len(topics)}] {topic}\n{'='*70}")
            try:
                run(topic, args.max, args.force_playwright, args.web)
            except Exception as e:
                print(f"[!] topic failed ({topic}): {e}")
        print(f"\nBATCH DONE: {len(topics)} topic(s) -> data/tech/")
        return

    topic = " ".join(args.topic).strip()
    if not topic:
        topic = input("Tech topic / question?\n> ").strip()
    if not topic:
        print("No topic given. Exiting.")
        return
    run(topic, args.max, args.force_playwright, args.web)


if __name__ == "__main__":
    main()
