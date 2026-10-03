"""Competitive deck: the seven MLCC makers side by side (python-pptx, native tables/charts where possible)."""
import json, sys
sys.path.insert(0, 'build'); from deck_kit import *
D = json.load(open('data/dashboard.json')); V = json.load(open('data/murata_valuation.json'))
PNG = 'build/png/'; X, Y = Inches(.6), Inches(1.6)
d = Deck('MLCC competitive deck v1 · 2 Oct 2026 · not investment advice')
ST = {s['t']: s for s in D['stocks']}
EVM = {'6981.T': 32.0, '009150.KS': 64.7, '6976.T': 22.1, '6762.T': 13.6, '2327.TW': 33.7, '6971.T': 15.3, '2492.TW': 20.2}  # EV / 4-5y mean EBITDA, build notes

s = d.slide('The MLCC field: seven makers, one cycle', 'Who wins the AI-server shortage, who rides it, and who only looks like an MLCC stock')
for i, (l, v, n, c) in enumerate([('Cycle score', f"{D['score']:.1f}", 'Upcycle intact', GOOD), ('Basket vs high', '-36%', 'Peaked 19 Jun-1 Jul 2026', RED),
                                    ('AI-server share, top 2', '~85%', 'Murata + SEMCO [A]', NAVY), ('Lead times', '14-20 wks', 'vs 8-10 normal [A]', AMBER)]):
    d.tile(s, X + Inches(3.08 * i), Inches(2.2), Inches(2.9), Inches(1.7), l, v, n, c)
d.text(s, 'The big bet: the shortage runs into 2027, but most of the good news is in Murata and SEMCO prices. The cycle trade sits in the laggards; Murata is the name to buy on the next drawdown.', X, Inches(4.4), Inches(12), Inches(1.4), 18, NAVY)

s = d.slide('Market map: two leaders, a pack, and China', 'Value share and AI-server share; output at full load', 'TrendForce Jun-2026; passive-components.eu 30 Jun 2026 [A]')
d.image(s, PNG + 'capacity_share.png', X, Y, h=Inches(4.6))

s = d.slide('Positioning: AI exposure vs MLCC purity', 'Top-right = AI leaders. Top-left = cycle levers. Bottom = not really MLCC stocks', 'passive-components.eu [A]; company filings; stockanalysis.com')
d.image(s, PNG + 'twobytwo.png', X, Y, h=Inches(5.1))
d.bullets(s, [('AI leaders:', 'Murata, SEMCO. Pricing power, priced for it.'), ('Cycle levers:', 'Taiyo Yuden, Yageo, Walsin. Highest beta to MLCC prices.'), ('Diversified:', 'TDK (batteries), Kyocera (packaging, KDDI).')], Inches(9.6), Y + Inches(.4), Inches(3.4), Inches(4.5), 14)

rows = [['', 'Murata', 'SEMCO', 'Taiyo Yuden', 'Yageo', 'Walsin', 'TDK', 'Kyocera'],
        ['MLCC % of revenue', '~55%', '~46%*', '69%', '~45%', '46%', '~10%', '<5%'],
        ['AI-server share', '~45%', '~40%', '<4%', '~3%', '~1%', '<5%', '~1%'],
        ['Book-to-bill', '1.47', '1.31', '1.72', '2.2', '>1.8', '—', '—'],
        ['Utilization', '~95%', '91%', '~85%', '80-85%', '80-85%', '—', '—'],
        ['2026 price action', 'none (−¥15bn)', '+30%', '+6-30%', '+50% list', '+5-15%', '—', 'none'],
        ['Fwd P/E', *[f"{ST[t]['fpe']:.1f}x" for t in ('6981.T', '009150.KS', '6976.T', '2327.TW', '2492.TW', '6762.T', '6971.T')]],
        ['EV / mean EBITDA', *[f"{EVM[t]:.0f}x" for t in ('6981.T', '009150.KS', '6976.T', '2327.TW', '2492.TW', '6762.T', '6971.T')]],
        ['From 2026 high', *[f"{ST[t]['dd']:.0%}" for t in ('6981.T', '009150.KS', '6976.T', '2327.TW', '2492.TW', '6762.T', '6971.T')]]]
g, a, r = C('E0F2E7'), C('FBF0D6'), C('F9E2E1')
heat = {}
for j, v in enumerate(rows[7][1:], 1): heat[(7, j)] = g if float(v[:-1]) < 22 else a if float(v[:-1]) < 35 else r
for j, v in enumerate(rows[3][1:], 1): heat[(3, j)] = g if v not in ('—',) else WHITE
for j, v in enumerate(rows[8][1:], 1): heat[(8, j)] = r if float(v[:-1]) < -35 else a if float(v[:-1]) < -20 else g
s = d.slide('Comparison matrix: who has what', 'Green = better for the long case; red = stretched or exposed', 'Company memos [F/A]; stockanalysis.com; Yahoo; *SEMCO = Component Solutions incl. inductors')
d.table(s, rows, X, Y, Inches(12.1), Inches(4.6), 13, [2.3, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4, 1.4], heat=heat)

s = d.slide('Capacity: who can add, and when it lands', 'High-end lines take 18-24 months; most 2026 decisions arrive 2H27-2028', 'Capacity memo 02 [A]')
d.table(s, [['Maker', 'Output / utilization', 'Expansion', 'Lands'],
            ['Murata', '140bn pcs/mo; ~95%', '+¥80bn equipment, >20% capacity; new Izumo building', '4Q27-2028'],
            ['SEMCO', '98bn pcs/mo; 91%', 'Philippines plant 3; capex ₩3tn → ₩6tn', '1Q27 on'],
            ['Taiyo Yuden', '40bn pcs/mo; ~85%', 'Malaysia pulled forward; +10-15%/yr; capex ¥42bn', '2027'],
            ['Yageo', 'n/d; 80-85% → >90%', 'Kaohsiung, Vietnam, Suzhou, Mexico', 'ongoing'],
            ['Walsin', 'n/d; 80-85%', '+10-15% 2026, +10% 2027', '2026-27'],
            ['Fenghua / Three-Circle', '50 / 55→100bn (claims)', 'High-cap project RMB1.86bn', 'May-2027']], X, Y, Inches(12.1), Inches(4.2), 13, [2.4, 2.6, 5.1, 2.0])

s = d.slide('Demand: AI servers and EVs carry the increment', 'MLCCs per device, log scale', 'TrendForce 18 May 2026; passive-components.eu; Mordor [A]')
d.image(s, PNG + 'content.png', X, Y, h=Inches(4.6))

s = d.slide('Stocks: the pure plays fell hardest', 'Distance from the 2026 high and forward P/E', 'Yahoo; stockanalysis.com, 2 Oct 2026')
d.image(s, PNG + 'peers.png', X, Y, h=Inches(4.6))

s = d.slide('Valuation: EV over cycle-average EBITDA', 'Same method as the house model; 4-5 years of history for peers, so read as relative', 'Yahoo fundamentals; stockanalysis.com; house model for Murata')
o = sorted(EVM.items(), key=lambda k: k[1])
d.bar_chart(s, [ST[t]['short'] for t, _ in o], [('EV / mean EBITDA (x)', [v for _, v in o])], X, Y, Inches(8.4), Inches(4.8), horizontal=True, fmt='0.0',
            colors=[RED if v > 35 else AMBER if v > 22 else GOOD for _, v in o])
d.bullets(s, [f"Murata own band: {V['band_median']:.1f}x median", 'SEMCO ~65x is the outlier', 'TDK / Kyocera cheap but not MLCC plays', 'Walsin and Taiyo Yuden: cheapest MLCC levers'], Inches(9.2), Y + Inches(.3), Inches(3.7), Inches(4), 14)

s = d.slide('History: buying the basket 35% off the peak', 'Positive at 24 months in every completed cycle since 2000', 'Equal-weight basket, local currency')
d.image(s, PNG + 'backtest.png', X, Y, h=Inches(4.6))

s = d.slide('Ranked shortlist', 'Verdict per name from the one-page screens', 'Screens in targets/MLCC/peers and murata')
v = [['Rank', 'Name', 'Verdict', 'Why', 'Action'],
     ['1', 'Walsin (2492.TW)', 'WORTH A LOOK', 'Cheapest MLCC lever: 21.7x fwd, revenue +45%', 'Long tactical; exit on 3 MoM declines'],
     ['2', 'Taiyo Yuden (6976.T)', 'WORTH A LOOK', 'Book-to-bill 1.72, -55% from high', 'Long tactical, small size'],
     ['3', 'Murata (6981.T)', 'WATCH', f"Best franchise, {V['ev_mult_today']:.0f}x vs {V['band_median']:.0f}x band", 'Stage in ¥6,200 / ¥5,000 / ¥4,100'],
     ['4', 'Yageo (2327.TW)', 'WATCH', '2018 analog: hikes and double-order risk', 'Decide after 27 Oct inventory read'],
     ['5', 'SEMCO (009150.KS)', 'PASS', '~65x mean EBITDA; capex doubling', 'Short candidate on a turn'],
     ['6', 'TDK (6762.T)', 'PASS', 'Battery story, not MLCC', 'Out of scope'],
     ['7', 'Kyocera (6971.T)', 'PASS', 'Packaging/KDDI story', 'Out of scope']]
hv = {(i, 2): (C('E0F2E7') if v[i][2] == 'WORTH A LOOK' else C('FBF0D6') if v[i][2] == 'WATCH' else C('F9E2E1')) for i in range(1, 8)}
d.table(s, v, X, Y, Inches(12.1), Inches(4.4), 13, [.7, 2.5, 1.7, 4.0, 3.2], heat=hv)

s = d.slide('The big bet and what kills it', 'One trade, one wait, one avoid', 'This deck')
d.card(s, X, Y, Inches(3.9), Inches(3.6), 'Trade', ['Long Walsin + Taiyo Yuden', 'Into the Japanese 1Q27 price leg', 'Exit: Taiwan monthly revenue down 3 months'], GOOD, 15)
d.card(s, Inches(4.7), Y, Inches(3.9), Inches(3.6), 'Wait', ['Murata on staged entry', 'Below ¥6,200 with book-to-bill > 1.0', 'Best name through the bust'], AMBER, 15)
d.card(s, Inches(8.8), Y, Inches(3.9), Inches(3.6), 'Avoid', ['SEMCO at ~65x mean EBITDA', 'Capex doubling into 2027', 'Short on SC01/SC04 turning red'], RED, 15)
d.text(s, 'What kills it: distributor double-ordering (Yageo channel months, 27 Oct) or a hyperscaler 2027 capex cut.', X, Inches(5.5), Inches(12), Inches(.7), 16, NAVY, bold=True)

s = d.slide('Sources and gaps', 'Tags: F = company document; A = attributed; E = estimate')
d.bullets(s, ['Company: Murata fact books 2022-2026 and 1Q FY3/27; Taiyo Yuden 1Q FY3/27 deck [F]', 'Market: TrendForce (May-Aug 2026), passive-components.eu, cnyes, BigGo summaries [A]',
              'Prices: Yahoo Finance; consensus: stockanalysis.com, 2 Oct 2026', 'Gaps: no primary capacity data; Paumanok/TrendForce price tables paywalled; peer history 4 years only; sell-side reports not yet included'],
          X, Y, Inches(12), Inches(4.5), 15)
print(d.save('MLCC_competitive_deck_v1_2.10.26.pptx'), d.n, 'slides')
