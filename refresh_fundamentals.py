"""
Refresh fundamentals only (SEC companyfacts XBRL) - no filing re-download.

Re-runs the (fixed, multi-concept-merging) fundamentals extractor over the
current cohort and rewrites each data/<TICKER>/financials.json. Fast, because it
only hits the companyfacts endpoint - not the filing archive.

  python refresh_fundamentals.py                 # cohort from competitors.json
  python refresh_fundamentals.py NVDA AMD TSM     # explicit tickers
"""

import json
import os
import sys

import data_agent as da

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
COMPETITORS = os.path.join(HERE, "competitors.json")


def cohort(argv):
    if argv:
        return [a.upper() for a in argv]
    with open(COMPETITORS, encoding="utf-8") as f:
        return [c["ticker"] for c in json.load(f)["companies"]]


def main():
    fetcher = da.UrllibFetcher()
    tmap = da.load_ticker_map(fetcher)
    for q in cohort(sys.argv[1:]):
        resolved = da.resolve_company(q, tmap)
        if not resolved:
            print(f"{q:<10} NOT FOUND on EDGAR (foreign/non-SEC) - skipped")
            continue
        cik, ticker, title = resolved
        try:
            cik10 = str(cik).zfill(10)
            facts = fetcher.get_json(da.COMPANYFACTS_URL.format(cik10=cik10))
            fin = da.extract_financials(facts, ticker, cik)
        except Exception as e:
            print(f"{q:<10} no companyfacts ({e})")
            continue
        out_dir = os.path.join(DATA, da.slugify(ticker))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "financials.json"), "w", encoding="utf-8") as f:
            json.dump(fin, f, indent=2)
        annual = fin.get("annual", {})
        yrs = sorted(annual.keys(), reverse=True)
        latest = annual.get(yrs[0], {}) if yrs else {}
        rev = latest.get("revenue")
        rev_s = f"{rev/1e9:.1f}B" if isinstance(rev, (int, float)) else "n/a"
        print(f"{ticker:<10} FY{yrs[0] if yrs else '----'} rev={rev_s} "
              f"GM={latest.get('gross_margin_pct')}%  ({len(yrs)} yrs: {','.join(yrs)})")


if __name__ == "__main__":
    main()
