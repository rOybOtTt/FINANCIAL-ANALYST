"""Murata valuation engine: EV / 5-yr-mean EBITDA own band (approved D-M1-style method chosen by Roy for MLCC, 2 Oct 2026),
three scenarios to FY3/2030, probability-weighted value, entry for a 20% IRR, reverse valuation, sensitivity grids.
Writes data/murata_model.json. All inputs traceable to data/clean/murata_history.csv (Murata fact books) and Yahoo prices."""
import json, pandas as pd, numpy as np
H = pd.read_csv('data/clean/murata_history.csv')
def g(m, fy):
    r = H[(H.metric == m) & (H.fiscal_year == fy)]
    if 'basis' in H and len(r) > 1: r = r[~r.basis.astype(str).str.contains('US GAAP', na=False)] if fy == 'FY3/2023' else r
    return float(r.value.iloc[0]) if len(r) else np.nan
FYS = [f'FY3/{y}' for y in range(2012, 2027)]
hist = pd.DataFrame({fy: dict(rev=g('net_sales', fy), op=g('operating_income', fy), da=g('depreciation_amortization', fy),
        ni=g('net_income_attrib_parent', fy), capex=g('capex', fy), cash=g('cash_and_cash_equivalents_headline', fy),
        debt=g('interest_bearing_debt', fy), sh=g('shares_outstanding_ex_treasury_split_adj_current', fy),
        cap=g('capacitor_revenue_segment_basis', fy) if not np.isnan(g('capacitor_revenue_segment_basis', fy)) else g('capacitor_sales_product_basis', fy),
        dps=g('dps_split_adj_current', fy), eq=g('equity_attrib_parent', fy)) for fy in FYS}).T
for c in hist: hist[c] = pd.to_numeric(hist[c])
hist['ebitda'] = hist.op + hist.da; hist['ebitda_m'] = hist.ebitda / hist.rev; hist['op_m'] = hist.op / hist.rev
hist['ebitda5'] = hist.ebitda.rolling(5).mean(); hist['netcash'] = hist.cash - hist.debt
print(hist[['rev','op','ebitda','ebitda_m','ebitda5','netcash','sh','cap']].round(3).to_string())

# monthly EV / 5yr-mean EBITDA (unadjusted-for-dividend close; Yahoo 'close' is split-adjusted)
p = json.load(open('data/raw/px_6981.T.json'))['chart']['result'][0]
px = pd.Series(p['indicators']['quote'][0]['close'], index=pd.to_datetime(p['timestamp'], unit='s')).dropna()
px.index = px.index.to_period('M')
rows = []
for per, close in px.items():
    # latest fiscal year reported by then (results ~end-April -> use FY ending Mar of year-1 until May)
    y = per.year if per.month >= 5 else per.year - 1
    fy = f'FY3/{y}'
    if fy not in hist.index or np.isnan(hist.loc[fy, 'ebitda5']): continue
    r = hist.loc[fy]; ev = close * r.sh - r.netcash
    rows.append(dict(month=str(per), close=close, fy=fy, ev=ev, mult=ev / r.ebitda5, pb=close * r.sh / r['eq']))
B = pd.DataFrame(rows)
pre = B[B.month < '2026-01']
band = {k: dict(p25=round(float(d.mult.quantile(.25)), 1), p50=round(float(d.mult.median()), 1), p75=round(float(d.mult.quantile(.75)), 1),
        n=len(d), start=d.month.iloc[0], end=d.month.iloc[-1]) for k, d in (('all', B), ('pre2026', pre))}
print(band); print(B.tail(3))
json.dump(dict(hist=hist.reset_index().rename(columns={'index': 'fy'}).to_dict('records'), band=band,
               band_series=B[['month', 'mult', 'pb']].round(2).to_dict('records')), open('data/murata_band.json', 'w'), indent=1, default=float)
