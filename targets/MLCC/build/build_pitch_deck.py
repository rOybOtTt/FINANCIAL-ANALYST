"""Murata pitch deck, ~22 slides, Glilot-style approximation. Numbers are read live from the recalculated house model
(murata/6981.T_model_v1_2.10.26.xlsx via verify_model.py) and data/*.json."""
import json, subprocess, sys
from openpyxl import load_workbook
sys.path.insert(0, 'build'); from deck_kit import *

subprocess.run([sys.executable, 'build/verify_model.py', 'murata/6981.T_model_v1_2.10.26.xlsx'], check=True, capture_output=True)
wb = load_workbook('/tmp/lo/out/v.xlsx', data_only=True)
V = json.load(open('data/murata_valuation.json')); D = json.load(open('data/dashboard.json')); MB = json.load(open('data/murata_band.json'))
G = wb['Sensitivity']
yen = lambda v: f'¥{v:,.0f}'
PNG = 'build/png/'
d = Deck('Murata (6981.T) · Glilot pitch v1 · 2 Oct 2026 · not investment advice')
X, Y = Inches(.6), Inches(1.6)

# 1 title
s = d.slide('Murata: the MLCC leader, priced for a new regime', 'Best franchise in the cycle; the price already pays for a permanent re-rating')
d.tile(s, X, Inches(2.2), Inches(2.9), Inches(1.7), 'Price', yen(V['price']), '2 Oct 2026 close')
d.tile(s, Inches(3.7), Inches(2.2), Inches(2.9), Inches(1.7), 'House value (PW, PV)', yen(V['PW']['pv']), 'EV / 5-yr-mean EBITDA band', RED)
d.tile(s, Inches(6.8), Inches(2.2), Inches(2.9), Inches(1.7), 'Cycle score', f"{D['score']:.1f} / 100", 'Upcycle intact (MLCC Cycle Watch)', GOOD)
d.tile(s, Inches(9.9), Inches(2.2), Inches(2.9), Inches(1.7), 'Verdict', 'WATCH', 'Do not add; stage in below ¥6,200', AMBER)
d.text(s, 'Murata makes ~40% of the world\'s multilayer ceramic capacitors (MLCCs): the tiny parts that keep a GPU\'s power steady. AI servers need 8-15x more of them. The business is at a record; the stock trades at nearly 3x its own mid-cycle multiple.',
       X, Inches(4.4), Inches(12), Inches(1.4), 18, NAVY)

# 2 answer
s = d.slide('The answer: great cycle, wrong price for Murata itself', 'Cycle trade belongs in the laggards; Murata is the name to own after the next drawdown', 'House model; MLCC Cycle Watch')
d.card(s, X, Y, Inches(3.9), Inches(4.9), 'Cycle: still up', ['Book-to-bill 1.47, a record', 'Lead times 14-20 wks vs 8-10', 'SEMCO +30%, Yageo +50% price hikes', 'Supply can\'t answer before 2H27'], GOOD, 15)
d.card(s, Inches(4.7), Y, Inches(3.9), Inches(4.9), 'Murata: too dear', [f"EV / 5y-mean EBITDA {V['ev_mult_today']:.1f}x vs {V['band_median']:.1f}x median", f"PW value {yen(V['PW']['pv'])} vs {yen(V['price'])}", f"IRR to Mar-2030: {V['PW']['irr']:.0%}", f"Price needs a {V['rev_mult_0irr']:.0f}x exit to break even"], RED, 15)
d.card(s, Inches(8.8), Y, Inches(3.9), Inches(4.9), 'What we do', ['Watch, do not add', 'Stage in at ¥6,200 / ¥5,000 / ¥4,100', 'Only while book-to-bill > 1.0', f"20%-IRR entry {yen(V['entry20'])}", 'Cycle exposure via Taiyo Yuden / Walsin'], BLUE, 15)

# 3 ELI5
s = d.slide('ELI5: an MLCC is a tiny water tower next to the chip', 'When a GPU suddenly draws current, nearby capacitors release charge before the power supply can react', 'Murata, Samsung Electro-Mechanics product pages')
steps = [('1  Ceramic powder', 'Barium titanate, ground finer than flour. Murata makes its own.'), ('2  Thin sheets', 'Cast into sheets under 1 micron thick.'),
         ('3  Print + stack', 'Nickel electrodes printed, hundreds of layers stacked.'), ('4  Fire + finish', 'Sintered at ~1,300°C into a chip 0.4 x 0.2 mm.')]
for i, (h, b) in enumerate(steps):
    d.card(s, X + Inches(3.08 * i), Y + Inches(.2), Inches(2.9), Inches(2.3), h, b, BLUE if i != 1 else GOOD, 14)
d.text(s, ['More layers, thinner layers = more charge in the same tiny box.', 'That is the whole game, and the thinnest layers come from the best powder.'], X, Inches(4.5), Inches(12), Inches(1.2), 20, NAVY, bold=True)

# 4 three panels (3rd = visibility metric)
s = d.slide('Three numbers behind the story', 'AI multiplies the parts count; Murata holds the share; the order book says it is still building', 'TrendForce 18 May 2026; passive-components.eu; Murata 1Q FY3/27')
d.tile(s, X, Y, Inches(3.9), Inches(2.0), 'MLCCs per GB200 NVL72 rack', '~440,000', 'vs ~1,100 in a smartphone [A]')
d.tile(s, Inches(4.7), Y, Inches(3.9), Inches(2.0), 'AI-server MLCC share', '~45%', 'SEMCO ~40%; rest <15% [A]')
d.tile(s, Inches(8.8), Y, Inches(3.9), Inches(2.0), 'Visibility: capacitor backlog', '¥402bn', 'MLCC book-to-bill 1.47 [F]', GOOD)
d.image(s, PNG + 'content.png', X, Inches(3.8), h=Inches(3.0))

# 5 moat
s = d.slide('The moat: own the powder, own the thinnest layers', 'Vertical integration from dielectric powder to firing is what competitors rent', 'Murata IR; passive-components.eu; company research memo')
for i, (h, b, c) in enumerate([('THE CHOICE', 'Make the barium-titanate powder, the sheets and the equipment in-house.', NAVY),
                                ('Outcome 1: high-cap first', 'Thinnest layers reach 10µF+ in small cases first: the GPU power parts.', BLUE),
                                ('Outcome 2: share', '~40% value share; ~45% AI-server; ~50% automotive [A].', BLUE),
                                ('Outcome 3: margin', 'Components OP margin >30% in 1Q FY3/27 [F].', GOOD)]):
    d.card(s, X + Inches(3.08 * i), Y + Inches(.2), Inches(2.9), Inches(3.0), h, b, c, 15)
d.bullets(s, [('How wide:', 'wide in high-cap/auto, narrow in commodity parts. SEMCO is within 5 points in AI servers, and Chinese makers are moving up.')], X, Inches(5.2), Inches(12), Inches(1), 16)

# 6 value chain
s = d.slide('Value chain: powder in, power integrity out', 'Murata sits on the chokepoint step; distributors are where cycles break', 'Company research memo; TrendForce')
for i, (h, b, c) in enumerate([('Upstream', ['Barium titanate (in-house; Sakai ~25-28% for others)', 'Nickel / copper paste', 'Furnaces, printers (in-house)'], GREY),
                                ('Murata', ['Powder → sheet → print → stack → fire → test', 'Japan, Wuxi, Philippines, Thailand', 'Utilization ~95%'], BLUE),
                                ('Downstream', ['Distributors (~1/3 of volume)', 'AI-server ODMs (Foxconn, Quanta, Wiwynn)', 'Phones, auto Tier-1s'], NAVY)]):
    d.card(s, X + Inches(4.1 * i), Y + Inches(.2), Inches(3.9), Inches(3.4), h, b, c, 14)
d.text(s, 'THE CHOKEPOINT: high-cap, small-case MLCCs for GPU power delivery. Murata + SEMCO supply 80-85%.', X, Inches(5.5), Inches(12), Inches(.8), 18, RED, bold=True)

# 7 company overview
s = d.slide('Company: ¥2.1tn revenue, half of it capacitors', 'FY3/27 guidance raised on 31 Jul; capacitors 55% of revenue', 'Murata fact book 2026; 1Q FY3/27 results')
for i, (l, v, n) in enumerate([('FY3/27 revenue guide', '¥2.11tn', '+15% YoY'), ('FY3/27 OP guide', '¥430bn', '20.4% margin'), ('Capacitor revenue guide', '¥1.16tn', '+24% YoY'), ('Net cash (Mar-26)', '¥650bn', '+ ¥150bn buyback')]):
    d.tile(s, X + Inches(3.08 * i), Y, Inches(2.9), Inches(1.6), l, v, n)
d.image(s, PNG + 'murata_history.png', X, Inches(3.4), h=Inches(3.5))

# 8 supply
s = d.slide('Supply: two makers own the high end', 'Monthly shipments at full load are the only capacity proxy anyone publishes', 'TrendForce Jun-2026; passive-components.eu 30 Jun 2026')
d.image(s, PNG + 'capacity_share.png', X, Y, h=Inches(4.3))
d.text(s, 'Murata adds >20% MLCC capacity by Mar-2028 (~¥80bn); first output from the new building 4Q27 [A].', X, Inches(6.1), Inches(12), Inches(.5), 15, NAVY)

# 9 orders
s = d.slide('Orders: record book-to-bill, backlog 1.8x the 2021 peak', 'The ratio fell below 1 two quarters before each order trough (2019, 2022)', 'Murata fact books 2022-2026; 1Q FY3/27')
d.image(s, PNG + 'murata_orders.png', X, Y, h=Inches(4.6))

# 10 most-guided metric
s = d.slide('Guidance: operating profit raised to ¥430bn', 'The most-guided line: up ¥50bn in July while price is still a headwind', 'Murata fact books; 30 Apr and 31 Jul 2026 guidance')
h = MB['hist']; cats = [x['fy'][-7:].replace('FY3/', "FY") for x in h[-5:]] + ['FY27 Apr', 'FY27 Jul']
vals = [round(x['op'] / 1000) for x in h[-5:]] + [380, 430]
d.bar_chart(s, cats, [('Operating profit, ¥bn', vals)], X, Y, Inches(8), Inches(4.8), fmt='0', colors=[CAT[0]] * 5 + [GREY, BLUE])
d.bullets(s, ['Volume does the work: data-center sales ¥371bn (+80%)', 'Price still -¥15bn YoY: no general MLCC hike yet', 'Next read: 30 Oct, a third raise needs book-to-bill > 1.3'], Inches(8.9), Y + Inches(.4), Inches(4), Inches(4), 15)

# 11 cycle score
s = d.slide(f"Cycle: score {D['score']:.1f}, upcycle intact", 'Seven of twelve signals green, five amber, none red', 'MLCC Cycle Watch, 2 Oct 2026')
rows = [['Signal', 'Weight', 'Status', 'Reading']] + [[x['name'][:38], x['weight'], x['status'].upper(), x['read'][:70] + ('…' if len(x['read']) > 70 else '')] for x in sorted(D['scorecard'], key=lambda z: -z['weight'])]
heat = {(i, 2): (C('E0F2E7') if r[2] == 'GREEN' else C('FBF0D6')) for i, r in enumerate(rows) if i}
d.table(s, rows, X, Y, Inches(12.1), Inches(4.9), 11, [3.6, .8, 1.0, 6.7], heat=heat)

# 12 history
s = d.slide('Twenty-six years of MLCC booms and busts', 'Stocks peaked 2-4 quarters before orders every time; shortages lasted 10-14 months', 'Yahoo adjusted closes; basket = Murata, SEMCO, Taiyo Yuden, Yageo, Walsin')
d.image(s, PNG + 'basket_history.png', X, Y, h=Inches(4.7))

# 13 backtest
ep = [e for e in D['backtest']['entry_minus35_basket'] if e.get('entry')]
s = d.slide('Buying 35% off the peak paid over two years', f"Positive at 24 months in {sum(e['fwd24'] > 0 for e in ep)} of {len(ep)} cycles; a coin toss at 12 months", 'Equal-weight basket, local currency; first month >=35% below cycle peak')
d.image(s, PNG + 'backtest.png', X, Y, w=Inches(8.4))
d.bullets(s, ['Today: basket -36%, Murata only -31%', 'Worst case: 2007, -43% more first', 'Murata alone works in pauses, not busts'], Inches(9.2), Y + Inches(.3), Inches(3.6), Inches(4), 15)

# 14 PxQ / price actions
s = d.slide('PxQ: everyone is raising prices except the Japanese', 'Murata\'s price impact is still -¥15bn YoY: the one leg the stocks have not priced', 'TrendForce Aug 2026; passive-components.eu; Murata 1Q speech')
d.table(s, [['Maker', 'Price action 2026', 'Effective', 'Tag'], ['Yageo', '+50% list, extended to direct customers', '1 Jul', 'A'], ['SEMCO', '+30% all MLCC; OEM hike in 4Q', '1 Aug', 'A'],
            ['Taiyo Yuden', '+10-30% auto, +6-13% consumer; second round', 'Apr / 1 Sep', 'A'], ['Walsin', '+5-15% consumer MLCC', 'Jun-Jul', 'A'],
            ['Murata', 'Net price still negative (-¥15bn YoY); 15-35% on AI/auto grades reported', 'Apr (unconfirmed)', 'F / A'], ['Kyocera', 'No 4Q change ("wait and see")', '—', 'A']],
        X, Y, Inches(12.1), Inches(3.6), 13, [2.0, 6.6, 2.0, 1.5])
d.text(s, 'Sensitivity: every +5% on Murata capacitor price ≈ +¥45-50bn EBITDA (≈ +8% on FY3/27).', X, Inches(5.6), Inches(12), Inches(.6), 17, NAVY, bold=True)

# 15 band
s = d.slide('Valuation: 31x mid-cycle EBITDA vs an 11.6x history', 'House method: EV / 5-yr-mean EBITDA on the own band; P/B as the timing check', 'Murata fact books; Yahoo; house model')
d.image(s, PNG + 'murata_band.png', X, Y, w=Inches(8.6))
d.bullets(s, [f"Band p25 / median / p75: {MB['band']['all']['p25']} / {MB['band']['all']['p50']} / {MB['band']['all']['p75']}x", f"P/B {V['pb_vs_median']:.0%} above its own median", 'Trailing P/E 66x vs 23x median'], Inches(9.4), Y + Inches(.3), Inches(3.5), Inches(4), 14)

# 16 sensitivity grids (ruling T6-03: slide 16)
s = d.slide('Sensitivity: price and volume barely move the answer', 'Value per share at exit (¥). Left: annual MLCC price x volume. Right: exit multiple x mean EBITDA', 'House model, Sensitivity sheet (live formulas)')
g1 = [['vol \\ price'] + [f'{G.cell(5, c).value:+.0%}' for c in range(2, 9)]]
for r in range(6, 12): g1.append([f'{G.cell(r, 1).value:+.0%}'] + [f'{G.cell(r, c).value:,.0f}' for c in range(2, 9)])
d.table(s, g1, X, Y, Inches(6.3), Inches(3.2), 11)
g2 = [['x \\ ¥bn'] + [str(G.cell(16, c).value) for c in range(2, 9)]]
for r in range(17, 25): g2.append([f'{G.cell(r, 1).value:g}x'] + [f'{G.cell(r, c).value:,.0f}' for c in range(2, 9)])
heat = {(i, j): C('FBE3E1') for i in range(1, 9) for j in range(1, 8) if float(g2[i][j].replace(',', '')) < V['price']}
d.table(s, g2, Inches(7.1), Y, Inches(5.7), Inches(3.9), 11, heat=heat)
d.text(s, f"Even +20% volume and +10% price a year for three years reach only ~¥{G.cell(11, 8).value:,.0f} on the own band. Today's ¥{V['price']:,} needs ~{V['rev_mult_0irr']:.0f}x. The multiple is the debate, not the cycle.", X, Inches(5.6), Inches(12.2), Inches(1), 16, NAVY, bold=True)

# 17 scenarios
s = d.slide('Scenarios to March 2030', 'Exit on the own band; FY3/27 = company guidance; 25/50/25 weights', 'House model, Scenarios sheet')
rows = [['', 'Bear', 'Base', 'Bull', 'Prob-weighted'],
        ['Capacitor volume FY28/29/30', '+5 / -8 / +2%', '+15 / +8 / -2%', '+20 / +12 / +5%', ''],
        ['Capacitor price FY28/29/30', '-3 / -10 / -3%', '+3 / +1 / -5%', '+10 / +3 / -2%', ''],
        ['FY3/30 EBITDA (¥bn)'] + [f"{V[k]['ebitda30'] / 1000:,.0f}" for k in ('Bear', 'Base', 'Bull', 'PW')],
        ['Exit multiple'] + [f"{V[k]['mult']:.1f}x" for k in ('Bear', 'Base', 'Bull')] + [''],
        ['Value per share at exit'] + [yen(V[k]['vps']) for k in ('Bear', 'Base', 'Bull', 'PW')],
        ['PV per share (8% CoE)'] + [yen(V[k]['pv']) for k in ('Bear', 'Base', 'Bull', 'PW')],
        ['IRR from ¥8,467'] + [f"{V[k]['irr']:.0%}" for k in ('Bear', 'Base', 'Bull', 'PW')],
        ['Entry for 20% IRR'] + [yen(V[k]['entry']) for k in ('Bear', 'Base', 'Bull', 'PW')]]
d.table(s, rows, X, Y, Inches(12.1), Inches(4.4), 14, [3.6, 2.1, 2.1, 2.1, 2.2])

# 18 ladder
s = d.slide('Value ladder: half the price on the house method', f"PW present value {yen(V['PW']['pv'])}; staged entry ¥6,200 / ¥5,000 / ¥4,100", 'House model; stockanalysis.com consensus')
d.image(s, PNG + 'murata_ladder.png', X, Y, h=Inches(4.2))
d.text(s, 'Steelman: if the trough margin has moved up for good, a 15-16x band gives ¥6,200-6,600 at exit. Still below the price.', X, Inches(6.0), Inches(12), Inches(.6), 15, INK2, italic=True)

# 19 competition
s = d.slide('Competition: who can take the high-end work', 'Ranked by threat to Murata in AI-server and automotive MLCC', 'Company memos; stockanalysis.com; Yahoo')
d.card(s, X, Y, Inches(3.9), Inches(3.4), 'High: SEMCO', ['~40% AI-server share', '+30% price, ₩3.3tn LTAs', 'Capex doubling in 2027', 'Fwd P/E 47.6x'], RED, 14)
d.card(s, Inches(4.7), Y, Inches(3.9), Inches(3.4), 'Medium: China makers', ['Fenghua, Three-Circle', 'Claims 50 and 55→100bn pcs/mo', 'High-cap project May-2027', 'Commodity first, then up'], AMBER, 14)
d.card(s, Inches(8.8), Y, Inches(3.9), Inches(3.4), 'Low: the rest', ['Taiyo Yuden, TDK, Yageo, Kyocera', 'AI-server share <5% each', 'Strong in niches (Taiyo high-cap, Yageo commodity)', 'TDK-Taiyo alliance is the one to watch'], GOOD, 14)

# 20 catalysts
s = d.slide('Catalysts: the 30 October call decides the next leg', 'Dates marked est. inferred from last year', 'Company IR calendars; investing.com')
d.table(s, [['Date', 'Event', 'What to read']] + [['~8-9 Oct', 'Yageo / Walsin Sep revenue', 'Industry volume and price'], ['27 Oct', 'Yageo 3Q', 'Distribution inventory months'],
            ['~29-30 Oct', 'SEMCO 3Q', 'Capex 2027, LTA pricing'], ['30 Oct', 'Murata 2Q FY3/27', 'Book-to-bill, price stance, third guide raise'],
            ['Nov-Dec', 'Japanese 1Q27 price decisions', 'The un-priced leg'], ['~2-5 Feb', 'Murata 3Q', 'Distributor orders, inventory']], X, Y, Inches(12.1), Inches(3.8), 14, [2.0, 4.3, 5.8])

# 21 risks
s = d.slide('What would make us wrong', 'And what we could not verify', 'Research memos 01-06')
d.card(s, X, Y, Inches(6.0), Inches(4.6), 'Ways to be wrong', ['Regime change: AI parts become contracted, trough margins up → 15-20x is the new band',
       'Japanese price leg lifts FY3/28 EBITDA toward ¥1tn', 'Whole cohort re-rates as "AI picks and shovels", like memory in 2025-26'], RED, 14)
d.card(s, Inches(6.8), Y, Inches(5.9), Inches(4.6), 'Open gaps', ['Murata MLCC price letter unconfirmed', 'No named-customer shares', 'Capacitor EBITDA not disclosed (model derives ~42%)',
       'Sell-side reports (G: drive) not yet included', 'Capacity is a shipment proxy'], GREY, 14)

# 22 philosophy
s = d.slide('Investment philosophy', 'How we own a cyclical with a great franchise')
d.text(s, ['Own the cycle where it is cheap, own the franchise where the price is right.',
           'MLCC demand has two more quarters of momentum and no supply answer before 2H27, so the trade sits in the laggards that fell 40-55%.',
           'Murata is the name we want through the next downturn: it falls least and recovers first. We buy it in stages when the price meets the band, not when the headlines peak.'],
       X, Inches(1.9), Inches(11.5), Inches(4.5), 22, NAVY)

print(d.save('murata/6981.T_pitch_deck_v1_2.10.26.pptx'), d.n, 'slides')
