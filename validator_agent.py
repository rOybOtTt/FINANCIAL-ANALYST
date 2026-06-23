"""
AMKOR - Validator Agent  (Agent 01b)
====================================

Validates the filings pulled by the Data Agent (agent 01).

It runs AUTOMATICALLY at the end of every Data Agent run, and can also be run
on its own at any time:

  python validator_agent.py
  python validator_agent.py --strict     # warnings count as failures

What it checks, per company and per filing:
  1. manifest.json exists and is readable for each company in the last run.
  2. Every filing in the manifest has its folder on disk.
  3. The primary document file exists and is not empty / not suspiciously tiny.
  4. The document is NOT an EDGAR rate-limit / error page.
  5. The document looks like a real filing (HTML/XBRL/text markers present).
  6. _meta.json exists for the filing.
  7. The filing date sits inside the requested lookback window.
  8. Folder count on disk matches the manifest count (nothing missing/extra).

Output:
  - Console report with PASS / WARN / FAIL per filing and a summary.
  - data/_validation_report.json  (machine-readable results)
  - Exit code 0 if OK, 1 if any FAIL (or any WARN when --strict).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

# A primary document smaller than this is almost certainly broken/truncated.
MIN_DOC_BYTES = 1024

# Strings that betray an EDGAR throttle / error page instead of a real filing.
ERROR_MARKERS = (
    "request rate threshold exceeded",
    "you have exceeded the sec",
    "access denied",
    "undeclared automated tool",
    "for security purposes, and to ensure that the public service remains available",
)

# At least one of these should appear in a genuine filing document.
CONTENT_MARKERS = (
    "<html", "<!doctype", "<xbrl", "<?xml",
    "securities and exchange commission",
    "form 10-k", "form 10-q", "form 8-k", "united states",
)


class Check:
    def __init__(self):
        self.fails = []
        self.warns = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    @property
    def status(self):
        if self.fails:
            return "FAIL"
        if self.warns:
            return "WARN"
        return "PASS"


def _read_text_head(path, nbytes=200_000):
    try:
        with open(path, "rb") as f:
            raw = f.read(nbytes)
        return raw.decode("utf-8", errors="ignore").lower()
    except OSError:
        return None


def validate_filing(filing, lookback_days):
    """Return (status, [messages]) for a single filing dict from a manifest."""
    c = Check()
    label = f"{filing.get('filingDate','?')} {filing.get('form','?')} {filing.get('accessionNumber','?')}"

    saved_to = filing.get("saved_to")

    # filing date inside the window?
    fdate = filing.get("filingDate")
    if fdate and lookback_days:
        try:
            d = datetime.strptime(fdate, "%Y-%m-%d").date()
            cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).date()
            if d < cutoff:
                c.warn(f"filing date {fdate} is older than the {lookback_days}-day window")
        except ValueError:
            c.warn(f"unparseable filing date: {fdate!r}")

    # primary document present?
    if not saved_to:
        # Some filings legitimately have no primary document.
        if filing.get("primaryDocument"):
            c.fail("primary document was expected but never saved (saved_to is null)")
        else:
            c.warn("filing has no primary document (nothing to download)")
        return c.status, label, c.fails + [f"(warn) {w}" for w in c.warns]

    if not os.path.isfile(saved_to):
        c.fail(f"saved file missing on disk: {saved_to}")
        return c.status, label, c.fails + [f"(warn) {w}" for w in c.warns]

    size = os.path.getsize(saved_to)
    if size == 0:
        c.fail("saved file is empty (0 bytes)")
    elif size < MIN_DOC_BYTES:
        c.warn(f"saved file is very small ({size} bytes) - possibly truncated")

    # _meta.json next to the document?
    folder = os.path.dirname(saved_to)
    if not os.path.isfile(os.path.join(folder, "_meta.json")):
        c.warn("_meta.json missing for this filing")

    # content sanity
    head = _read_text_head(saved_to)
    if head is None:
        c.fail("could not read saved file")
    else:
        for marker in ERROR_MARKERS:
            if marker in head:
                c.fail(f"document looks like an EDGAR error/throttle page (matched {marker!r})")
                break
        else:
            if size >= MIN_DOC_BYTES and not any(m in head for m in CONTENT_MARKERS):
                c.warn("document does not contain any expected filing markers")

    return c.status, label, c.fails + [f"(warn) {w}" for w in c.warns]


def validate_company(ticker, manifest_path):
    c = Check()
    result = {"ticker": ticker, "manifest": manifest_path, "filings": []}

    if not os.path.isfile(manifest_path):
        c.fail("manifest.json missing")
        result["status"] = c.status
        result["messages"] = c.fails
        return result

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        c.fail(f"manifest.json unreadable: {e}")
        result["status"] = c.status
        result["messages"] = c.fails
        return result

    lookback = manifest.get("lookback_days")
    filings = manifest.get("filings", [])

    # folder count vs manifest count
    company_dir = os.path.dirname(manifest_path)
    on_disk = [d for d in os.listdir(company_dir)
               if os.path.isdir(os.path.join(company_dir, d))]
    if len(on_disk) != len(filings):
        c.warn(f"{len(on_disk)} folders on disk but manifest lists {len(filings)} filings")

    n_pass = n_warn = n_fail = 0
    for filing in filings:
        status, label, msgs = validate_filing(filing, lookback)
        result["filings"].append({"label": label, "status": status, "messages": msgs})
        if status == "FAIL":
            n_fail += 1
        elif status == "WARN":
            n_warn += 1
        else:
            n_pass += 1

    if n_fail:
        c.fail(f"{n_fail} filing(s) failed validation")
    if n_warn:
        c.warn(f"{n_warn} filing(s) raised warnings")

    result["status"] = c.status
    result["messages"] = c.fails + [f"(warn) {w}" for w in c.warns]
    result["counts"] = {"pass": n_pass, "warn": n_warn, "fail": n_fail}
    return result


def validate_run(data_dir=DATA_DIR, strict=False, quiet=False):
    """Validate the most recent Data Agent run. Returns (ok, report)."""
    def say(*a):
        if not quiet:
            print(*a)

    say("\n" + "=" * 60)
    say("VALIDATOR AGENT - checking saved filings")
    say("=" * 60)

    last_run_path = os.path.join(data_dir, "_last_run.json")
    companies = []
    if os.path.isfile(last_run_path):
        try:
            with open(last_run_path, encoding="utf-8") as f:
                last_run = json.load(f)
            for r in last_run.get("results", []):
                if r.get("found") and r.get("ticker"):
                    companies.append(r["ticker"])
        except (OSError, json.JSONDecodeError):
            pass

    # fall back to scanning every company folder
    if not companies and os.path.isdir(data_dir):
        companies = [d for d in os.listdir(data_dir)
                     if os.path.isdir(os.path.join(data_dir, d))]

    if not companies:
        say("No companies found to validate (has the Data Agent run yet?).")
        return True, {"companies": [], "overall": "EMPTY"}

    results = []
    for ticker in companies:
        manifest_path = os.path.join(data_dir, ticker, "manifest.json")
        res = validate_company(ticker, manifest_path)
        results.append(res)

        say(f"\n### {ticker}: {res['status']}")
        for m in res.get("messages", []):
            say(f"    - {m}")
        for fr in res.get("filings", []):
            if fr["status"] != "PASS":
                say(f"    [{fr['status']}] {fr['label']}")
                for msg in fr["messages"]:
                    say(f"        {msg}")

    any_fail = any(r["status"] == "FAIL" for r in results)
    any_warn = any(r["status"] == "WARN" for r in results)
    overall = "FAIL" if any_fail else ("WARN" if any_warn else "PASS")

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "strict": strict,
        "companies": results,
    }
    out_path = os.path.join(data_dir, "_validation_report.json")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except OSError:
        pass

    # summary line
    say("\n" + "-" * 60)
    for r in results:
        cnt = r.get("counts", {})
        say(f"  {r['ticker']:<8} {r['status']:<5} "
            f"pass={cnt.get('pass',0)} warn={cnt.get('warn',0)} fail={cnt.get('fail',0)}")
    say("-" * 60)
    say(f"OVERALL: {overall}   (report -> {out_path})")

    ok = not any_fail and not (strict and any_warn)
    return ok, report


def main():
    p = argparse.ArgumentParser(description="AMKOR Validator Agent.")
    p.add_argument("--strict", action="store_true",
                   help="Treat warnings as failures (non-zero exit).")
    p.add_argument("--data-dir", default=DATA_DIR)
    args = p.parse_args()
    ok, _ = validate_run(args.data_dir, strict=args.strict)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
