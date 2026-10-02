"""Builds data/dashboard.json for the MLCC Cycle Watch page.
Every reading below cites a memo in research/ (and through it a URL). Tags:
F = company primary doc / price data, A = attributed (press, aggregator, broker), E = our estimate."""
import json, pandas as pd

AS_OF = "2026-10-02"
NAMES = {"6981.T": "Murata", "009150.KS": "Samsung Electro-Mechanics", "6976.T": "Taiyo Yuden",
         "6762.T": "TDK", "2327.TW": "Yageo", "6971.T": "Kyocera", "2492.TW": "Walsin Technology"}
SHORT = {"6981.T": "Murata", "009150.KS": "SEMCO", "6976.T": "Taiyo Yuden", "6762.T": "TDK",
         "2327.TW": "Yageo", "6971.T": "Kyocera", "2492.TW": "Walsin"}

# ---------- scorecard: same rule as Memory Cycle Watch ----------
# green=0, amber=1, red=2, x weight; score = sum / (2 x total weight of signals with a reading).
# Bands: <25 upcycle intact, 25-49 late upcycle, 50-69 turn underway, >=70 downturn confirmed.
SC = [
 dict(id="SC01", name="Murata capacitor book-to-bill", weight=3, status="green",
      why="Orders over sales turns before price and earnings. In 2018 the capacitor ratio fell from above 1 to 0.80 two quarters before the order trough; in 2021 it peaked one quarter before the stocks bottomed out of the boom.",
      green="Capacitor book-to-bill at or above 1.10 and backlog rising", amber="0.95 to 1.10, or falling two quarters in a row from a peak", red="Below 0.95 (2019 read 0.80; 2022 read 0.79)",
      read="1.47 MLCC / 1.34 total in Apr-Jun 2026, the highest in the series; capacitor backlog ¥402bn, 1.8x the 2021 peak.", src="Murata 1Q FY2026 speech, 31 Jul 2026 [F]; backlog [A]", next="Murata 2Q, 30 Oct 2026"),
 dict(id="SC02", name="Price actions and ASP direction", weight=3, status="green",
      why="MLCC prices normally fall a few percent a year. A broad hike that reaches OEM contracts, not only distributors, has marked every true shortage (2010, 2017-18, 2020-21).",
      green="Hikes broadening to OEM contracts and to the Japanese makers", amber="Hikes confined to distributors or to Taiwan/China makers; Japanese still cutting", red="Hikes withdrawn, or spot below list for 4+ weeks",
      read="SEMCO +30% (1 Aug) and a 4Q OEM hike; Yageo +50% list (1 Jul); Taiyo Yuden Apr and Sep; Walsin +5-15%. Murata still reports a ¥15bn YoY price headwind and no general MLCC hike.", src="TrendForce 4 & 27 Aug 2026; passive-components.eu 1 Jul 2026 [A]; Murata speech [F]", next="Murata/Taiyo/Kyocera 4Q-1Q price stance"),
 dict(id="SC03", name="Lead times", weight=2, status="green",
      why="Lead times stretch while customers still trust the shortage; they shorten first when buffers are full (2018: 30+ weeks fell back within two quarters).",
      green="Stretching or stable above 14 weeks", amber="Shortening for 2 consecutive reports", red="Back below 10 weeks on high-end parts",
      read="Standard 14-18 weeks, high-cap/high-voltage 15-20, some SEMCO high-cap ~40 weeks; capacity planned for 4Q26 pushed into 2027.", src="TrendForce 18 Aug 2026; Fusion Worldwide [A]", next="TrendForce mid-Oct bulletin"),
 dict(id="SC04", name="Channel and customer inventory", weight=3, status="amber",
      why="Double-ordering is how MLCC shortages end. In Dec-2018 distributors sat on 6-7 months against 2-3 normal, and prices fell 15% the next quarter.",
      green="Below ~1.5 months and no double-order talk", amber="Sources disagree, or any maker flags unusually large distributor orders", red="Above 4 months in distribution, or order cancellations",
      read="TrendForce: mainstream channel under 30 days. Yageo: China distribution ~2 months, global 4, high-service 5-6. Murata notes some distributor orders in 'large quantities'.", src="TrendForce 28 Jul 2026; Yageo 2Q call via BigGo 29 Jul [A]; Murata speech [F]", next="Yageo 3Q call, 27 Oct"),
 dict(id="SC05", name="Utilization", weight=2, status="green",
      why="When the leaders run full, volume spills to Taiwan/China and pricing power spreads; the turn starts when the spillover makers fill up and add capacity.",
      green="Japan/Korea above 90% and Taiwan rising", amber="Taiwan/China also above 90% while capex accelerates", red="Leaders falling below 85%",
      read="Murata ~95%, SEMCO 91%, Taiyo Yuden ~85%, Yageo 80-85% guided above 90% for 3Q, Walsin 80-85%.", src="Murata speech [F]; sedaily 28 Sep; BigGo [A]", next="3Q calls, late Oct"),
 dict(id="SC06", name="Taiwan monthly revenue (Yageo, Walsin)", weight=2, status="green",
      why="The only monthly hard number in passives; released by the 10th, a quarter ahead of Japanese results.",
      green="YoY above +20% with the 3-month average rising", amber="YoY positive but MoM falling 2 months in a row", red="YoY negative, or 3 straight MoM declines",
      read="Aug: Yageo NT$16.3bn +51.8% YoY (+1.2% MoM, sixth record); Walsin NT$4.57bn +45.5% (best since Nov 2018).", src="cnyes 8-9 Sep 2026 [A]", next="Sep revenue ~8-9 Oct"),
 dict(id="SC07", name="Capacity and capex response", weight=2, status="amber",
      why="High-end MLCC capacity takes 18-24 months; shortages have historically lasted 10-14 months before new lines arrived. Capex announced now lands in 2H27-2028.",
      green="Capex flat and aimed at high-end; no greenfield pull-ins", amber="One leader steps capex up sharply, or Chinese makers add >20% capacity", red="Two leaders plus China all add in the same year as orders slow",
      read="SEMCO capex ~₩3tn (2026) to ~₩6tn (2027) and Philippines plant 3 in 1Q27; Murata +¥80bn new building, first output 4Q27; Taiyo Yuden Malaysia pulled forward; Three-Circle claims 55 to 100bn pcs/month.", src="02_capacity memo [A]", next="FY27 capex guides, Jan-May 2027"),
 dict(id="SC08", name="AI-server and hyperscaler demand", weight=3, status="green",
      why="AI servers carry 8-15x the MLCCs of a normal server and are the marginal buyer of high-cap parts; hyperscaler capex leads MLCC orders by 1-3 quarters.",
      green="Hyperscaler capex raised or held; next-year growth double-digit", amber="Next-year growth guided below ~15% or a top-4 pause", red="Any top-4 cut",
      read="2026 hyperscaler capex >$700bn, raised through the year; Murata data-center sales guide ¥371bn (from ¥325bn), +80% YoY.", src="Memory Cycle Watch SC08; BigGo 31 Jul [A]", next="Hyperscaler 3Q calls, late Oct"),
 dict(id="SC09", name="Consumer end-demand (phones, PCs)", weight=2, status="amber",
      why="Phones and PCs are still half of MLCC units. In 2018 and 2022 the consumer slump started the destock even while auto and industrial held.",
      green="Phone and PC units growing", amber="Flat or soft units while AI carries the cycle", red="Units falling >5% YoY with rising OEM inventory",
      read="Murata and TrendForce call consumer demand subdued; TrendForce warns China/US slowdown may weaken the 2H26 peak season.", src="Murata speech [F]; TrendForce [A]", next="Apple/Android builds, Oct-Nov"),
 dict(id="SC10", name="Stocks vs fundamentals", weight=2, status="amber",
      why="MLCC stocks peaked 2-4 quarters before orders in 2000, 2007, 2010 and 2018. A big drawdown with orders still rising is the classic mid-cycle wobble, or the first warning.",
      green="Basket within 10% of its high", amber="Basket 20%+ below its high while orders still rise", red="Basket 20%+ below AND SC01 or SC04 red",
      read="Equal-weight basket 36% below its June high; Taiyo Yuden -55%, Yageo -45%, Walsin -41%, Murata -31%, SEMCO -30%, all while book-to-bill sits at records.", src="Yahoo daily closes 2 Oct 2026 [F]", next="daily"),
 dict(id="SC11", name="Murata guidance slope", weight=2, status="green",
      why="Murata reports first among the Japanese and guides conservatively; an upward revision with price still a headwind means volume is doing the work.",
      green="Full-year OP guide raised", amber="Held while orders rise", red="Cut",
      read="FY3/27 raised on 31 Jul: revenue ¥2.11tn (from 1.96), OP ¥430bn (from 380), capex ¥225bn.", src="BigGo 31 Jul 2026 [A]", next="30 Oct 2026"),
 dict(id="SC12", name="Chinese supply and pricing", weight=1, status="amber",
      why="State-backed Chinese makers flooded commodity MLCCs in 2019 and 2023; they now push into high-cap parts.",
      green="China capacity growth below 10% and no high-cap qualification at top OEMs", amber="Claimed capacity growth above 20%, or high-end qualification news", red="China discounting high-cap parts >20% vs Japanese",
      read="Fenghua claims 50bn pcs/month; Three-Circle claims 55 to 100bn by end-2026 (single source) with a ¥1.86bn high-cap project due May-2027.", src="02_capacity memo [A]", next="Quarterly"),
]
w = {"green": 0, "amber": 1, "red": 2}
tot = sum(s["weight"] for s in SC if s["status"] != "unknown")
pts = sum(w[s["status"]] * s["weight"] for s in SC if s["status"] != "unknown")
score = round(100 * pts / (2 * tot), 1)
band = ("upcycle intact" if score < 25 else "late upcycle / decelerating" if score < 50 else
        "turn underway" if score < 70 else "downturn confirmed")

bt = json.load(open("data/backtest.json"))
px = pd.read_csv("data/clean/monthly_prices.csv", index_col=0, parse_dates=True)
cons = pd.read_csv("data/clean/consensus.csv")
ind = pd.read_csv("data/cycle_indicators.csv")

def series(pat):
    d = ind[ind.indicator.str.contains(pat, regex=False)].drop_duplicates("date", keep="last")
    return [[r.date[:7], float(r.value)] for r in d.itertuples()]

stocks = []
for t, n in NAMES.items():
    c = cons[cons.ticker == t].set_index("metric")["value"]
    p = json.load(open(f"data/raw/pxd_{t}.json"))["chart"]["result"][0]
    s = pd.Series(p["indicators"]["quote"][0]["close"], index=pd.to_datetime(p["timestamp"], unit="s")).dropna()
    stocks.append(dict(t=t, name=n, short=SHORT[t], ccy=p["meta"]["currency"], last=round(float(s.iloc[-1]), 1),
        peak=round(float(s.max()), 1), peak_date=str(s.idxmax().date()), dd=round(float(s.iloc[-1] / s.max() - 1), 3),
        low52=round(float(s[-250:].min()), 1), r12=round(float(s.iloc[-1] / s.iloc[-250] - 1), 3),
        fpe=c.get("fwd_pe"), evebitda=c.get("ev_ebitda"), pb=c.get("pb"), tp=c.get("target_price"),
        spark=[round(float(v), 1) for v in s.resample("W").last().dropna().values[-78:]]))

D = dict(as_of=AS_OF, score=score, band=band, counts={k: sum(1 for s in SC if s["status"] == k) for k in ("green", "amber", "red", "unknown")},
  weights_total=tot, scorecard=SC,
  phase="Mid upcycle in fundamentals, late-cycle wobble in the stocks",
  summary=("Orders, lead times and prices all say the MLCC shortage is still building: Murata's MLCC book-to-bill hit 1.47 in Apr-Jun 2026 (2021 peak 1.32), "
           "lead times run 14-20 weeks against 8-10 normal, and SEMCO and Yageo pushed 30-50% hikes into OEM contracts. Supply cannot answer before 2H27: "
           "new high-end lines take 18-24 months and planned 4Q26 capacity slipped into 2027. The stocks disagree: after an 8x run in the equal-weight basket, "
           "they peaked 19 Jun to 1 Jul and are still 36% below the high. That gap, fundamentals rising while prices fall, has preceded both a second leg (2010, 2021) and a top (2000, 2018)."),
  flip_down=["Murata capacitor book-to-bill falls below 1.10 at the 30 Oct results, or backlog shrinks QoQ (SC01).",
             "Yageo or Walsin monthly revenue falls MoM for three months, or Yageo reports distribution above 4 months (SC04/SC06).",
             "Lead times shorten in two consecutive TrendForce bulletins (SC03).",
             "SEMCO's 2027 capex step-up is matched by Murata and the Chinese makers while price hikes stall (SC07).",
             "A top-4 hyperscaler cuts its 2027 capex framework (SC08)."],
  flip_up=["Murata, Taiyo Yuden and Kyocera join the price hikes for 1Q27; that is the leg the stocks have not priced.",
           "Murata raises FY3/27 guidance again on 30 Oct with book-to-bill above 1.3.",
           "Monthly Taiwan revenue keeps setting records through 4Q, the seasonally weak quarter."],
  backtest=bt, stocks=stocks,
  murata_bbr=series("Murata capacitor book-to-bill"), murata_bbr_total=series("Murata total book-to-bill"),
  murata_cap_backlog=series("Murata capacitor order backlog"),
)
# FY2026 Q1 MLCC ratio is quoted for MLCC (1.47), the series above is "capacitors"; Murata's MLCC = capacitors here.
if D["murata_bbr"][-1][0] != "2026-06": D["murata_bbr"].append(["2026-06", 1.47])
json.dump(D, open("data/dashboard.json", "w"), indent=1, default=lambda o: None if pd.isna(o) else float(o))
print("score", score, band, D["counts"], "bbr pts", len(D["murata_bbr"]), "backlog pts", len(D["murata_cap_backlog"]))
