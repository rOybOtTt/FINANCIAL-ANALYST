"""Static PNG charts for the decks and PDFs (deck palette from DECK_BLUEPRINT.md)."""
import json, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
NAVY, BLUE, GREY = '#1F2D5A', '#1B6CB5', '#8A94A6'
CAT = ['#5B9BD5', '#F2B6A0', '#A8C97F', '#F2B23E', '#C9C2E0', '#3FA39B', '#1B6CB5']
GOOD, AMBER, RED = '#2E7D32', '#E69500', '#C0392B'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': '#C9D1DC', 'axes.labelcolor': NAVY,
                     'xtick.color': '#4A5568', 'ytick.color': '#4A5568', 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#E6EAF0', 'grid.linewidth': .8, 'axes.titleweight': 'bold', 'axes.titlecolor': NAVY,
                     'axes.titlesize': 13, 'axes.titlelocation': 'left', 'savefig.dpi': 200, 'savefig.bbox': 'tight', 'figure.facecolor': 'white'})
OUT = 'build/png/'
import os; os.makedirs(OUT, exist_ok=True)
pctf = FuncFormatter(lambda v, _: f'{v:.0%}')
D = json.load(open('data/dashboard.json')); BT = D['backtest']; MB = json.load(open('data/murata_band.json'))

def save(fig, name, src):
    fig.text(0.0, -0.02, src, fontsize=8, style='italic', color=GREY, transform=fig.transFigure)
    fig.savefig(OUT + name); plt.close(fig)

# 1 basket history
s = pd.Series(BT['basket_core']); s.index = pd.to_datetime(s.index)
fig, ax = plt.subplots(figsize=(10, 4.2)); ax.plot(s.index, s.values, color=BLUE, lw=1.8); ax.set_yscale('log')
ax.fill_between(s.index, s.values, s.min() * .9, color=BLUE, alpha=.08)
for p in BT['peaks']:
    t = pd.Timestamp(p)
    if t in s.index: ax.scatter(t, s[t], color=RED, s=28, zorder=3); ax.annotate(t.strftime('%Y'), (t, s[t]), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=8, color=RED)
ax.set_title('Equal-weight MLCC basket, 2000-2026 (log scale)'); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
save(fig, 'basket_history.png', 'Murata, SEMCO, Taiyo Yuden, Yageo, Walsin; Yahoo adjusted closes, local currency, 2 Oct 2026')

# 2 backtest
ep = [e for e in BT['entry_minus35_basket'] if e.get('entry')]
lab = [e['peak'][:4] for e in ep]; x = np.arange(len(ep)); w = .26
fig, ax = plt.subplots(figsize=(10, 4.2))
for i, (k, c, n) in enumerate([('fwd12', CAT[3], '12 months'), ('fwd24', BLUE, '24 months'), ('fwd36', CAT[5], '36 months')]):
    ax.bar(x + (i - 1) * w, [e[k] or 0 for e in ep], w, color=c, label=n)
ax.axhline(0, color=NAVY, lw=.8); ax.set_xticks(x, [f'{l} cycle' for l in lab]); ax.yaxis.set_major_formatter(pctf); ax.legend(frameon=False, ncol=3, loc='upper left')
ax.set_title('Return after buying the basket 35% below its cycle peak')
save(fig, 'backtest.png', 'First month the basket closed >=35% below its cycle peak; equal-weight, local currency')

# 3 Murata book-to-bill + backlog
b = D['murata_bbr']; bl = D['murata_cap_backlog']
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ax[0].plot([p[0] for p in b], [p[1] for p in b], color=BLUE, lw=2, marker='o', ms=3); ax[0].axhline(1, color=GREY, ls='--', lw=1)
ax[0].set_title('Murata capacitor book-to-bill'); ax[0].tick_params(axis='x', rotation=60, labelsize=8)
ax[0].set_xticks(range(0, len(b), 3), [b[i][0] for i in range(0, len(b), 3)])
ax[1].bar([p[0] for p in bl], [p[1] for p in bl], color=[BLUE if i == len(bl) - 1 else CAT[0] for i in range(len(bl))])
ax[1].set_title('Capacitor order backlog, JPY bn'); ax[1].tick_params(axis='x', rotation=60, labelsize=8)
ax[1].set_xticks(range(0, len(bl), 3), [bl[i][0] for i in range(0, len(bl), 3)])
save(fig, 'murata_orders.png', 'Murata fact books 2022-2026; 1Q FY3/27 results (31 Jul 2026)')

# 4 capacity + share
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
L = ['Murata', 'SEMCO', 'Three-Circle*', 'Fenghua*', 'Taiyo Yuden']; V = [140, 98, 55, 50, 40]
ax[0].barh(L[::-1], V[::-1], color=[CAT[2], GREY, GREY, CAT[1], BLUE]); ax[0].set_title('MLCC output, bn pcs / month'); ax[0].set_xlim(0, 165)
for i, v in enumerate(V[::-1]): ax[0].text(v + 2, i, str(v), va='center', fontsize=9, color=NAVY)
L2 = ['Murata', 'SEMCO', 'TDK', 'Taiyo Yuden', 'Yageo', 'Kyocera AVX']; v1 = [40, 18, 12, 10, 10, 5]; v2 = [45, 40, 5, 4, 3, 0]
y = np.arange(len(L2)); ax[1].barh(y + .2, v1[::-1] if False else v1, .4, color=BLUE, label='Value share'); ax[1].barh(y - .2, v2, .4, color=CAT[1], label='AI-server share')
ax[1].set_yticks(y, L2); ax[1].invert_yaxis(); ax[1].legend(frameon=False, loc='lower right'); ax[1].set_title('Share of MLCC value vs AI-server, %')
save(fig, 'capacity_share.png', 'TrendForce Jun-2026 shipments (*company claims); passive-components.eu 30 Jun 2026 (attributed)')

# 5 content per device
L = ['Smartphone', 'Enterprise server', 'ICE car', 'GB200 board', 'Electric car', '8-GPU AI server', 'GB200 NVL72 rack']; V = [1100, 2500, 3000, 6500, 14000, 20000, 440000]
fig, ax = plt.subplots(figsize=(10, 3.8)); ax.barh(L[::-1], V[::-1], color=[BLUE, BLUE, CAT[2], BLUE, GREY, GREY, GREY]); ax.set_xscale('log')
for i, v in enumerate(V[::-1]): ax.text(v * 1.08, i, f'{v:,}', va='center', fontsize=9, color=NAVY)
ax.set_title('MLCCs per device (log scale)'); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:,.0f}'))
save(fig, 'content.png', 'passive-components.eu, TrendForce 18 May 2026, Mordor (attributed); ranges at midpoint')

# 6 Murata band
bs = pd.DataFrame(MB['band_series']); bs['month'] = pd.to_datetime(bs.month)
bd = MB['band']['all']
fig, ax = plt.subplots(figsize=(10, 3.8)); ax.plot(bs.month, bs.mult, color=BLUE, lw=1.8)
for k, c, n in (('p25', GOOD, 'p25'), ('p50', NAVY, 'median'), ('p75', RED, 'p75')):
    ax.axhline(bd[k], color=c, ls='--', lw=1); ax.text(bs.month.iloc[0], bd[k] + .4, f'{n} {bd[k]:.1f}x', color=c, fontsize=8)
ax.scatter(bs.month.iloc[-1], bs.mult.iloc[-1], color=RED, zorder=3); ax.annotate(f'today {bs.mult.iloc[-1]:.1f}x', (bs.month.iloc[-1], bs.mult.iloc[-1]), xytext=(-70, 0), textcoords='offset points', color=RED, fontsize=9)
ax.set_title('Murata EV / 5-yr-mean EBITDA, own band')
save(fig, 'murata_band.png', 'Monthly close x shares ex-treasury less net cash, over trailing 5-FY mean EBITDA; Murata fact books, Yahoo')

# 7 Murata history: capacitor vs other revenue + OP margin small panel
h = pd.DataFrame(MB['hist']); fy = [f[-4:] for f in h.fy]
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={'width_ratios': [1.6, 1]})
ax[0].bar(fy, h.cap / 1e3, color=BLUE, label='Capacitors'); ax[0].bar(fy, (h.rev - h.cap) / 1e3, bottom=h.cap / 1e3, color=CAT[0], label='Everything else')
ax[0].set_title('Murata revenue, JPY bn (FYE March)'); ax[0].legend(frameon=False); ax[0].tick_params(axis='x', rotation=60, labelsize=8)
ax[1].plot(fy, h.op_m, color=NAVY, marker='o', ms=3, label='Operating margin'); ax[1].plot(fy, h.ebitda_m, color=CAT[3], marker='o', ms=3, label='EBITDA margin')
ax[1].yaxis.set_major_formatter(pctf); ax[1].set_title('Margins'); ax[1].legend(frameon=False, fontsize=8); ax[1].tick_params(axis='x', rotation=60, labelsize=8)
save(fig, 'murata_history.png', 'Murata fact books 2022 and 2026; capacitor sales product basis to FY3/21, segment basis after')

# 8 peers drawdown + fwd PE
st = D['stocks']
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={'wspace': .45})
o = sorted(st, key=lambda s: s['dd']); ax[0].barh([s['short'] for s in o], [s['dd'] for s in o], color=[RED if s['dd'] < -.35 else AMBER if s['dd'] < -.2 else GOOD for s in o])
ax[0].xaxis.set_major_formatter(pctf); ax[0].set_title('Distance from 2026 high')
o = sorted(st, key=lambda s: s['fpe'] or 0); ax[1].barh([s['short'] for s in o], [s['fpe'] or 0 for s in o], color=[BLUE if s['short'] == 'Murata' else CAT[0] for s in o])
ax[1].set_title('Forward P/E (x)')
for i, s in enumerate(o): ax[1].text((s['fpe'] or 0) + .5, i, f"{s['fpe']:.1f}", va='center', fontsize=9, color=NAVY)
save(fig, 'peers.png', 'Yahoo daily closes; stockanalysis.com consensus, 2 Oct 2026')

# 9 Murata scenario ladder
sc = json.load(open('data/murata_valuation.json'))
fig, ax = plt.subplots(figsize=(10, 3.4))
items = [('Bear', sc['Bear']['pv'], RED), ('PW value', sc['PW']['pv'], NAVY), ('Base', sc['Base']['pv'], BLUE), ('Bull', sc['Bull']['pv'], GOOD), ('Consensus TP', 10414, GREY), ('Price', 8467, AMBER)]
ax.barh([i[0] for i in items][::-1], [i[1] for i in items][::-1], color=[i[2] for i in items][::-1])
for j, (n, v, c) in enumerate(items[::-1]): ax.text(v + 80, j, f'¥{v:,.0f}', va='center', fontsize=9, color=NAVY)
ax.axvline(sc['entry20'], color=RED, ls='--', lw=1); ax.text(sc['entry20'] + 60, 5.3, f"20%-IRR entry ¥{sc['entry20']:,.0f}", color=RED, fontsize=8)
ax.grid(axis='y', visible=False); ax.set_title('Murata value per share today (PV at 8% cost of equity), JPY')
save(fig, 'murata_ladder.png', 'House model 6981.T_model_v1_2.10.26.xlsx; EV / 5-yr-mean EBITDA own band exit at Mar-2030')
print('charts ok')

# 10 2x2 positioning: x = AI-server MLCC share, y = MLCC/capacitor share of revenue, bubble = market cap (USD bn, approx)
P = [('Murata', 45, 55, 103), ('SEMCO', 40, 46, 83), ('Taiyo Yuden', 4, 69, 9), ('TDK', 5, 10, 40), ('Yageo', 3, 45, 42), ('Kyocera', 1, 5, 32), ('Walsin', 1, 46, 6)]  # USD bn at JPY150, KRW1400, TWD31
fig, ax = plt.subplots(figsize=(9, 5.2))
for i, (n, x, y, m) in enumerate(P):
    ax.scatter(x, y, s=m * 18, color=CAT[i], alpha=.85, edgecolor='white', lw=2, zorder=3)
    off = {'Walsin': (-48, -14), 'Yageo': (12, 4)}.get(n, (10, 6))
    ax.annotate(n, (x, y), xytext=off, textcoords='offset points', fontsize=11, color=NAVY, weight='bold')
ax.axvline(20, color=GREY, ls='--', lw=1); ax.axhline(30, color=GREY, ls='--', lw=1)
ax.set_xlim(-3, 55); ax.set_ylim(0, 80); ax.set_xlabel('AI-server MLCC share, %'); ax.set_ylabel('MLCC / capacitors, % of revenue')
for (tx, ty, t) in ((40, 76, 'AI leaders'), (1, 76, 'Cycle levers'), (40, 3, '(empty)'), (1, 3, 'Diversified')):
    ax.text(tx, ty, t, fontsize=10, color=GREY, style='italic')
ax.set_title('Positioning: AI exposure vs MLCC purity (bubble = market cap)')
save(fig, 'twobytwo.png', 'Shares: passive-components.eu 30 Jun 2026 [A]; revenue mix: company filings; market caps stockanalysis.com 2 Oct 2026, USD at ¥150, ₩1,400, NT$31.')
print('2x2 ok')
