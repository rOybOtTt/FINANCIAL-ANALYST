# MLCC cycle: history 2000-2026 and leading indicators (as of 2 Oct 2026)

Tags: [FACT] = company primary document or local price data; [ATTRIBUTED] = press/aggregator/broker, not independently verified; [ESTIMATE] = my arithmetic or judgement.
Machine-readable series: `targets/MLCC/data/cycle_indicators.csv`.
Fiscal-year convention: Murata/Taiyo "FY2026" = Apr-2026 to Mar-2027 (Murata's own "FY2026 Q1" = Apr-Jun 2026).

## 0. Source-quality warnings
- BigGo Finance summaries of Taiyo Yuden's 1Q contain wrong numbers (said sales 84.8bn, OP 3.1bn; the company deck says 93.9bn and 4.8bn). Anything cited to BigGo/Bitget/aggregators is [ATTRIBUTED]; use primary decks when re-checking.
- The "Murata orders/backlog 1.27 vs 1.25 in 2018" claim (ldeepai.com / search summary) conflicts with Murata's own reported BBR (total 1.34, MLCC 1.47). Not used.
- No usable sources found for 2004, 2008-10 MLCC-specific operating data (price, utilization, inventory). Those rows rely on stock data only. Gap, not zero information.
- Monthly price file `data/clean/monthly_prices.csv` labels appear to run about one month late vs daily closes (e.g. Yageo's June-2026 high appears under "2026-05"). Pre-2024 peak/trough months are approximate (+/- 1 month); 2026 figures below use daily data.

## A. Cycle chronology

Stock drawdowns = peak-to-trough closing price of the listed names (local data, [FACT] for prices; the drawdown % is [ESTIMATE]). Y = Yageo, W = Walsin, M = Murata, T = Taiyo Yuden, S = SEMCO.

| Cycle | Start | Peak | Trough | Trigger of turn | Price / utilization / inventory | Stock drawdown (peak to trough) |
|---|---|---|---|---|---|---|
| 2000 dot-com | 1999-2000 order surge | Feb-Apr 2000 (T high Apr-00; Y Feb-01; W Jul-01) | Mar 2003 (T, Y, M); Aug 2002 (W) | OEM double/triple ordering of tantalum/MLCC for telecom/internet build-out; bust 2001 | Industry article: shortage cycles "seldom lasted more than 10 to 14 months"; capacity added, then "market does an about-face" [ATTRIBUTED] https://passive-components.eu/capacity-expansion-in-the-global-mlcc-markets/ (undated). Double-ordering inflated demand 3-4x [ATTRIBUTED] https://www.qmscfl.com/the-multilayer-ceramic-capacitor-mlcc-shortage-crisis/ (undated) | T -89%, W -83%, Y -80%, M -60%, S -57% [ESTIMATE] |
| 2004-05 | n/a | n/a | n/a | No MLCC-specific source found | Yageo share price -23% in 2004, +20% in 2005 [ATTRIBUTED] https://companiesmarketcap.com/yageo/stock-price-history/ | not computed (mid-cycle wobble, not a full cycle in stock data) |
| 2007-09 (GFC) | 2006-07 | May-Aug 2007 (M, T May-07; Y, W Jun-07; S Aug-07) | Sep 2008 (T); Oct-Dec 2008 (M, Y, W); Jul 2008 (S) | Global recession, handset/PC demand collapse | Passive-components.eu lists expansions in 1995, 2000, 2007, 2011 [ATTRIBUTED] (same link as above). No price/utilization data found | T -84%, W -82%, Y -74%, M -64%, S -45% [ESTIMATE] |
| 2010 boom / 2011 bust | 2009 recovery | Feb-May 2010 (T Feb, W Mar, S May); Dec-10 (M); Apr-11 (Y) | Jul-Nov 2011 (S, T, Y); Sep-12 (W); Jul-12 (M) | Restocking boom, then capacity add / destock | No MLCC-specific price or utilization source found (gap) | T -61%, W -67%, S -56%, Y -49%, M -36% [ESTIMATE] |
| 2017-18 super-cycle | Mar-2017 (shortage "March 2017-March 2018") | Peak pricing / allocation Q2-Q3 2018; Yageo intraday ATH NT$1,310 Jul-2018 (pre-split) | Stocks: W Sep-18, T Nov-18, Y Apr-19, S Jul-19. Fundamentals: Murata FY2019 Q1 (Apr-Jun 2019) | Smartphone and auto pull + Japanese capacity shifted to high-end; then US-China trade war demand slump from Sep-2018, customer destock | Yageo raised price 4 times in 2017; standard parts up 5-10x, lead times 4-8 wks to 30+ wks [ATTRIBUTED] https://www.semimedia.cc/yageo-may-increase-the-mlcc-price-by-40-50/ . Chairman Jun-2018: book-to-bill 3, orders 2x shipments [ATTRIBUTED] https://www.taipeitimes.com/News/biz/archives/2018/06/12/2003694718 . Dec-2018: distributor inventory 6-7 months vs 2-3 normal; Yageo ASP -15% QoQ 1Q19 and -10% 2Q19 (forecast) [ATTRIBUTED] https://www.taipeitimes.com/News/biz/archives/2018/12/17/2003706238 . Murata Apr-2019: "customers and the market have higher-than-normal levels of capacitor inventories" [FACT] https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2019/0426b/18q4-e.ashx . Murata capacitor BBR FY2019 Q1 0.80, Q2 0.85 [FACT] (fact book 2022, below) | Y -72%, W -68%, T -51%, S -44%, M -30% [ESTIMATE] |
| 2020-21 COVID boom | Apr-Jun 2020 (Murata FY2020 Q1 BBR 0.90) | Murata orders peak FY2021 Q1 (Apr-Jun 2021): total 495.2bn JPY, BBR 1.13; capacitor orders 223.8bn, BBR 1.18; total backlog peak 503bn at Sep-2021 [FACT] https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2022/0713/factbook2022.ashx | Orders trough FY2022 Q4 (Jan-Mar 2023): total 313.8bn (-37% vs peak), capacitors 139.3bn (-38%) [FACT] | WFH electronics + chip-shortage over-ordering; reversal as inventories built | Yageo 2020: lead times 45 to 90 days, +10% commercial price [ATTRIBUTED] https://www.eetasia.com/what-does-2020-hold-for-the-mlcc-market/ . Murata capacitor BBR 1.32 in Jan-Mar 2021 [FACT] | Stocks Jan/Nov-2021 high to Aug/Nov-2022 low: W -68%, Y -52%, S -45%, T -43%, M -33% [ESTIMATE] |
| 2022-23 correction | Jul 2022 (BBR 0.91, then 0.78) | n/a | Orders FY2022 Q4; backlog trough 290bn at Dec-2023 (total), capacitor backlog trough 124bn at Sep-2023 [FACT] https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2024/0628b/factbook2024.ashx | Destocking. Murata total BBR 0.98, 0.91, 0.78, 0.90 through FY2022 | Murata inventory 575bn JPY Mar-2023 to 513bn Mar-2024 [FACT]. Mid-2023: Japanese plants ~90% utilization, China makers 60-70% [ATTRIBUTED] https://www.morningstar.com/stocks/we-expect-mlcc-suppliers-margins-recover-h2 . Price declines modest vs prior downturns [ATTRIBUTED] same link | see 2020-21 row |
| 2024 recovery | Jan-Mar 2024 (BBR turned 1.05) | n/a (gradual) | n/a | AI/auto/infra recovery, FY2024 capacitor BBR 1.05, 0.96, 0.97, 1.03 [FACT] | Murata capacitor sales FY2024 832.7bn JPY (+9.7%) [FACT] fact book 2026. Taiyo: price declines still ongoing | n/a |
| 2025-26 AI-server cycle | FY2025 Q3 (Oct-Dec 2025): total BBR 1.07, backlog 336bn | Not yet. Latest: Murata FY2026 Q1 BBR 1.34 / MLCC 1.47; Yageo BB 2.2 (end-Jun); Taiyo capacitor BB 1.72 | Not yet. Equities: 2026 closing highs 19 Jun to 1 Jul, then -49% to -62% by Jul-Sep lows [ESTIMATE] | AI server needs 10-15x the MLCCs of a conventional server [ATTRIBUTED]; high-end capacity takes 18-24 months to add [ATTRIBUTED] https://passive-components.eu/yageo-announces-july-2026-capacitor-price-increase/ | Murata util "very close to 95%" [FACT]; SEMCO 91% (Jun) [ATTRIBUTED]; Yageo ~80-85% 2Q, >90% 3Q guide [ATTRIBUTED]; channel inventory <30 days [ATTRIBUTED]. Details in B and C | 2026 closing high to trough: Y -60%, M -49%, S -61%, T -62% (trough 14 Sep); last close vs high: Y -45%, M -31%, S -30%, T -55% [ESTIMATE] |

Observations for the thesis [ESTIMATE]:
1. Equities have peaked before fundamentals in every cycle with data: Yageo's stock peaked May-Jul 2018, Murata's capacitor BBR was still above 1 into FY2018, and orders cracked in Apr-Jun 2019. In 2026 shares already round-tripped 50-60% in July while orders kept accelerating.
2. Order peak-to-trough in the last full cycle was -37% to -38% for Murata over 7 quarters (FY2021 Q1 to FY2022 Q4).
3. Prior shortage cycles (1995, 2000, 2007, 2011, 2017-18) are described as lasting 10-14 months before capacity arrived [ATTRIBUTED, passive-components.eu]. The current one is roughly 9-12 months old (price actions began Feb-Apr 2026); capacity adds are being pushed out to 2027 [ATTRIBUTED, TrendForce 18 Aug 2026].

## B. Leading indicators, latest readings

### B1. Murata (Apr-Jun 2026 results, released 31 Jul 2026)

| Item | Reading | Tag | Source |
|---|---|---|---|
| Revenue 1Q FY2026 | 502.3bn JPY, record, +20.7% YoY | FACT | https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0731d/26q1-e-speach.ashx (31 Jul 2026) |
| Operating profit | 98.5bn JPY, +59.8% YoY | FACT | same |
| Total book-to-bill | 1.34 | FACT | same |
| MLCC book-to-bill | 1.47 | FACT | same |
| Capacitor orders / backlog | 415.5bn / 402.2bn JPY (backlog 269.2bn at Mar-2026) | ATTRIBUTED | https://www.bitget.com/news/detail/12560605591446 (2 Aug 2026); Mar-26 backlog FACT in fact book 2026 |
| Total orders (derived) | about 673bn JPY (1.34 x 502.3) | ESTIMATE | derived |
| Utilization | "very close to 95%" | FACT | same speech |
| Inventory | +18.5bn JPY QoQ at Jun-2026; H1 build to be below the 17bn plan | FACT | same speech |
| Pricing | Price declines still a 15bn JPY YoY headwind, "smaller than a normal year". Management said some "adjustments" may be needed; no general hike announced | FACT / ATTRIBUTED | speech; https://www.bitget.com/news/detail/12560605591446 |
| FY2026 guidance (raised) | Revenue 2,110bn (from 1,960), OP 430bn (from 380), data-center sales 370.6bn (from 325), capex 225bn | ATTRIBUTED | https://finance.biggo.com/news/JP_6981.T_2026-07-31 |
| Data-center MLCC outlook | +35-40% QoQ, about +80% YoY | ATTRIBUTED | same |
| Capacity actions | Sep 2026: notifying discontinuation of selected part numbers across nine MLCC series, last orders Mar 2028 | ATTRIBUTED | https://www.ftcelectronics.ph/news/murata-to-discontinue-selected-mlccs-across-nine-series,reshaping-supply-options |

Murata quarterly orders, book-to-bill, backlog (JPY bn; FY = Apr-Mar start year). Total orders and capacitor orders. Full series in CSV.

| FY | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| FY2019 total orders (BBR) | 339.1 (0.95) | 392.3 (0.97) | 413.1 (1.01) | 362.5 (1.00) |
| FY2020 | 293.5 (0.90) | 475.7 (1.12) | 536.4 (1.15) | 516.2 (1.26) |
| FY2021 | 495.2 (1.13) | 480.4 (1.03) | 449.9 (0.96) | 471.6 (1.09) |
| FY2022 | 426.5 (0.98) | 439.7 (0.91) | 324.8 (0.78) | 313.8 (0.90) |
| FY2023 | 361.0 (0.98) | 419.8 (0.95) | 419.2 (0.95) | 410.5 (1.05) |
| FY2024 | 429.9 (1.02) | 426.7 (0.92) | 449.3 (1.00) | 414.9 (1.01) |
| FY2025 (ATTRIBUTED; BBR derived) | 431.1 (1.04) | 487.0 (1.00) | 500.7 (1.07) | 570.7 (1.24) |
| FY2026 | about 673 (1.34) | | | |
| Capacitor orders (BBR) FY2019 | 110.3 (0.80) | 117.5 (0.85) | 156.2 (1.07) | 154.5 (1.12) |
| FY2020 | 117.5 (0.87) | 167.0 (1.07) | 199.8 (1.19) | 222.6 (1.32) |
| FY2021 | 223.8 (1.18) | 198.1 (0.98) | 189.9 (0.95) | 211.6 (1.10) |
| FY2022 | 197.5 (0.98) | 164.9 (0.85) | 144.3 (0.79) | 139.3 (0.87) |
| FY2023 | 164.3 (0.97) | 190.3 (0.97) | 203.7 (1.03) | 200.5 (1.06) |
| FY2024 | 213.2 (1.05) | 204.7 (0.96) | 207.2 (0.97) | 207.6 (1.03) |
| FY2025 capacitor BBR | 1.03 | 1.01 | n/a | n/a |
| FY2026 | 415.5 (1.47) | | | |

Sources: FY2019-21 https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2022/0713/factbook2022.ashx ; FY2022 https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2024/0628b/factbook2024.ashx ; FY2023-24 https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0626/factbook2026.ashx [FACT]. FY2025 orders via search summary of https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2025/1031b/25q2-e.ashx plus backlog cross-check to fact book 2026.
Gap: FY2017-FY2018 quarterly orders not found (older fact books not retrievable). FY2017/18 annual capacitor sales 449.8bn / 574.2bn JPY [FACT, fact book 2022].

Backlog (JPY bn, total / capacitors): Jun-21 490.7/224.3 (peak area); Mar-23 339.8/135.9; Sep-23 310.2/124.0 (cap trough); Dec-24 284.4/135.9; Jun-25 302.5/148.7; Dec-25 336.1/181.8; Mar-26 446.2/269.2; Jun-26 capacitors 402.2 [ATTRIBUTED]. Capacitor backlog has risen 2.7x in 12 months and is 1.8x its 2021 peak [ESTIMATE].

### B2. Taiyo Yuden (Apr-Jun 2026, released 5 Aug 2026) [FACT: https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260805/20260805509466.pdf]

| Item | Reading |
|---|---|
| Net sales / OP | 93.9bn JPY (+5% QoQ) / 4.8bn JPY (+39% QoQ) |
| Capacitor orders | +41% QoQ |
| Order backlog | +78% QoQ |
| Book-to-bill | 1.72 capacitors; 1.58 all products |
| Price | "Pace of price decreases ... improved significantly" vs prior quarter |
| FY3/27 guidance (raised) | Sales 424.0bn (+19%), OP 45.0bn (+125%), capex 42bn |
| Capacitor utilization | about 85% in 1Q [ATTRIBUTED https://finance.biggo.com/news/JP_6976.T_2026-08-05]; confirm in deck |
| Price actions | Apr 2026: 10-30% automotive, 6-13% consumer; further adjustment effective 1 Sep 2026 [ATTRIBUTED https://www.trendforce.com/news/2026/08/04/news-across-the-board-30-price-hike-mlcc-price-surge-intensifies/] |
| Alliance | TDK and Taiyo Yuden exploring a business alliance on advanced MLCCs/inductors, 29 Sep 2026 [ATTRIBUTED https://passive-components.eu/september-2026-interconnect-passives-and-electromechanical-components-market-insights/] |

### B3. SEMCO (2Q26, reported 30 Jul 2026) [ATTRIBUTED: https://finance.biggo.com/news/KR_009150.KS_2026-07-30]

| Item | Reading |
|---|---|
| Revenue / OP | KRW 3.46tn (+24% YoY) / KRW 440.4bn (+107%), margin 12.7% |
| Component (MLCC) division revenue | KRW 1,649.4bn, +29% YoY, +17% QoQ (no division OP disclosed in sources found) |
| Utilization | 91% as of Jun-2026 (https://en.sedaily.com/finance/2026/09/28/samsung-electro-mechanics-q3-profit-seen-jumping-23-fold-on); "high 90s" in another summary |
| Outlook | Management expected another QoQ revenue rise and record earnings in 3Q; "larger-than-normal" capex |
| LTAs | More than ten hyperscaler LTAs; largest-ever KRW 1.0722tn MLCC deal for 1 Jan-31 Dec 2027; cumulative disclosed AI LTAs KRW 3.32tn (https://www.trendforce.com/news/2026/09/04/news-samsung-electro-mechanics-secures-krw-1-07-trillion-long-term-mlcc-supply-deal-for-ai-servers/, 4 Sep 2026) |
| 3Q26 consensus OP | KRW 605bn (2.3x YoY) (sedaily, 28 Sep 2026) |
| Price | +30% on all MLCC categories from 1 Aug 2026; 4Q26 OEM/ODM hike 25-30% consumer X5R, 10-20% high-end X6S (first time hitting OEMs, not only distributors) (https://www.trendforce.com/presscenter/news/20260827-13202.html, 27 Aug 2026) |

### B4. Yageo and Walsin (Taiwan monthly revenue, NT$ bn)

| Month | Yageo | MoM | YoY | Walsin | MoM | YoY |
|---|---|---|---|---|---|---|
| Jun-2026 | 15.359 | +2.0% | +38.9% | 3.961 | +7.1% | +25.8% |
| Jul-2026 | 16.131 | +5.0% | +51.5% | 4.443 | +12.2% | +42.0% |
| Aug-2026 | 16.332 | +1.2% | +51.8% | 4.569 | +2.8% | +45.5% |
| YTD Jan-Aug | 115.085 (+34.9%) | | | 29.941 (+22.1%) | | |

[ATTRIBUTED] Yageo: https://news.cnyes.com/news/id/6600434 , https://news.cnyes.com/news/id/6568348 , https://tw.stock.yahoo.com/news/%E5%9C%8B%E5%B7%A8-%E8%87%AA%E7%B5%90%E5%89%8D8%E6%9C%88%E5%90%88%E4%BD%B5%E7%87%9F%E6%94%B61150-85%E5%84%84%E5%85%83-%E5%B9%B4%E5%A2%9E34-9-074400388.html (Aug release 8 Sep 2026). Walsin: https://news.cnyes.com/news/id/6601760 (9 Sep), https://finance.technews.tw/2026/08/10/industry-academia/ , https://money.udn.com/money/story/5710/9615386 . Yageo has hit six straight record months; Aug was Walsin's highest since Nov 2018.

| Item | Reading | Source (all ATTRIBUTED) |
|---|---|---|
| Yageo 2Q26 | Revenue NT$44.5bn (+35.7% YoY, +16.5% QoQ); book-to-bill 2.2 by end-June | https://finance.biggo.com/news/TW_2327.TW_2026-07-29 (29 Jul 2026) |
| Yageo utilization | 2Q: commodity about 80%, specialty about 85%; 3Q guide both above 90% | same |
| Yageo channel inventory | China distribution about 2 months, global distribution 4 months, high-service channels 5-6 months, all better YoY | same |
| Yageo pricing | 1 Jul 2026: list price about +50% across MLCC, aluminium, tantalum, polymer, film, supercaps; first time extended to direct customers (over 50% of revenue); spot on some high-end parts up to nearly 10x since May | https://passive-components.eu/yageo-announces-july-2026-capacitor-price-increase/ (1 Jul 2026) |
| Walsin | Book-to-bill above 1.8 for 2-3 months (was 1.4); order visibility to year-end, partly 2027; consumer MLCC +5-15% from Jun/Jul; chairman: price rises "inevitable" | https://finance.technews.tw/2026/08/10/industry-academia/ ; https://www.trendforce.com/news/2026/08/04/news-across-the-board-30-price-hike-mlcc-price-surge-intensifies/ |
| Walsin CEO (Jun) | Tightness may persist beyond 2027 into 2028; MLCC utilization 80-85%; MLCC capacity +15% this year | https://finance.biggo.com/news/2TUNwZ4BHDAP3F-7ILW3 (12 Jun 2026) |
| Equity reaction | Yageo peak about NT$1,140 close (30 Jun); Goldman/MS/Citi trimmed targets in late Jul on "more conservative" price-hike assumptions (multiple compression, EPS raised) | https://finance.biggo.com/news/5284bd26-3667-4cc0-9090-835f09eb7cd2 |

### B5. Channel, lead times, price notices, Japan data

| Item | Reading | Tag / source |
|---|---|---|
| June 2026 monthly MLCC shipments | Murata 140bn pcs, SEMCO 98bn, Taiyo 40bn: five-year highs | ATTRIBUTED https://www.trendforce.com/presscenter/news/20260728-13155.html (28 Jul 2026) |
| Channel inventory | Mainstream MLCC below 30 days; agent prices +20-25%; spot 2-3x | ATTRIBUTED same |
| Lead times | Standard cases 14-18 weeks; high-cap/high-voltage 15-20; some SEMCO high-cap about 40 weeks (DigiKey). Capacity planned for 4Q26 pushed into 2027 | ATTRIBUTED https://www.trendforce.com/news/2026/08/18/news-mlcc-lead-times-diverge-as-high-end-products-stretch-to-5-10-months-on-ai-demand-tightness-may-extend-into-2027/ (18 Aug 2026) |
| Lead times (broker view) | 32-52 weeks including standard commercial parts (higher than TrendForce, likely vendor-skewed) | ATTRIBUTED https://www.astutegroup.com/news/general/mlcc-shortages-deepen-as-ai-demand-extends-lead-times/ |
| Distributor demand | Bookings/POS accelerating, B2B 1.2-1.3x; MLCC to tighten further into 1H27, relief 2H27/2028 | ATTRIBUTED https://passive-components.eu/september-2026-interconnect-passives-and-electromechanical-components-market-insights/ |
| Fusion Worldwide | Capacitor search demand +42% over 90 days; 26-40 week lead times on constrained families | ATTRIBUTED https://info.fusionww.com/blog/mlcc-supply-is-tightening-faster-than-buyers-can-ignore |
| JEITA | April 2026 Japanese passive-component shipments 231.4bn JPY, +18% YoY; capacitor shipments record (released 30 Jun 2026). Later months not found | ATTRIBUTED https://www.bitget.com/news/detail/12560605484739 |
| Japan trade | July 2026 total exports +23.2% YoY (chips-led); no component-level figure | ATTRIBUTED https://www.cnbc.com/2026/08/20/japan-exports-imports-july-chip-ai.html |
| Price notices 2026 | Taiyo Apr; Murata 1 Apr on ferrite beads/inductors (silver cost; MLCC % not confirmed) https://www.trendforce.com/news/2026/03/17/news-mlcc-giant-murata-reportedly-confirms-april-1-price-hike-on-key-components/ ; SEMCO 1 Aug +30%, 4Q OEM hike; Yageo 1 Jul +50% list; Walsin Jun/Jul +5-15% | ATTRIBUTED |
| Japanese big three | Murata, Taiyo, Kyocera announced no 4Q price change; "wait-and-see" | ATTRIBUTED https://www.trendforce.com/presscenter/news/20260827-13202.html |

Not found: Sourceability/Avnet quantified lead-time reports (only a vendor note that Avnet shows stock at 10 weeks on specific parts); Taiyo/TDK monthly utilization from primary sources; JEITA May-Aug 2026 data; Yageo Jan-May monthly revenue.

## C. Where is the cycle now (Oct 2026)?

| Lens | Reading | Verdict [ESTIMATE] |
|---|---|---|
| Source labels | TrendForce 27 Aug: MLCC "officially entered an upcycle" after SEMCO's OEM hike; mentions upward price trajectory in 4Q26 and a possible Japanese price move as "next phase" | Early-to-mid upcycle in price |
| Orders/backlog | Murata BBR 1.34 (1.47 MLCC), capacitor backlog about 3x year-ago; Taiyo BB 1.72; Yageo 2.2; Walsin above 1.8. Murata 2018-19 reference: capacitor BBR above 1 through FY2018, then 0.80 | Mid-cycle on orders; BBR already above the 2020-21 peak (total 1.26, capacitors 1.32 in Jan-Mar 2021) |
| Utilization | Murata about 95%, SEMCO 91%, Yageo 80-85% heading to above 90%, Walsin 80-85% | Japan/Korea full; Taiwan/China still absorbing spillover, i.e. room left for volume |
| Price | Hikes led by SEMCO (+30%) and Yageo (+50% list); Murata still reports net price decline (-15bn JPY YoY) and no general hike | Price pass-through incomplete; Murata/Taiyo hikes would be the next leg |
| Channel inventory | Below 30 days (TrendForce) vs Yageo's 2-6 months by channel: sources disagree on definition | Lean, but conflicting; refine with distributor data |
| Capacity | High-end adds take 18-24 months; 4Q26 additions pushed to 2027; Murata culling part numbers (like 2018 EOLs) | Supply response lagging; relief 2H27-2028 per distributors; Walsin CEO says possibly 2028 |
| Equities | Peaked late Jun/1 Jul; down 30-55% from highs today | Market already pricing a peak-or-pause; historically stocks lead fundamentals by 2-4 quarters |

Overall [ESTIMATE]: early-to-mid upcycle for fundamentals (orders still accelerating, price pass-through incomplete, utilization at ceiling only in Japan/Korea), but the equity cycle looks mid-to-late. Main sources saying "early": TrendForce (upcycle start), Walsin and distributors (tightness into 2H27-2028). Counter-signals to monitor: customer double-ordering (Murata notes some distributor orders are "large quantities"), consumer-electronics demand "subdued", TrendForce warning that China/US slowdown may weaken the 2H26 peak season, and the 2018 pattern where book-to-bill of 3 preceded a 2019 inventory glut.

Price-hike announcements 2026 (all [ATTRIBUTED]): Taiyo Yuden Apr (10-30% auto, 6-13% consumer) and 1 Sep; Murata 1 Apr (inductors/ferrites; MLCC magnitude unverified); SEMCO Aug +30%, 4Q OEM +10-30%; Yageo 1 Jul +50% list; Walsin Jun/Jul +5-15%, direct-customer talks in 3Q-4Q. AI-server shortage of high-capacity MLCC: 10uF-and-up allocated, up to 40 weeks; one rack up to 440,000 MLCCs (TrendForce, 4 Aug 2026).

## D. Catalyst calendar, Oct 2026 - Feb 2027

Dates marked "confirmed" were stated by an aggregator; "est." are my inference from prior-year timing. Verify against company IR calendars before use.

| Date | Event | Status / source |
|---|---|---|
| About 8-9 Oct 2026 | Yageo and Walsin Sep revenue (Taiwan deadline the 10th; Aug releases came 8 and 9 Sep) | est. |
| Mid-Oct 2026 | TrendForce MLCC bulletin and 4Q contract price read-through; Japan Sep trade data (about 21 Oct) | est. |
| 27 Oct 2026 | Yageo 3Q26 results | aggregator date https://www.investing.com/equities/yageo-corp-earnings |
| 29 Oct 2026 | Kyocera 2Q FY2027 results | aggregator https://www.investing.com/equities/kyocera-corp.-earnings |
| About 29-30 Oct 2026 | SEMCO 3Q26 results (3Q25 was 29 Oct 2025) | est. |
| 30 Oct 2026 | Murata 2Q FY2026 results (watch BBR, MLCC price stance, utilization, FY guidance) | aggregator https://www.investing.com/equities/murata-mfg-co-earnings |
| 30 Oct 2026 | TDK 2Q FY3/27 results | aggregator https://www.investing.com/equities/tdk-corp.-earnings |
| 5 Nov 2026 | Taiyo Yuden 2Q FY3/27 results | aggregator https://www.investing.com/equities/taiyo-yuden-co.,-ltd.-earnings |
| About 5-10 Nov 2026 | Walsin 3Q26 results/call (date not found) | est. |
| About 9-10 Nov 2026 | Yageo and Walsin Oct revenue | est. |
| About 9-10 Dec 2026 | Nov revenue | est. |
| Nov-Dec 2026 | Supplier replenishment windows: SEMCO Nov, Yageo Dec, one Murata line Jan 2027 (TrendForce 18 Aug); whether Murata/Taiyo/Kyocera join 4Q-1Q price hikes | ATTRIBUTED |
| About 8-11 Jan 2027 | Dec revenue and 4Q total for Yageo, Walsin | est. |
| About 27-30 Jan 2027 | SEMCO 4Q26; Kyocera 3Q (late Jan); TDK 3Q (about 30 Jan) | est. |
| About 2-5 Feb 2027 | Murata 3Q FY2026 (3Q FY2025 was 2 Feb 2026), Taiyo Yuden 3Q | est. |
| About 9-10 Feb 2027 | Jan revenue for Yageo, Walsin | est. |
| 1 Jan 2027 | Start of SEMCO's KRW 1.07tn single-customer MLCC LTA delivery period | ATTRIBUTED |
| Monthly | JEITA capacitor shipments (about 30th for prior-prior month), Korea ICT/semiconductor exports (1st), TrendForce MLCC price bulletins | est. |
