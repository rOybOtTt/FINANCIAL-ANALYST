"""
AMKOR - Source Validator  (Agent 02b)
=====================================

Decides whether a web source is RELIABLE enough to use in tech research.

The Tech Agent (02) calls this for every candidate URL it finds, and only
sources that pass are kept. It can also be run on its own to vet any URL:

  python source_validator.py https://arxiv.org/abs/2401.12345
  python source_validator.py https://some-random-blog.blogspot.com/... --fetch

Scoring (0-100):
  + registry tier 1 (peer-reviewed/academic/standards)  -> base 60
  + registry tier 2 (reputable analysis/journalism)      -> base 45
  + trusted TLD (.edu / .gov)                             -> +30
  + HTTPS                                                 -> +8
  + page has an author byline           (needs --fetch)  -> +10
  + page has a publication date         (needs --fetch)  -> +10
  + page has citations / DOI / refs     (needs --fetch)  -> +14
  - matches a low-quality signal                         -> -40

Verdict:
  score >= 60  -> RELIABLE
  40..59       -> BORDERLINE
  < 40         -> UNRELIABLE
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(HERE, "reliable_sources.json")

RELIABLE_THRESHOLD = 60
BORDERLINE_THRESHOLD = 40


def load_registry(path=REGISTRY_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def domain_of(url):
    netloc = urlparse(url if "://" in url else "http://" + url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _registry_match(domain, registry):
    """Return the most specific matching source entry, or None."""
    best = None
    for src in registry.get("sources", []):
        d = src["domain"].lower()
        if domain == d or domain.endswith("." + d):
            if best is None or len(d) > len(best["domain"]):
                best = src
    return best


# ---- page-signal detection (only when --fetch / fetched HTML supplied) -----

_AUTHOR_RE = re.compile(
    r'(name=["\']author["\']|rel=["\']author["\']|property=["\']article:author["\']|class=["\'][^"\']*byline)',
    re.I)
_DATE_RE = re.compile(
    r'(property=["\']article:published_time["\']|name=["\']date["\']|name=["\']pubdate["\']|<time[\s>]|datetime=)',
    re.I)
_CITE_RE = re.compile(
    r'(doi\.org/|>doi<|references|bibliography|\bcite[ds]?\b|citation)', re.I)


def page_signals(html):
    h = html or ""
    return {
        "author": bool(_AUTHOR_RE.search(h)),
        "date": bool(_DATE_RE.search(h)),
        "citations": bool(_CITE_RE.search(h)),
    }


def fetch_html(url):
    """Light fetch for signal checks. urllib first, Playwright on block."""
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    req = Request(url, headers={"User-Agent":
                  "AMKOR Source Validator (roybaibuch@gmail.com)"})
    try:
        with urlopen(req, timeout=20) as r:
            data = r.read(300_000)
            if r.headers.get("Content-Encoding") == "gzip":
                import gzip
                data = gzip.decompress(data)
            return data.decode("utf-8", errors="ignore")
    except (HTTPError, URLError):
        pass
    # browser fallback
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_context().new_page()
            pg.goto(url, timeout=25000, wait_until="domcontentloaded")
            html = pg.content()
            b.close()
            return html
    except Exception:
        return None


# Scholarly indexes that only list registered academic / publisher content.
# A hit discovered through one of these is itself a strong reliability signal.
SCHOLARLY_CHANNELS = {"arxiv": 60, "crossref": 50, "semantic_scholar": 50}


def validate(url, registry=None, html=None, do_fetch=False, channel=None):
    """Return a verdict dict for a single URL.

    channel: optional discovery channel ('arxiv' / 'crossref' / ...). When the
    URL was found through a curated scholarly index, that itself adds reliability
    even if the final publisher domain is not in the registry.
    """
    registry = registry or load_registry()
    domain = domain_of(url)
    score = 0
    signals = []

    if channel in SCHOLARLY_CHANNELS:
        pts = SCHOLARLY_CHANNELS[channel]
        score += pts
        signals.append(f"discovered via scholarly index '{channel}' +{pts}")

    match = _registry_match(domain, registry)
    if match:
        base = 60 if match["tier"] == 1 else 45
        score += base
        signals.append(f"registry tier {match['tier']} ({match['name']}, {match['type']}) +{base}")

    for tld in registry.get("trusted_tlds", []):
        if domain.endswith(tld):
            score += 30
            signals.append(f"trusted TLD {tld} +30")
            break

    if url.lower().startswith("https://"):
        score += 8
        signals.append("https +8")

    for bad in registry.get("low_quality_signals", []):
        if bad in domain or bad in url.lower():
            score -= 40
            signals.append(f"low-quality signal '{bad}' -40")
            break

    # page-content signals
    if html is None and do_fetch:
        html = fetch_html(url)
    if html:
        ps = page_signals(html)
        if ps["author"]:
            score += 10; signals.append("author byline +10")
        if ps["date"]:
            score += 10; signals.append("publication date +10")
        if ps["citations"]:
            score += 14; signals.append("citations/DOI/refs +14")

    score = max(0, min(100, score))
    if score >= RELIABLE_THRESHOLD:
        verdict = "RELIABLE"
    elif score >= BORDERLINE_THRESHOLD:
        verdict = "BORDERLINE"
    else:
        verdict = "UNRELIABLE"

    return {
        "url": url,
        "domain": domain,
        "in_registry": bool(match),
        "registry_name": match["name"] if match else None,
        "tier": match["tier"] if match else None,
        "score": score,
        "verdict": verdict,
        "signals": signals,
    }


def main():
    p = argparse.ArgumentParser(description="AMKOR Source Validator.")
    p.add_argument("url", help="URL to validate.")
    p.add_argument("--fetch", action="store_true",
                   help="Fetch the page to check author/date/citations.")
    args = p.parse_args()
    res = validate(args.url, do_fetch=args.fetch)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] != "UNRELIABLE" else 1)


if __name__ == "__main__":
    main()
