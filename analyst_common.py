"""
AMKOR - Analyst Common  (shared foundation for Agents 4-7)
==========================================================

Provides:
  - get_client()      : an Anthropic client (reads ANTHROPIC_API_KEY from env)
  - ask_claude(...)   : one Claude call (Opus 4.8, adaptive thinking, streaming)
  - load_context(...) : builds a compact DATA BRIEF from everything Agents 1/2/3
                        produced (EDGAR filings, tech research, market snapshots)

The analyst agents (Financial=4, Tech=5, Synthesizer=6, Senior=7) all read the
SAME data brief, so they argue over one shared set of facts.

Requires:  pip install anthropic   and   ANTHROPIC_API_KEY set in the environment.
"""

import html as html_mod
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

MODEL = "claude-opus-4-8"

# Budgets (characters) to keep the brief rich but affordable.
MAX_FILING_CHARS = 14000     # per extracted filing document
MAX_TOTAL_FILING_CHARS = 40000


class NoApiKey(Exception):
    pass


def get_client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise NoApiKey(
            "ANTHROPIC_API_KEY is not set.\n"
            "  PowerShell:  $env:ANTHROPIC_API_KEY = 'sk-ant-...'\n"
            "  (or set it permanently in your system environment variables)\n"
            "Get a key at https://console.anthropic.com/ ."
        )
    try:
        import anthropic
    except ImportError:
        raise NoApiKey("The 'anthropic' SDK is not installed. Run: python -m pip install anthropic")
    return anthropic.Anthropic()


def ask_claude(system_blocks, user_text, max_tokens=4000, effort="medium", attachments=None):
    """One Claude call. `system_blocks` is a list of system content blocks
    (so the big shared data brief can be cached). `attachments` is an optional
    list of content blocks (e.g. PDF document blocks from pdf_block()) prepended
    to the user message. Returns the text answer."""
    client = get_client()
    if attachments:
        content = list(attachments) + [{"type": "text", "text": user_text}]
    else:
        content = user_text
    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_blocks,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": content}],
    ) as stream:
        msg = stream.get_final_message()
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def pdf_block(path):
    """A base64 PDF document content block for Claude's native PDF reading."""
    import base64
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return {"type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": data}}


def system_with_context(persona, data_brief):
    """Build the system field: cached data brief first, then the agent persona.
    Caching the brief means every analyst in a debate reuses the same prefix."""
    return [
        {"type": "text",
         "text": "You are analyzing companies using the shared DATA BRIEF below.\n\n"
                 "===== DATA BRIEF (collected by the data agents) =====\n" + data_brief,
         "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": persona},
    ]


# --------------------------------------------------------------------------
# Context loading
# --------------------------------------------------------------------------

def _strip_html(raw):
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)          # drop comments (incl. ones with '>')
    raw = re.sub(r"(?s)<[a-zA-Z/][^<>]*>", " ", raw)    # only real tags; don't eat literal '<'
    raw = html_mod.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


def _read(path):
    # errors="replace" so a non-UTF-8 upload (Excel-exported CSV, latin-1, etc.)
    # is read leniently instead of crashing the run; catch UnicodeError too
    # (UnicodeDecodeError is a ValueError, NOT an OSError).
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, UnicodeError):
        return None


# --- uploaded-document ingestion ------------------------------------------

TEXT_EXTS = {".txt", ".md", ".csv", ".tsv", ".json", ".log", ".yaml", ".yml", ".py"}
HTML_EXTS = {".htm", ".html"}
PDF_EXTS = {".pdf"}


def read_docx(path):
    """Extract text from a .docx/.docm without external deps (it's a zip of XML).
    Returns None on a corrupt / non-zip / wrong-structure file so the caller can
    distinguish a parse failure from a genuinely empty document."""
    import zipfile
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
    except (zipfile.BadZipFile, KeyError, OSError):
        return None
    # insert structural separators BEFORE stripping tags so tables don't fuse
    xml = re.sub(r"(?i)<w:tab[^>]*/?>", "\t", xml)   # tab stops
    xml = re.sub(r"(?i)</w:tc>", "\t", xml)          # table cell -> column sep
    xml = re.sub(r"(?i)</w:tr>", "\n", xml)          # table row -> newline
    xml = re.sub(r"(?i)</w:p>", "\n", xml)           # paragraph breaks
    xml = re.sub(r"(?i)<w:br[^>]*/?>", "\n", xml)    # line breaks
    xml = re.sub(r"(?s)<[^>]+>", "", xml)            # drop remaining tags
    text = html_mod.unescape(xml)
    text = re.sub(r"[ ]{2,}", " ", text)             # squeeze spaces; keep tabs/newlines
    return text.strip()


def read_text_like(path):
    """Return extracted text for a text-like upload, "" for an empty-but-valid
    file, or None if it failed to parse / must be read natively (PDF) / is
    unsupported."""
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTS:
        raw = _read(path)
        return raw if raw is not None else None
    if ext in HTML_EXTS:
        raw = _read(path)
        return _strip_html(raw) if raw is not None else None
    if ext in {".docx", ".docm"}:
        return read_docx(path)
    return None  # PDF -> handle via pdf_block(); anything else -> unsupported


def is_pdf(path):
    return os.path.splitext(path)[1].lower() in PDF_EXTS


def validate_pdf(path):
    """Return (ok, reason). Guards against empty, oversized, and fake (renamed)
    PDFs before we base64-encode and send them to Claude."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return False, "unreadable"
    if size == 0:
        return False, "empty (0 bytes)"
    if size > 25_000_000:  # ~33MB after base64; stays under the 32MB API limit
        return False, f"too large ({size:,} bytes > 25MB)"
    try:
        with open(path, "rb") as f:
            head = f.read(5)
    except OSError:
        return False, "unreadable"
    if head != b"%PDF-":
        return False, "not a real PDF (bad header)"
    return True, "ok"


def _ticker_match(value, company_filter):
    """True if `value` (a ticker, possibly with a Yahoo suffix or '.'->'_'
    folder form) matches any ticker in company_filter. None filter = match all."""
    if not company_filter:
        return True
    norm = lambda s: (s or "").upper().replace("_", ".")
    want = {norm(c) for c in company_filter}
    v = norm(value)
    return v in want or v.split(".")[0] in {w.split(".")[0] for w in want}


def _load_market(company_filter=None):
    out = []
    mdir = os.path.join(DATA, "market")
    if not os.path.isdir(mdir):
        return out
    for tk in sorted(os.listdir(mdir)):
        snap_path = os.path.join(mdir, tk, "snapshot.json")
        if not os.path.isfile(snap_path):
            continue
        try:
            snap = json.loads(_read(snap_path) or "{}")
        except json.JSONDecodeError:
            continue
        if not _ticker_match(snap.get("ticker", tk), company_filter):
            continue
        m = snap.get("metrics", {})
        cc = snap.get("financials", {}).get("price_cross_check", {})
        lines = [f"### {snap.get('ticker', tk)} - {m.get('name')} ({snap.get('role','')})",
                 f"price={m.get('price')} {m.get('currency') or ''}, change={m.get('change_pct')}%, "
                 f"P/E={m.get('pe')}, prev_close={m.get('previous_close')}, "
                 f"52wk=[{m.get('week52_low')},{m.get('week52_high')}], volume={m.get('volume')}, "
                 f"cross_source={cc.get('result')}"]
        news = snap.get("news", [])
        if news:
            lines.append("recent reliable news:")
            for n in news[:5]:
                lines.append(f"  - {n.get('title')} ({n.get('source')})")
        out.append("\n".join(lines))
    return out


def _load_tech(tech_filter=None):
    """tech_filter = optional list of topic slugs to keep (scopes the brief to the
    current target's deck-headline research). None = include every tech dossier."""
    out = []
    tdir = os.path.join(DATA, "tech")
    if not os.path.isdir(tdir):
        return out
    keep = {s for s in tech_filter} if tech_filter else None
    for slug in sorted(os.listdir(tdir)):
        if keep is not None and slug not in keep:
            continue
        fpath = os.path.join(tdir, slug, "findings.json")
        if not os.path.isfile(fpath):
            continue
        try:
            data = json.loads(_read(fpath) or "{}")
        except json.JSONDecodeError:
            continue
        lines = [f"### Tech research: {data.get('topic', slug)}"]
        for fnd in data.get("findings", [])[:6]:
            lines.append(f"  - [{fnd.get('reliability')} {fnd.get('score')}] "
                         f"{fnd.get('title')} ({fnd.get('source')})")
            if fnd.get("summary"):
                lines.append(f"      {fnd['summary'][:240]}")
        out.append("\n".join(lines))
    return out


def _load_filings(company_filter=None):
    """Manifest summaries for each company, plus extracted text from the richest
    filings (10-K then 10-Q), budgeted so the brief stays affordable."""
    out, used = [], 0
    if not os.path.isdir(DATA):
        return out
    for tk in sorted(os.listdir(DATA)):
        cdir = os.path.join(DATA, tk)
        man_path = os.path.join(cdir, "manifest.json")
        if not os.path.isfile(man_path):
            continue
        if company_filter and tk.upper() not in {c.upper() for c in company_filter}:
            continue
        try:
            man = json.loads(_read(man_path) or "{}")
        except json.JSONDecodeError:
            continue
        filings = man.get("filings", [])
        lines = [f"### EDGAR filings for {man.get('ticker', tk)} ({man.get('company','')}) "
                 f"- last {man.get('lookback_days')}d, {len(filings)} filing(s):"]
        for f in filings[:25]:
            lines.append(f"  - {f.get('filingDate')} {f.get('form')} ({f.get('accessionNumber')})")
        # extract text from the most relevant filing (prefer 10-K, then 10-Q)
        ranked = sorted(filings, key=lambda f: (
            0 if (f.get("form") or "").upper() == "10-K" else
            1 if (f.get("form") or "").upper() == "10-Q" else 2,
            f.get("filingDate") or ""), )
        for f in ranked[:2]:
            if used >= MAX_TOTAL_FILING_CHARS:
                break
            path = f.get("saved_to")
            if not path or not os.path.isfile(path):
                continue
            raw = _read(path)
            if not raw:
                continue
            text = _strip_html(raw)[:MAX_FILING_CHARS]
            used += len(text)
            lines.append(f"\n  --- excerpt: {f.get('filingDate')} {f.get('form')} "
                         f"(first {len(text)} chars of text) ---\n  {text}\n")
        out.append("\n".join(lines))
    return out


def _fmt_money(v, currency="USD"):
    if v is None:
        return "n/a"
    try:
        av = abs(v)
    except TypeError:
        return str(v)
    if av >= 1e9:
        return f"{v/1e9:,.2f}B {currency}"
    if av >= 1e6:
        return f"{v/1e6:,.0f}M {currency}"
    return f"{v:,.0f} {currency}"


def _load_fundamentals(company_filter=None):
    out = []
    if not os.path.isdir(DATA):
        return out
    for tk in sorted(os.listdir(DATA)):
        fpath = os.path.join(DATA, tk, "financials.json")
        if not os.path.isfile(fpath):
            continue
        if company_filter and tk.upper() not in {c.upper() for c in company_filter}:
            continue
        try:
            fin = json.loads(_read(fpath) or "{}")
        except json.JSONDecodeError:
            continue
        annual = fin.get("annual", {})
        if not annual:
            continue
        cur = fin.get("currency", "USD")
        lines = [f"### {fin.get('ticker', tk)} fundamentals ({fin.get('entity','')}) "
                 f"- reporting currency {cur}, SEC companyfacts XBRL"]
        for y in sorted(annual.keys(), reverse=True):
            r = annual[y]
            lines.append(
                f"  FY{y}: revenue={_fmt_money(r.get('revenue'), cur)} "
                f"(YoY {r.get('revenue_yoy_pct')}%), gross_margin={r.get('gross_margin_pct')}%, "
                f"op_margin={r.get('operating_margin_pct')}%, net_margin={r.get('net_margin_pct')}%, "
                f"net_income={_fmt_money(r.get('net_income'), cur)}, EPS_diluted={r.get('eps_diluted')}, "
                f"R&D={_fmt_money(r.get('rd_expense'), cur)}, op_cash_flow={_fmt_money(r.get('operating_cash_flow'), cur)}, "
                f"capex={_fmt_money(r.get('capex'), cur)}, FCF={_fmt_money(r.get('free_cash_flow'), cur)}, "
                f"cash={_fmt_money(r.get('cash'), cur)}, LT_debt={_fmt_money(r.get('long_term_debt'), cur)}, "
                f"equity={_fmt_money(r.get('equity'), cur)}")
        out.append("\n".join(lines))
    return out


def _load_analysts(company_filter=None):
    """Sell-side analyst ratings (Agent 03c finviz) + analyst/news headlines."""
    out = []
    mdir = os.path.join(DATA, "market")
    if not os.path.isdir(mdir):
        return out
    for folder in sorted(os.listdir(mdir)):
        cdir = os.path.join(mdir, folder)
        if not os.path.isdir(cdir):
            continue
        if not _ticker_match(folder, company_filter):
            continue
        ratings = news = None
        rp, np_ = os.path.join(cdir, "analyst_ratings.json"), os.path.join(cdir, "news.json")
        if os.path.isfile(rp):
            try:
                ratings = json.loads(_read(rp) or "{}")
            except json.JSONDecodeError:
                pass
        if os.path.isfile(np_):
            try:
                news = json.loads(_read(np_) or "{}")
            except json.JSONDecodeError:
                pass
        if not ratings and not news:
            continue
        tk = (ratings or news or {}).get("ticker", folder)
        if company_filter and tk.upper() not in {c.upper() for c in company_filter}:
            continue
        lines = [f"### {tk} - analyst coverage & news"]
        if ratings and ratings.get("ratings"):
            lines.append("recent sell-side ratings (date | firm | action | rating | target):")
            for r in ratings["ratings"][:8]:
                lines.append(f"  - {r.get('date')} | {r.get('firm')} | {r.get('action')} | "
                             f"{r.get('rating')} | {r.get('price_target')}")
        if news and news.get("news"):
            items = news["news"]
            an = [n for n in items if n.get("analyst_item")][:4]
            gen = [n for n in items if not n.get("analyst_item")][:4]
            if an:
                lines.append("analyst-coverage news:")
                for n in an:
                    lines.append(f"  - {n.get('title')} ({n.get('source')})")
            if gen:
                lines.append("recent reliable news:")
                for n in gen:
                    lines.append(f"  - {n.get('title')} ({n.get('source')})")
        out.append("\n".join(lines))
    return out


def load_context(company_filter=None, tech_filter=None):
    """Assemble the full DATA BRIEF string from Agents 1/2/3 output.

    company_filter : optional list of tickers to scope fundamentals/market/
                     analysts/filings to (the target + its peers). None = all.
    tech_filter    : optional list of tech-topic slugs to scope the tech research
                     to (the current target's deck headlines). None = all.
    Both default to None, so legacy callers get the original behavior."""
    fundamentals = _load_fundamentals(company_filter)
    market = _load_market(company_filter)
    analysts = _load_analysts(company_filter)
    tech = _load_tech(tech_filter)
    filings = _load_filings(company_filter)

    parts = []
    if fundamentals:
        parts.append("## COMPANY FUNDAMENTALS (Agent 01: SEC companyfacts XBRL - "
                     "revenue / margins / EPS / cash flow / balance sheet)\n"
                     + "\n\n".join(fundamentals))
    if market:
        parts.append("## MARKET DATA (Agent 03: financials + reliable news)\n" + "\n\n".join(market))
    if analysts:
        parts.append("## ANALYST COVERAGE (Agent 03c: sell-side ratings + reliable news)\n"
                     + "\n\n".join(analysts))
    if tech:
        parts.append("## TECH RESEARCH (Agent 02: reliable-source findings)\n" + "\n\n".join(tech))
    if filings:
        parts.append("## SEC EDGAR FILINGS (Agent 01)\n" + "\n\n".join(filings))

    if not parts:
        return ("(No data found. Run the data agents first: data_agent.py, "
                "tech_agent.py, market_agent.py.)")
    return "\n\n".join(parts)
