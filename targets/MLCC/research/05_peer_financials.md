# 05 Peer financials: methods, sources, gaps (retrieved 2026-10-02)

## Sources by name
- Fiscal.ai (MCP): covers only Murata (XJPX_6981), SEMCO (XKRX_009150), TDK (XJPX_6762), and only the `segments_and_kpis` dataset. No standardized financial statements and no stock prices for any name. Taiyo Yuden, Yageo, Kyocera, Walsin are not in the Fiscal.ai universe.
- Segment data (annual, JPY/KRW mn): Fiscal.ai for Murata (Capacitors rev; Components rev/OP), SEMCO (Component Solutions rev/OP, FY2017-25), TDK (Capacitors, Passive Components rev; Passive Components segment profit, FY2016-25).
- Consolidated financials: Yahoo Finance fundamentals-timeseries API (no crumb needed), all 7 names, 4 fiscal years each plus 0-5 quarterly/half-year points. Currency: JPY / KRW / TWD, mn.
- Consensus, price, market cap, multiples: stockanalysis.com (via WebFetch), 2026-10-02 close.
- FY labels: Japanese FY2025 = year ending Mar-2026; Dec filers FY = calendar year.

## Gaps
- History is 4 fiscal years (FY2022-FY2025 for Mar filers; FY2022-2025 for Dec filers), not 8. Yahoo does not serve older data; EDGAR does not cover these names. FY2017-21 only exists for segment series (SEMCO, TDK). Fix needs company IR/annual reports or a paid feed.
- Quarterly: Japanese names expose only half-year/semi data points (period_end Mar/Sep), not 4 clean quarters; Murata has 3 points. Korea/Taiwan names have 5 quarters. Quarterly rows are labelled `Q:<period_end>` and may be 3M or 6M duration; check before use.
- r_and_d missing for Taiyo Yuden, TDK, Kyocera; capex missing for Taiyo Yuden. eps_diluted/shares_diluted sparse for quarterlies.
- `dividends_per_share` was not available; delivered `dividends_paid_total` (cash flow, mn, negative = outflow). DPS must be sourced separately.
- Not retrieved: Taiyo Yuden capacitor segment, Yageo MLCC/passive segment, Walsin segment; Murata Components OP FY2025 is the segment OP (not capacitors-only OP). Murata capacitors-only OP is not disclosed.
- Consensus: stockanalysis free tier shows only FY1 (and sometimes revenue only). Murata/Taiyo Yuden/TDK/Kyocera/SEMCO/Yageo FY2 estimates are Pro-gated (blank). Walsin forecast page 404: no consensus estimates, price target or ratings. Murata, Taiyo Yuden, TDK, Kyocera, SEMCO: EPS consensus n/a for Japanese names.
- Yahoo quoteSummary (crumb) was rate-limited; Yahoo chart works for prices but was not used.

## Discrepancies / cautions
- Kyocera average target (JPY 3,585) is below the current price (3,668); Yageo target 1,009 implies +61% (possible stale/outlier targets, as the page itself notes). SEMCO +52%.
- Net cash is vendor-defined (stockanalysis) and differs from cash minus Yahoo total debt: SEMCO 240bn (vendor) vs ~444bn (Yahoo cash 2,721bn less debt 2,277bn); Yageo vendor net debt 46.9bn vs Yahoo cash 98.1bn less debt 150.9bn = -52.8bn. Differences come from lease/short-term investment treatment.
- Forward P/E and EV/EBITDA are vendor-computed on their own estimates; Japanese names show forward PE with no visible EPS consensus.
- TDK FY2016 passive components profit (200bn) and OP include pre-restatement/one-off reclassification; use FY2017+ for trend.
- Yahoo Murata FY2025 revenue JPY 1,830,856mn vs Fiscal.ai segments (Components 1,159,734mn + others) consistent; Mar-2025 revenue 1,743,352mn matches company reported.
- Consensus stockanalysis page for Murata labelled FY2027 = FYE Mar-2027; in the CSV that is FY1.
