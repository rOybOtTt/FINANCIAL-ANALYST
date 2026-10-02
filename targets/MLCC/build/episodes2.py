"""Adds max further drawdown after the -35% entry, and the same test for Murata alone (-30% entry)."""
import pandas as pd, json
df=pd.read_csv('data/clean/monthly_prices.csv',index_col=0,parse_dates=True)
CORE=['6981.T','009150.KS','6976.T','2327.TW','2492.TW']
r=df[CORE].pct_change(fill_method=None); r=r.where(r.abs()<1.5)
b=(1+r.mean(axis=1).fillna(0)).cumprod(); b=b[b.index>='2000-01-01']; b=b/b.iloc[0]*100
def study(s,peaks,thr):
    rows=[]
    for p in peaks:
        w=s[(s.index>=pd.Timestamp(p)-pd.DateOffset(months=5))&(s.index<=pd.Timestamp(p)+pd.DateOffset(months=5))]
        if not len(w): continue
        pk=w.idxmax(); pv=s[pk]; post=s[s.index>pk]
        x=post[post<=pv*(1-thr)]
        if not len(x): rows.append(dict(peak=pk.strftime('%Y-%m'),entry=None)); continue
        e=x.index[0]; i=s.index.get_loc(e)
        f=lambda h: round(s.iloc[i+h]/s[e]-1,3) if i+h<len(s) else None
        nxt=s.iloc[i:i+25]
        rows.append(dict(peak=pk.strftime('%Y-%m'),entry=e.strftime('%Y-%m'),fwd6=f(6),fwd12=f(12),fwd24=f(24),fwd36=f(36),
            further_dd=round(nxt.min()/s[e]-1,3),months_to_low=int((nxt.idxmin()-e).days//30),
            back_to_peak=next((d.strftime('%Y-%m') for d,v in s.iloc[i:].items() if v>=pv),None)))
    return rows
peaks=['2000-03','2004-03','2007-06','2010-03','2018-05','2021-02','2024-06']
basket=study(b,peaks,0.35)
m=df['6981.T'].dropna()
mur=study(m,['2001-04','2004-03','2007-06','2010-12','2015-08','2018-05','2021-01','2024-03'],0.30)
pd.set_option('display.width',250)
print(pd.DataFrame(basket).to_string()); print(pd.DataFrame(mur).to_string())
j=json.load(open('data/backtest.json')); j['entry_minus35_basket']=basket; j['entry_minus30_murata']=mur
json.dump(j,open('data/backtest.json','w'),indent=1)
pd.DataFrame(basket).to_csv('data/clean/backtest_basket_minus35.csv',index=False)
pd.DataFrame(mur).to_csv('data/clean/backtest_murata_minus30.csv',index=False)
