# MLCC capacity, share, utilization, supply risk (retrieved 2026-10-02)

Tags: [FACT] = company filing/IR; [ESTIMATE] = analyst/derived; [ATTRIBUTED] = press/secondary, unverified. Full row-level data with URLs: `../data/capacity.csv`.
Caveat: no company publishes bn pcs/month capacity. TrendForce June-2026 *shipments* are used as a capacity proxy.

## 1. Capacity (bn pcs/month) and expansions
| Company | Capacity / proxy | Expansion & capex | Source (date) | Tag |
|---|---|---|---|---|
| Murata | 140 shipped Jun-26 (utilization ~95% => capacity ~145-150, my inference) | Izumo bldg done (¥47bn, Apr-26); Philippines Batangas ¥11.2bn; Thailand 2023, Iwami 2023, Wuxi 2024; +¥80bn more MLCC capex, phase 1 output 4Q27, phase 2 2028-29; group capex ¥255bn FY3/27 | [TrendForce](https://www.trendforce.com/presscenter/news/20260728-13155.html) (2026-07-28); [Murata IR](https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0731d/26q1-e-speach.ashx) (2026-07-31); [Evertiq](https://evertiq.com/design/2026-04-07-murata-completes-new-mlcc-production-building-in-japan) (2026-04-07); [BigGo](https://finance.biggo.com/news/c224320e-798a-4ff7-9b35-b97c4f358d4a) (2026-09-04) | shipments [ESTIMATE]; capex [FACT]/[ATTRIBUTED] |
| SEMCO | 98 shipped Jun-26 (one source: ~100 capacity) | Capex 3trn KRW 2026 -> 6trn 2027 (all businesses); Philippines Plant 3 >1trn KRW; Busan up to +20%/yr; Tianjin 24h | [Korea Herald](https://www.koreaherald.com/article/10829283) (2026-08-03); [BigGo](https://finance.biggo.com/news/cf7fa6ce-e7c4-45b2-a240-ce51b159f08c) | [ESTIMATE]/[ATTRIBUTED] |
| Taiyo Yuden | 40 shipped Jun-26 | Capex ¥42bn FY3/27; Malaysia plant pulled forward; Niigata Bldg 4 ¥15bn (2019 ann.); Sarawak RM680m | [BigGo](https://finance.biggo.com/news/JP_6976.T_2026-08-05) (2026-08-18) | [FACT] |
| TDK | not found | Passive-components capex ¥200bn (one secondary source); TDK-Taiyo Yuden alliance 2026-09-29 (joint MLCC/inductor R&D, possible capital tie) | [mreport](https://www.mreport.co.th/en/news/industry-movement/110-japan-electronic-components-ai-outlook-2026); [BigGo](https://finance.biggo.com/news/035d3747-1fcd-4ce7-8fbe-2285212e590c) | [ATTRIBUTED] |
| Yageo (incl. KEMET) | not found | "No 2026 capacity expansion" in one summary but call cites sites Kaohsiung, Vietnam, Suzhou, Mexico; H1 capex <NT$3bn, larger in H2 | [BigGo](https://finance.biggo.com/news/TW_2327.TW_2026-07-29) (2026-08-03) | [FACT]/conflict flagged |
| Walsin | ~8bn/mo automotive passive (older claim) | +10% end-2026, +10% 2027; capex ~NT$4bn (vs NT$0.5-1bn history) | [BigGo](https://finance.biggo.com/news/d478cae8-9d09-41bb-a303-118140ab45e9) (2026-08-10) | [ATTRIBUTED] |
| Fenghua | 50 (claimed; +15.1 Xianghe, verified Apr-26) | 3-stage RMB7.5bn program complete | [Sohu](https://www.sohu.com/a/1068548263_122066679); [Sina](https://finance.sina.com.cn/jjxw/2026-05-29/doc-inhzpsps8042876.shtml) | [ATTRIBUTED] |
| Three-Circle | secondary claim 55 -> 100 by end-2026 (unverified; verify vs. filing) | High-cap MLCC project RMB1.861bn spent, ready 2027-05-31 | [36Kr](https://eu.36kr.com/en/p/3989788780903169) (2026-09-20) | [FACT] (project) / low-confidence (capacity) |
| Holy Stone | n/a | +NT$3bn (Hokkaido line, Yilan Lize) | [DigiTimes](https://www.digitimes.com/news/a20260326PD207/holy-stone-capacity-mlcc-taiwan-production.html) (2026-03-26; blocked, via snippet) | [ATTRIBUTED] |
| Kyocera AVX, Eyang, Samwha, Darfon | not found | Kyocera AVX: 47uF 0402 mass production Dec-25 | [passive-components.eu](https://passive-components.eu/kyocera-avx-unveils-world-first-mlcc-with-industry-highest-capacitance-47%CE%BCf-in-0402-size/) | gap |

Industry context: 2025 demand ~5trn pcs/yr; AI servers ~2-3% of units but ~10% of capacity ([BigGo](https://finance.biggo.com/news/BCo4np4BrAZSr0oSUIyJ), 2026-06-06) [ESTIMATE]. Expansion lead time 18-24 months; equipment 10-16 months [ATTRIBUTED].
Conflict: Murata capacity growth ">20% load-based" ([36Kr](https://eu.36kr.com/en/p/3989788780903169)) vs "10-15%" ([BigGo](https://finance.biggo.com/news/c224320e-798a-4ff7-9b35-b97c4f358d4a)).

## 2. Market share
| Company | Value share (global) | AI-server share | Source |
|---|---|---|---|
| Murata | ~40% | ~45% | [passive-components.eu](https://passive-components.eu/mlccs-in-the-age-of-ai-q2-2026-market-tightness/) (2026-06-30) |
| SEMCO | ~18% (vs 24% H1-24, conflict) | ~40% | same; [2025 piece](https://passive-components.eu/chinas-mlcc-makers-reach-10-market-share/) (2025-06-16) |
| TDK | ~12% | <5% | same |
| Taiyo Yuden | ~10% | <4% | same |
| Yageo | ~10% | ~3% | same |
| Kyocera AVX | ~5% | <2% | same |
| China makers | 10% (H2-24; 6% in 2019) | n/a | 2025 piece |

All [ATTRIBUTED]; underlying Paumanok/TrendForce data paywalled. Murata #1, SEMCO #2 in AI-server; together ~80-85% of AI-grade. Unit-share data not found. Taiwan makers ~25% of global capacity in 2023 (search snippet, unverified).

## 3. Utilization and inventory
| Company | Utilization | Date | Source |
|---|---|---|---|
| Murata | ~95% | Sep-26 | BigGo above [ATTRIBUTED] |
| SEMCO | Busan mid-90s Q2, high-90s Q3 | 2026 | BigGo [ATTRIBUTED]; components 91% end-Jun (Digitimes snippet) |
| Taiyo Yuden | ~85% Q1 FY3/27 (target high-80s) | Aug-26 | [FACT] |
| Yageo | commodity ~80%->>90%; specialty ~85%->>90% (earlier ~70%/~80%) | Q2-Q3 26 | [FACT] |
| Walsin | MLCC 80-85%; "near full" Aug | 2026 | [ATTRIBUTED] |
| China makers | 82-86% (one snippet) | n/a | weak |

Inventory: mainstream channel <30 days (TrendForce 2026-07-28); Yageo Greater China distributors ~2 months, global ~4 months; global channel inventory -8% m/m Aug-26 (UBS via 36Kr). Murata capacitor inventory fell slightly Q1 FY3/27. Gap: 2022-2025 utilization time series (only 60-70% Taiwan lows in snippets, no source).

## 4. MLCC revenue
| Company | Figure | Source | Tag |
|---|---|---|---|
| Murata | Capacitors ¥936.4bn FY3/26 (+12.6%, ~51% of ¥1,830.9bn); Q1 FY3/27 ¥282.5bn (+30% y/y); FY3/27E ¥1,157.5bn (+23.6%) | Murata IR 2026-07-31 | [FACT] |
| SEMCO | Component Solutions KRW5.199trn FY25 of 11.3145trn (~46%); Q2-26 1.649trn (+29%) | [SEMCO](https://m.samsungsem.com/global/newsroom/news/view.do?id=10042); [TrendForce](https://www.trendforce.com/news/2026/08/04/news-across-the-board-30-price-hike-mlcc-price-surge-intensifies/) | [FACT]; division includes non-MLCC |
| Taiyo Yuden | Capacitors ¥233.2bn FY3/25 (69%); Q1 FY3/27 ¥69.0bn (+14.7%) | [ir-tracker](https://www.ir-tracker.com/en/articles/6976-2026-Q3) | [FACT] (FY3/26 figure not retrieved) |
| TDK | Passive components ¥593.2bn FY3/27E (~20% of revenue); MLCC split not found | mreport | [ATTRIBUTED] |
| Yageo | Q2-26 revenue NT$44.5bn, AI 16%; MLCC share not found | BigGo | [FACT] |
| Walsin | MLCC 46.4% of Q1-26 revenue NT$9.56bn (~NT$4.4bn) | [BigGo](https://finance.biggo.com/news/TW_2492.TW_2026-05-27) (2026-05-27) | [FACT]/derived |
| Three-Circle | H1-26 revenue RMB6.42bn total (+54.8%); MLCC split not found | [QQ](https://news.qq.com/rain/a/20260827A0ACDX00) | [FACT] |
| Fenghua | Q1-26 revenue RMB1.51bn; H1 high-end ~40% of MLCC revenue | BigGo; [ifeng](https://i.ifeng.com/c/8wPsJ8fsA7r) | [FACT] |
| Holy Stone | MLCC ~$0.45bn 2024 | TrendForce datatrack | [ESTIMATE] |

## 5. Product positioning / moat
| Item | Data | Source |
|---|---|---|
| Layers / thickness | Leaders <0.5um, >1,500 layers; Chinese ~1um, ~1,000 layers | passive-components.eu 2026-06-30 [ATTRIBUTED] |
| Yield | Standard >99%; ultra-high-cap AI MLCC ~40%; cycle 27 vs >50 days | BigGo 2026-06-06 [ATTRIBUTED] |
| Content | GB200 NVL72 rack ~440k MLCCs; Vera Rubin ~800k/accelerator | TrendForce; Korea Herald [ATTRIBUTED] |
| Taiyo Yuden | 1005M 22uF embeddable for AI servers; strength in package-substrate parts | [Taiyo Yuden](https://www.yuden.co.jp/en/news/category/taiyo_yuden_commercializes_1005m-size_embeddable_multilayer_ceramic_capacitor_with_22-f_capacitance_.html) |
| Kyocera AVX | 47uF in 0402 (2.1x prior) | passive-components.eu [FACT] |
| Chinese entrants | High-end ~40% of Fenghua MLCC revenue | ifeng [FACT] |
In-house dielectric powder (Murata, SEMCO, TY) not verified in this pass: gap.

## 6. Supply-side risks
| Risk | Evidence | Source |
|---|---|---|
| Raw materials | Higher BaTiO3, nickel powder, rare-earth additives cited for price hikes; Indonesia cut nickel ore exports by two-thirds; Sakai Chemical ~25-28% BaTiO3 share | [Archetype](https://www.archetype-research.com/p/sakai-chemical-and-nippon-chemical); BigGo [ATTRIBUTED]. Palladium/silver rising (Walsin call 2026-05-27). Palladium MLCC-specific: not found |
| Prices | SEMCO +30% Aug-1; Yageo ~+50% Jul-1; Walsin +5-15%; Murata stopped general-purpose orders 2026-09-04 | TrendForce 2026-08-04; BigGo |
| Lead times | 20-26 wks (up to 40) | passive-components.eu |
| China entrants | Chinese suppliers could approach 80bn/mo standardized capacity (China market split piece); consumer spot softening (0603-104 RMB30 -> ~10) | [TrendForce](https://www.trendforce.com/news/2026/09/21/news-chinas-mlcc-market-splits-ai-grade-orders-reportedly-stretch-into-2q27-while-consumer-spot-prices-slide/) (2026-09-21) |
| Cycle risk | Walsin: tightness to 2027-28 (undated) | [BigGo](https://finance.biggo.com/news/2TUNwZ4BHDAP3F-7ILW3) |

## Paywalled / unresolved gaps
Paumanok and TrendForce share tables and datatrack capacity charts; DigiTimes (blocked); Murata/TDK/SEMCO MLCC-only revenue; TDK and Kyocera MLCC capacity; Yageo MLCC revenue share; unit share; 2022-25 utilization history; Eyang, Samwha, Darfon data; Taiyo Yuden FY3/26 full-year; Three-Circle capacity claim needs filing check. Several BigGo/Substack sources are aggregators; treat as [ATTRIBUTED].
