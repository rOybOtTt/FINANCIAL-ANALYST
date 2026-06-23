"""
AMKOR - Market Data Validator  (Agent 03b)
==========================================

Validates the financial + news data that the Market Intel Agent (03) pulled for
each company. Runs AUTOMATICALLY at the end of every Market Agent run, and can
also be run standalone:

  python market_validator.py
  python market_validator.py --strict

What it checks, per company snapshot:
  1. CROSS-SOURCE PRICE: Yahoo price vs CNBC price agree within tolerance (2%).
     This is the core "validate the data" check - two independent sources must
     corroborate the number.
  2. Previous-close agreement between the two sources.
  3. Required financial fields are present and numerically sane
     (price > 0, 52-week low <= price <= 52-week high, etc.).
  4. NEWS SOURCES: every kept news item comes from a reliable outlet (re-checked
     through the Source Validator 02b) and the list is non-empty.
  5. FRESHNESS: the snapshot was generated recently (default within 2 days).

Verdict per company: PASS / WARN / FAIL. Writes data/market/_validation_report.json.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import source_validator as sv

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_DIR = os.path.join(HERE, "data", "market")

PRICE_TOLERANCE = 0.02      # 2% allowed disagreement between sources
FRESH_MAX_DAYS = 2          # snapshot considered stale beyond this


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def validate_snapshot(snap, registry):
    fails, warns = [], []
    fin = snap.get("financials", {})

    ya = _num((fin.get("yahoo") or {}).get("price"))
    cn = _num((fin.get("cnbc") or {}).get("price"))

    # 1. cross-source price agreement
    if ya is None and cn is None:
        fails.append("no price from either source")
    elif ya is None or cn is None:
        warns.append("price available from only one source (no cross-check)")
    else:
        diff = abs(ya - cn) / ya if ya else 1
        if diff > PRICE_TOLERANCE:
            fails.append(f"price mismatch: Yahoo {ya} vs CNBC {cn} ({diff:.1%} > {PRICE_TOLERANCE:.0%})")

    # 2. previous-close agreement
    pcy = _num((fin.get("yahoo") or {}).get("previous_close"))
    pcc = _num((fin.get("cnbc") or {}).get("previous_close"))
    if pcy and pcc and abs(pcy - pcc) / pcy > PRICE_TOLERANCE:
        warns.append(f"previous-close mismatch: Yahoo {pcy} vs CNBC {pcc}")

    # 3. sanity of the consolidated metrics
    m = snap.get("metrics", {})
    price = _num(m.get("price"))
    if price is None or price <= 0:
        fails.append("consolidated price missing or <= 0")
    lo, hi = _num(m.get("week52_low")), _num(m.get("week52_high"))
    if price and lo and hi:
        if not (lo <= price <= hi):
            warns.append(f"price {price} outside 52-week range [{lo}, {hi}]")
        if lo > hi:
            fails.append(f"52-week low {lo} > high {hi}")

    # 4. news sources reliable + present
    news = snap.get("news", [])
    if not news:
        warns.append("no reliable news items kept")
    bad = []
    for item in news:
        v = sv.validate(item.get("url", ""), registry=registry)
        if v["verdict"] == "UNRELIABLE":
            bad.append(item.get("url", "")[:60])
    if bad:
        fails.append(f"{len(bad)} news item(s) from UNRELIABLE sources slipped in: {bad[:3]}")

    # 5. freshness
    gen = snap.get("generated_utc")
    if gen:
        try:
            dt = datetime.fromisoformat(gen)
            age = (datetime.now(timezone.utc) - dt).days
            if age > FRESH_MAX_DAYS:
                warns.append(f"snapshot is {age} days old (> {FRESH_MAX_DAYS})")
        except ValueError:
            warns.append("unparseable generated_utc timestamp")

    status = "FAIL" if fails else ("WARN" if warns else "PASS")
    return status, fails, warns


def validate_run(market_dir=MARKET_DIR, strict=False, quiet=False):
    def say(*a):
        if not quiet:
            print(*a)

    registry = sv.load_registry()
    say("\n" + "=" * 60)
    say("MARKET DATA VALIDATOR (03b) - cross-checking financials + news")
    say("=" * 60)

    if not os.path.isdir(market_dir):
        say("No market data found (has the Market Agent run yet?).")
        return True, {"overall": "EMPTY"}

    tickers = [d for d in os.listdir(market_dir)
               if os.path.isdir(os.path.join(market_dir, d))]
    if not tickers:
        say("No company snapshots found.")
        return True, {"overall": "EMPTY"}

    results = []
    for tk in tickers:
        snap_path = os.path.join(market_dir, tk, "snapshot.json")
        if not os.path.isfile(snap_path):
            results.append({"ticker": tk, "status": "FAIL",
                            "messages": ["snapshot.json missing"]})
            say(f"\n### {tk}: FAIL\n    - snapshot.json missing")
            continue
        try:
            with open(snap_path, encoding="utf-8") as f:
                snap = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            results.append({"ticker": tk, "status": "FAIL",
                            "messages": [f"snapshot unreadable: {e}"]})
            say(f"\n### {tk}: FAIL\n    - snapshot unreadable: {e}")
            continue

        status, fails, warns = validate_snapshot(snap, registry)
        msgs = fails + [f"(warn) {w}" for w in warns]
        results.append({"ticker": tk, "status": status, "messages": msgs})
        say(f"\n### {tk}: {status}")
        for mmsg in msgs:
            say(f"    - {mmsg}")

    any_fail = any(r["status"] == "FAIL" for r in results)
    any_warn = any(r["status"] == "WARN" for r in results)
    overall = "FAIL" if any_fail else ("WARN" if any_warn else "PASS")

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "overall": overall, "strict": strict, "companies": results,
    }
    try:
        with open(os.path.join(market_dir, "_validation_report.json"),
                  "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    except OSError:
        pass

    say("\n" + "-" * 60)
    for r in results:
        say(f"  {r['ticker']:<10} {r['status']}")
    say("-" * 60)
    say(f"OVERALL: {overall}")

    ok = not any_fail and not (strict and any_warn)
    return ok, report


def main():
    p = argparse.ArgumentParser(description="AMKOR Market Data Validator (03b).")
    p.add_argument("--strict", action="store_true", help="Warnings cause non-zero exit.")
    p.add_argument("--market-dir", default=MARKET_DIR)
    args = p.parse_args()
    ok, _ = validate_run(args.market_dir, strict=args.strict)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
