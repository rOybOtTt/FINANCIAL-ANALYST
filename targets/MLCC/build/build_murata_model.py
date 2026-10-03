"""Builds 6981.T_model_v1_2.10.26.xlsx: the house model for Murata, valued with EV / 5-yr-mean EBITDA own band
(Roy's ruling, 2 Oct 2026: MLCC uses the memory card D-M1 logic, no regime credit; P/B is a timing check).
Every forecast and valuation cell is a live formula off the Inputs sheet."""
import json, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import ColorScaleRule

band = json.load(open('data/murata_band.json'))
hist = pd.DataFrame(band['hist'])
OUT = 'murata/6981.T_model_v1_2.10.26.xlsx'

NAVY = '1F2D5A'; BLUE = '1B6CB5'; INPUT = 'FFF4CC'; GREY = 'F2F4F7'
hdr = Font(bold=True, color='FFFFFF'); hfill = PatternFill('solid', fgColor=NAVY)
inp = PatternFill('solid', fgColor=INPUT); sub = PatternFill('solid', fgColor=GREY)
thin = Border(bottom=Side(style='thin', color='C9D1DC'))
wb = Workbook()

def head(ws, r, vals, c0=1):
    for i, v in enumerate(vals):
        c = ws.cell(r, c0 + i, v); c.font = hdr; c.fill = hfill; c.alignment = Alignment(horizontal='center', wrap_text=True)

def title(ws, t, s):
    ws['A1'] = t; ws['A1'].font = Font(bold=True, size=16, color=NAVY)
    ws['A2'] = s; ws['A2'].font = Font(italic=True, color='687386')

# ---------------- Inputs ----------------
I = wb.active; I.title = 'Inputs'
title(I, 'Murata Manufacturing (6981.T): inputs', 'Yellow = input. JPY mn unless stated. Price 2 Oct 2026 close. Sources on the Sources sheet.')
rows = [
 ('Share price (JPY)', 8467, 'Yahoo 2-Oct-2026'),
 ('Shares outstanding ex-treasury (mn)', 1820.292, 'Fact book 2026, FY3/26 split-adjusted'),
 ('Net cash FY3/26', 650441, 'Cash 653.7bn less debt 3.3bn, fact book 2026'),
 ('FY3/27 operating profit guide', 430000, 'Murata 31-Jul-2026 revision'),
 ('FY3/27 D&A guide', 178000, 'April guide, not revised'),
 ('FY3/27 capacitor revenue guide', 1157500, '31-Jul-2026 revision'),
 ('FY3/27 total revenue guide', 2110000, '31-Jul-2026 revision'),
 ('Other-business EBITDA margin', 0.13, 'Derived: FY3/26 EBITDA less capacitors at ~38% [E]'),
 ('Drop-through of price on capacitor EBITDA', 0.90, 'Assumption: price changes fall almost fully to EBITDA [A]'),
 ('Tax + minorities on (EBITDA - D&A)', 0.23, 'FY3/26 net income / OP ≈ 0.83, less finance income [E]'),
 ('Cost of equity (CAPM)', 0.08, 'JGB 10y ~1.6% + 1.0 beta x 6.5% ERP [A]'),
 ('Years to exit (to Mar-2030)', 3.5, 'Oct-2026 to end FY3/30'),
 ('Target IRR for entry', 0.20, 'House rule'),
 ('EBITDA FY3/26 (actual)', '=History!Q4', 'Op income + D&A'),
]
head(I, 4, ['Item', 'Value', 'Note'])
for i, (a, b, c) in enumerate(rows, start=5):
    I.cell(i, 1, a); x = I.cell(i, 2, b); I.cell(i, 3, c)
    if not str(b).startswith('='): x.fill = inp
N = {a: f'Inputs!$B${i}' for i, (a, b, c) in enumerate(rows, start=5)}
PRICE, SH, NC, OP27, DA27, CAP27, REV27, MOTH, DROP, TAX, COE, YRS, IRR, E26 = [N[r[0]] for r in rows]

# forward schedule inputs
r0 = 21
I.cell(r0 - 1, 1, 'Forward schedule (all scenarios)').font = Font(bold=True, color=NAVY)
head(I, r0, ['Item', 'FY3/27', 'FY3/28', 'FY3/29', 'FY3/30', 'Note'])
sched = [('D&A', [178000, 190000, 200000, 205000], 'Rises with the new Izumo building [A]'),
         ('Capex', [255000, 240000, 230000, 220000], 'FY3/27 guide 255bn; then tapering [A]'),
         ('DPS (JPY)', [70, 75, 80, 85], 'FY3/27 guide 70; +5/yr [A]')]
for j, (a, v, n) in enumerate(sched):
    I.cell(r0 + 1 + j, 1, a); I.cell(r0 + 1 + j, 6, n)
    for k, x in enumerate(v): c = I.cell(r0 + 1 + j, 2 + k, x); c.fill = inp
DA_ROW, CAPEX_ROW, DPS_ROW = r0 + 1, r0 + 2, r0 + 3

# scenario drivers
s0 = 27
I.cell(s0 - 1, 1, 'Scenario drivers (FY3/28, FY3/29, FY3/30)').font = Font(bold=True, color=NAVY)
head(I, s0, ['Driver', 'Bear', 'Base', 'Bull', 'Note'])
SC = ['Bear', 'Base', 'Bull']
drv = [('Probability', [.25, .50, .25], 'House convention 25/50/25'),
       ('Capacitor volume FY3/28', [.05, .15, .20], 'AI-server units +30%/yr (Murata) vs consumer flat'),
       ('Capacitor volume FY3/29', [-.08, .08, .12], 'Bear = 2019-style destock'),
       ('Capacitor volume FY3/30', [.02, -.02, .05], ''),
       ('Capacitor price FY3/28', [-.03, .03, .10], 'Bull = Murata joins SEMCO/Yageo hikes'),
       ('Capacitor price FY3/29', [-.10, .01, .03], 'Bear = 2019 ASP -15%/qtr at Yageo'),
       ('Capacitor price FY3/30', [-.03, -.05, -.02], 'Normal annual price erosion returns'),
       ('Other revenue growth p.a.', [.02, .03, .04], 'RF modules, inductors, batteries'),
       ('Exit EV / 5-yr-mean EBITDA (x)', ['=Band!$F$5', '=Band!$F$6', '=Band!$F$7'], 'Own band p25 / median / p75, May-2016 to now')]
for j, (a, v, n) in enumerate(drv):
    I.cell(s0 + 1 + j, 1, a); I.cell(s0 + 1 + j, 5, n)
    for k, x in enumerate(v):
        c = I.cell(s0 + 1 + j, 2 + k, x)
        if not str(x).startswith('='): c.fill = inp
DRV = {a: s0 + 1 + j for j, (a, v, n) in enumerate(drv)}
for r in range(5, 50):
    for c in range(2, 6):
        cell = I.cell(r, c)
        if isinstance(cell.value, float) and abs(cell.value) < 1.01 and r >= s0: cell.number_format = '0.0%'
for a in ('Other-business EBITDA margin', 'Drop-through of price on capacitor EBITDA', 'Tax + minorities on (EBITDA - D&A)', 'Cost of equity (CAPM)', 'Target IRR for entry'):
    I[N[a].split('!')[1].replace('$', '')].number_format = '0.0%'
I[N['Exit EV / 5-yr-mean EBITDA (x)'] if False else 'B36'].number_format = '0.0x' if False else '0.0'
I.column_dimensions['A'].width = 42; I.column_dimensions['C'].width = 14; I.column_dimensions['E'].width = 14; I.column_dimensions['F'].width = 46
for c in 'BD': I.column_dimensions[c].width = 14

# ---------------- History ----------------
Hs = wb.create_sheet('History')
title(Hs, 'Murata: 15 years of history (FYE March, JPY mn)', 'Murata fact books 2022/2024/2026. US GAAP to FY3/23, IFRS from FY3/24 (FY3/23 shown IFRS-restated where available).')
fys = list(hist.fy)
head(Hs, 3, ['Metric'] + fys)
mets = [('Revenue', 'rev'), ('Operating income', 'op'), ('D&A', 'da'), ('EBITDA', None), ('EBITDA margin', None), ('5-yr mean EBITDA', None),
        ('Capacitor revenue', 'cap'), ('Capacitor share of revenue', None), ('Net income', 'ni'), ('Capex', 'capex'),
        ('Cash', 'cash'), ('Interest-bearing debt', 'debt'), ('Net cash', None), ('Shares ex-treasury (mn)', 'sh'), ('DPS (JPY, split-adj)', 'dps'), ('Equity (parent)', 'eq')]
for i, (lab, key) in enumerate(mets, start=4):
    Hs.cell(i, 1, lab)
    for j, fy in enumerate(fys):
        col = L(2 + j); c = Hs.cell(i, 2 + j)
        if key: c.value = None if pd.isna(hist.loc[j, key]) else float(hist.loc[j, key])
        elif lab == 'EBITDA': c.value = f'={col}5+{col}6'
        elif lab == 'EBITDA margin': c.value = f'={col}7/{col}4'; c.number_format = '0.0%'
        elif lab == '5-yr mean EBITDA': c.value = f'=AVERAGE({L(j-2)}7:{col}7)' if j >= 4 else None
        elif lab == 'Capacitor share of revenue': c.value = f'={col}10/{col}4'; c.number_format = '0.0%'
        elif lab == 'Net cash': c.value = f'={col}14-{col}15'
        if c.number_format == 'General': c.number_format = '#,##0'
# EBITDA FY3/26 lives at Q7 (col Q = 17th = FY3/2026)
assert fys[-1] == 'FY3/2026'
I['B18'] = f'=History!{L(1 + len(fys))}7'
Hs.column_dimensions['A'].width = 28
for j in range(len(fys)): Hs.column_dimensions[L(2 + j)].width = 11

# ---------------- Band ----------------
Bd = wb.create_sheet('Band')
title(Bd, 'Own valuation band: EV / 5-yr-mean EBITDA', 'Monthly close x shares ex-treasury less net cash of the latest reported FY, over the trailing 5-FY mean EBITDA. P/B shown as the timing check.')
Bd['E4'] = 'Statistic'; Bd['F4'] = 'EV/5y EBITDA'; Bd['G4'] = 'P/B'
for c in ('E4', 'F4', 'G4'): Bd[c].font = hdr; Bd[c].fill = hfill
bs = band['band_series']; n = len(bs); last = 4 + n
Bd['A4'] = 'Month'; Bd['B4'] = 'EV / 5y-mean EBITDA'; Bd['C4'] = 'P/B'
for c in ('A4', 'B4', 'C4'): Bd[c].font = hdr; Bd[c].fill = hfill
for i, r in enumerate(bs, start=5):
    Bd.cell(i, 1, r['month']); Bd.cell(i, 2, r['mult']).number_format = '0.0'; Bd.cell(i, 3, r['pb']).number_format = '0.00'
stats = [('p25 (Bear exit)', 'PERCENTILE(B5:B{0},0.25)', 'PERCENTILE(C5:C{0},0.25)'),
         ('Median (Base exit)', 'MEDIAN(B5:B{0})', 'MEDIAN(C5:C{0})'),
         ('p75 (Bull exit)', 'PERCENTILE(B5:B{0},0.75)', 'PERCENTILE(C5:C{0},0.75)'),
         ('Today', 'B{0}', 'C{0}'),
         ('Today vs median', 'B{0}/MEDIAN(B5:B{0})-1', 'C{0}/MEDIAN(C5:C{0})-1')]
for k, (a, f1, f2) in enumerate(stats, start=5):
    Bd.cell(k, 5, a); Bd.cell(k, 6, '=' + f1.format(last)).number_format = '0.0'; Bd.cell(k, 7, '=' + f2.format(last)).number_format = '0.00'
Bd['F9'].number_format = '0%'; Bd['G9'].number_format = '0%'
Bd['E11'] = 'Band excludes nothing: the 2026 spike is inside the sample. Pre-2026 the median is 11.5x.'
Bd['E11'].font = Font(italic=True, color='687386')
Bd.column_dimensions['A'].width = 10; Bd.column_dimensions['E'].width = 22

# ---------------- Scenarios ----------------
S = wb.create_sheet('Scenarios')
title(S, 'Scenarios to FY3/2030 and probability-weighted value', 'Capacitor EBITDA(t) = capacitor EBITDA(t-1) x (1+volume) + price-driven revenue x drop-through. Exit at Mar-2030 on the own band.')
FYC = ['FY3/27', 'FY3/28', 'FY3/29', 'FY3/30']
summary_rows = {}
blk = 4
for si, sc in enumerate(SC):
    col_in = L(2 + si)  # Inputs column for this scenario
    r = blk
    S.cell(r, 1, f'{sc} case').font = Font(bold=True, size=12, color=NAVY)
    head(S, r + 1, ['Line'] + FYC)
    lines = ['Capacitor revenue', 'Capacitor EBITDA', 'Capacitor EBITDA margin', 'Other revenue', 'Other EBITDA', 'Group revenue', 'Group EBITDA',
             'D&A', 'Net income (approx.)', 'Capex', 'Dividends', 'Net cash (end)']
    R = {ln: r + 2 + i for i, ln in enumerate(lines)}
    for ln in lines: S.cell(R[ln], 1, ln)
    for k in range(4):
        c = L(2 + k); p = L(1 + k); icol = L(2 + k)  # Inputs forward schedule column
        if k == 0:
            S[f'{c}{R["Capacitor revenue"]}'] = f'={CAP27}'
            S[f'{c}{R["Other revenue"]}'] = f'={REV27}-{CAP27}'
            S[f'{c}{R["Other EBITDA"]}'] = f'={c}{R["Other revenue"]}*{MOTH}'
            S[f'{c}{R["Capacitor EBITDA"]}'] = f'={OP27}+{DA27}-{c}{R["Other EBITDA"]}'
        else:
            vol = f'Inputs!${col_in}${DRV[f"Capacitor volume FY3/{27+k}"]}'
            prc = f'Inputs!${col_in}${DRV[f"Capacitor price FY3/{27+k}"]}'
            S[f'{c}{R["Capacitor revenue"]}'] = f'={p}{R["Capacitor revenue"]}*(1+{vol})*(1+{prc})'
            S[f'{c}{R["Capacitor EBITDA"]}'] = f'={p}{R["Capacitor EBITDA"]}*(1+{vol})+{p}{R["Capacitor revenue"]}*(1+{vol})*{prc}*{DROP}'
            S[f'{c}{R["Other revenue"]}'] = f'={p}{R["Other revenue"]}*(1+Inputs!${col_in}${DRV["Other revenue growth p.a."]})'
            S[f'{c}{R["Other EBITDA"]}'] = f'={c}{R["Other revenue"]}*{MOTH}'
        S[f'{c}{R["Capacitor EBITDA margin"]}'] = f'={c}{R["Capacitor EBITDA"]}/{c}{R["Capacitor revenue"]}'
        S[f'{c}{R["Group revenue"]}'] = f'={c}{R["Capacitor revenue"]}+{c}{R["Other revenue"]}'
        S[f'{c}{R["Group EBITDA"]}'] = f'={c}{R["Capacitor EBITDA"]}+{c}{R["Other EBITDA"]}'
        S[f'{c}{R["D&A"]}'] = f'=Inputs!{icol}{DA_ROW}'
        S[f'{c}{R["Net income (approx.)"]}'] = f'=({c}{R["Group EBITDA"]}-{c}{R["D&A"]})*(1-{TAX})'
        S[f'{c}{R["Capex"]}'] = f'=Inputs!{icol}{CAPEX_ROW}'
        S[f'{c}{R["Dividends"]}'] = f'=Inputs!{icol}{DPS_ROW}*{SH}'
        prev_cash = NC if k == 0 else f'{p}{R["Net cash (end)"]}'
        S[f'{c}{R["Net cash (end)"]}'] = f'={prev_cash}+{c}{R["Net income (approx.)"]}+{c}{R["D&A"]}-{c}{R["Capex"]}-{c}{R["Dividends"]}'
        for ln in lines:
            S[f'{c}{R[ln]}'].number_format = '0.0%' if 'margin' in ln else '#,##0'
    # valuation block
    v = r + 2 + len(lines) + 1
    vals = [('5-yr mean EBITDA FY3/26-30', f'=AVERAGE({E26},B{R["Group EBITDA"]}:E{R["Group EBITDA"]})', '#,##0'),
            ('Exit multiple (x)', f'=Inputs!{col_in}{DRV["Exit EV / 5-yr-mean EBITDA (x)"]}', '0.0'),
            ('Exit EV', f'=B{v}*B{v+1}', '#,##0'),
            ('Exit equity value', f'=B{v+2}+E{R["Net cash (end)"]}', '#,##0'),
            ('Value per share at exit (JPY)', f'=B{v+3}/{SH}', '#,##0'),
            ('Dividends received to exit (JPY)', f'=SUM(Inputs!B{DPS_ROW}:E{DPS_ROW})', '#,##0'),
            ('IRR from today', f'=((B{v+4}+B{v+5})/{PRICE})^(1/{YRS})-1', '0.0%'),
            ('Present value per share at CoE (JPY)', f'=B{v+4}/(1+{COE})^{YRS}+SUMPRODUCT(Inputs!B{DPS_ROW}:E{DPS_ROW},1/(1+{COE})^{{0.5,1.5,2.5,3.5}})', '#,##0'),
            ('Entry price for 20% IRR (JPY)', f'=(B{v+4}+B{v+5})/(1+{IRR})^{YRS}', '#,##0'),
            ('Probability', f'=Inputs!{col_in}{DRV["Probability"]}', '0%')]
    for k, (a, f, fmt) in enumerate(vals):
        S.cell(v + k, 1, a).font = Font(bold=True); c = S.cell(v + k, 2, f); c.number_format = fmt; c.fill = sub
    summary_rows[sc] = dict(vps=f'B{v+4}', irr=f'B{v+6}', pv=f'B{v+7}', entry=f'B{v+8}', p=f'B{v+9}', mean5=f'B{v}', mult=f'B{v+1}', cash=f'E{R["Net cash (end)"]}', ebitda30=f'E{R["Group EBITDA"]}')
    blk = v + len(vals) + 2
S.column_dimensions['A'].width = 38
for c in 'BCDE': S.column_dimensions[c].width = 14

# ---------------- Valuation summary ----------------
V = wb.create_sheet('Valuation', 0)
title(V, 'Murata (6981.T): house valuation', 'Method: EV / 5-yr-mean EBITDA, own band p25/median/p75 (no regime credit); P/B timing check. Price 2-Oct-2026.')
head(V, 4, ['Line', 'Bear', 'Base', 'Bull', 'Prob-weighted'])
lines = [('Probability', 'p', '0%'), ('Exit multiple (x)', 'mult', '0.0'), ('5-yr mean EBITDA (JPY mn)', 'mean5', '#,##0'), ('FY3/30 EBITDA (JPY mn)', 'ebitda30', '#,##0'),
         ('Net cash Mar-2030 (JPY mn)', 'cash', '#,##0'), ('Value per share at exit', 'vps', '#,##0'), ('PV per share at CoE', 'pv', '#,##0'), ('IRR from today', 'irr', '0.0%'), ('Entry for 20% IRR', 'entry', '#,##0')]
for i, (a, k, fmt) in enumerate(lines, start=5):
    V.cell(i, 1, a)
    for j, sc in enumerate(SC):
        c = V.cell(i, 2 + j, f'=Scenarios!{summary_rows[sc][k]}'); c.number_format = fmt
    if k not in ('p', 'mult', 'irr'):
        c = V.cell(i, 5, f'=SUMPRODUCT(B5:D5,B{i}:D{i})'); c.number_format = fmt
    elif k == 'irr':
        c = V.cell(i, 5, f'=((E10+SUM(Inputs!B{DPS_ROW}:E{DPS_ROW}))/{PRICE})^(1/{YRS})-1'); c.number_format = fmt
V['A16'] = 'Share price'; V['B16'] = f'={PRICE}'; V['B16'].number_format = '#,##0'
V['A17'] = 'PW PV vs price'; V['B17'] = '=E11/B16-1'; V['B17'].number_format = '0%'
V['A18'] = 'EV / 5y-mean EBITDA today'; V['B18'] = '=Band!F8'; V['B18'].number_format = '0.0'
V['A19'] = 'Own-band median'; V['B19'] = '=Band!F6'; V['B19'].number_format = '0.0'
V['A20'] = 'Reverse: exit multiple the price needs for a 0% IRR (Base)'; V['B20'] = f"=({PRICE}*{SH}-Scenarios!{summary_rows['Base']['cash']})/Scenarios!{summary_rows['Base']['mean5']}"; V['B20'].number_format = '0.0'
V['A21'] = 'Reverse: exit multiple the price needs for a 20% IRR (Base)'; V['B21'] = f"=({PRICE}*(1+{IRR})^{YRS}*{SH}-Scenarios!{summary_rows['Base']['cash']})/Scenarios!{summary_rows['Base']['mean5']}"; V['B21'].number_format = '0.0'
V['A22'] = 'P/B today vs own median (timing check)'; V['B22'] = '=Band!G9'; V['B22'].number_format = '0%'
V['A24'] = 'Verdict'; V['A24'].font = Font(bold=True, color=NAVY)
V['B24'] = '=IF(B16>E13,"Above the 20%-IRR entry: wait / avoid on the house method",IF(B16>E11,"Between entry and PW value: hold","Below PW value: buy"))'
V.column_dimensions['A'].width = 52
for c in 'BCDE': V.column_dimensions[c].width = 15

# ---------------- Sensitivity ----------------
G = wb.create_sheet('Sensitivity')
title(G, 'Sensitivity grids', 'Grid 1 = the single technical driver: annual MLCC price change x annual volume growth, FY3/28-30, Base other inputs, Base exit multiple. Grid 2 = exit multiple x 5-yr mean EBITDA.')
# grid 1: per-cell closed form, 3 years constant g and p, written out explicitly
base_cap27 = "Scenarios!B6"; base_capE27 = "Scenarios!B7"  # Base block rows defined below via summary_rows; verify
# locate Base block rows
G['A4'] = 'Value per share at exit (JPY): rows = annual capacitor volume growth, columns = annual capacitor price change'; G['A4'].font = Font(bold=True)
gs = [-0.05, 0.0, 0.05, 0.10, 0.15, 0.20]; ps = [-0.10, -0.05, -0.02, 0.0, 0.03, 0.06, 0.10]
G['A5'] = 'vol \\ price'
for j, p in enumerate(ps): c = G.cell(5, 2 + j, p); c.number_format = '0%'; c.font = hdr; c.fill = hfill
base_r0 = None
for k, v in summary_rows.items():
    pass
# Base block: rows start where 'Base case' label sits; capacitor revenue/EBITDA FY3/27 at column B
for row in S.iter_rows(min_col=1, max_col=1):
    if row[0].value == 'Base case': base_r0 = row[0].row
CR, CE = f'Scenarios!$B${base_r0+2}', f'Scenarios!$B${base_r0+3}'
OR27 = f'Scenarios!$B${base_r0+5}'
def capE(n, g, p):  # capacitor EBITDA after n years
    if n == 0: return CE
    return f'({capE(n-1,g,p)}*(1+{g})+{CR}*(1+{g})^{n}*(1+{p})^{n-1}*{p}*{DROP})'
oth = lambda n: f'{OR27}*(1+Inputs!$C${DRV["Other revenue growth p.a."]})^{n}*{MOTH}'
for i, g in enumerate(gs):
    rr = 6 + i; c = G.cell(rr, 1, g); c.number_format = '0%'; c.font = hdr; c.fill = hfill
    for j, p in enumerate(ps):
        gc, pc = f'$A{rr}', f'{L(2+j)}$5'
        eb = [f'({OP27}+{DA27})'] + [f'({capE(n, gc, pc)}+{oth(n)})' for n in (1, 2, 3)]
        mean5 = f'(({E26})+{"+".join(eb)})/5'
        # net cash: approximate with Base net cash at Mar-2030 (cash sensitivity is second-order)
        f = f'=({mean5}*Inputs!$C${DRV["Exit EV / 5-yr-mean EBITDA (x)"]}+Scenarios!{summary_rows["Base"]["cash"]})/{SH}'
        G.cell(rr, 2 + j, f).number_format = '#,##0'
G.conditional_formatting.add('B6:H11', ColorScaleRule(start_type='min', start_color='F8E3E1', mid_type='percentile', mid_value=50, mid_color='FFFFFF', end_type='max', end_color='E0F2E7'))
G['A13'] = 'Net cash held at the Base-case Mar-2030 level in grid 1 (second-order effect). Current price for reference:'; G['H13'] = f'={PRICE}'; G['H13'].number_format = '#,##0'
# grid 2
G['A15'] = 'Value per share at exit (JPY): rows = exit EV / 5-yr-mean EBITDA, columns = 5-yr mean EBITDA (JPY bn)'; G['A15'].font = Font(bold=True)
ms = [8, 10.4, 11.6, 13.5, 16, 20, 25, 30]; es = [450, 500, 550, 600, 650, 700, 800]
G['A16'] = 'mult \\ EBITDA'
for j, e in enumerate(es): c = G.cell(16, 2 + j, e); c.font = hdr; c.fill = hfill
for i, m in enumerate(ms):
    rr = 17 + i; c = G.cell(rr, 1, m); c.font = hdr; c.fill = hfill
    for j in range(len(es)):
        G.cell(rr, 2 + j, f'=($A{rr}*{L(2+j)}$16*1000+Scenarios!{summary_rows["Base"]["cash"]})/{SH}').number_format = '#,##0'
G.conditional_formatting.add('B17:H24', ColorScaleRule(start_type='min', start_color='F8E3E1', mid_type='percentile', mid_value=50, mid_color='FFFFFF', end_type='max', end_color='E0F2E7'))
G.column_dimensions['A'].width = 16
for j in range(2, 10): G.column_dimensions[L(j)].width = 12

# ---------------- Sources ----------------
So = wb.create_sheet('Sources')
title(So, 'Sources', 'Tags: F = company primary document / exchange data; A = attributed or assumption; E = our arithmetic.')
src = [('History FY3/12-FY3/22', 'Murata Fact Book 2022', 'https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2022/0713/factbook2022.ashx', 'F'),
       ('History FY3/16-FY3/26', 'Murata Fact Book 2026', 'https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0626/factbook2026.ashx', 'F'),
       ('FY3/27 guidance (31 Jul 2026)', 'Murata 1Q FY2026 results', 'https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0731d/26q1-e-speach.ashx', 'F'),
       ('Monthly prices', 'Yahoo Finance chart API', 'https://query1.finance.yahoo.com/v8/finance/chart/6981.T', 'F'),
       ('Consensus TP ¥10,414, fwd P/E 37.8x', 'stockanalysis.com, 2-Oct-2026', 'https://stockanalysis.com/quote/tyo/6981/', 'A'),
       ('Valuation method ruling', 'Roy, 2-Oct-2026: EV / mid-cycle EBITDA band (memory card D-M1 logic)', '', 'A'),
       ('Scenario drivers', 'targets/MLCC/research memos 01-03, 06', '', 'A/E')]
head(So, 4, ['Item', 'Source', 'URL', 'Tag'])
for i, r in enumerate(src, start=5):
    for j, x in enumerate(r): So.cell(i, 1 + j, x)
So.column_dimensions['A'].width = 34; So.column_dimensions['B'].width = 60; So.column_dimensions['C'].width = 80

wb.save(OUT); print('saved', OUT, 'base block row', base_r0)
