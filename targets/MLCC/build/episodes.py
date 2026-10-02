"""Per-cycle episodes for the equal-weight MLCC basket: run-up, peak, depth, and the forward
return of buying (a) at the first month the basket is >=35% below its cycle peak and
(b) 4 months after the peak -- the two ways today's position (-36%, ~4-5m after peak) can be matched."""
import pandas as pd, json
df=pd.read_csv('data/clean/monthly_prices.csv',index_col=0,parse_dates=True)
CORE=['6981.T','009150.KS','6976.T','2327.TW','2492.TW']
r=df[CORE].pct_change(fill_method=None); r=r.where(r.abs()<1.5)
b=(1+r.mean(axis=1).fillna(0)).cumprod(); b=b[b.index>='2000-01-01']; b=b/b.iloc[0]*100
# also per-name daily-free monthly
peaks=['2000-02','2004-01','2007-06','2010-03','2015-10','2018-05','2021-02','2024-06','2026-05']
eps=[]
for p in peaks:
    win=b[(b.index>=pd.Timestamp(p)-pd.DateOffset(months=4))&(b.index<=pd.Timestamp(p)+pd.DateOffset(months=4))]
    pk=win.idxmax(); pv=b[pk]
    pre=b[(b.index>=pk-pd.DateOffset(months=24))&(b.index<=pk)]; run=pv/pre.min()-1
    post=b[(b.index>pk)&(b.index<=pk+pd.DateOffset(months=36))]
    tr=post.idxmin() if len(post) else None
    def fwd(i,h):
        j=b.index.get_loc(i)+h
        return round(b.iloc[j]/b[i]-1,3) if j<len(b) else None
    x=post[post<=pv*0.65]; e1=x.index[0] if len(x) else None
    e2=pk+pd.DateOffset(months=4); e2=e2 if e2 in b.index else None
    eps.append(dict(peak=pk.strftime('%Y-%m'),runup_24m=round(run,2),
        trough=tr.strftime('%Y-%m') if tr is not None else None,
        depth=round(post.min()/pv-1,2) if len(post) else None,
        months_to_trough=((tr-pk).days//30) if tr is not None else None,
        buy_at_minus35=e1.strftime('%Y-%m') if e1 is not None else None,
        **({f'm35_fwd{h}':fwd(e1,h) for h in (6,12,24)} if e1 is not None else {}),
        buy_peak_plus4=e2.strftime('%Y-%m') if e2 is not None else None,
        dd_at_plus4=round(b[e2]/pv-1,2) if e2 is not None else None,
        **({f'p4_fwd{h}':fwd(e2,h) for h in (6,12,24)} if e2 is not None else {})))
E=pd.DataFrame(eps); pd.set_option('display.width',250); print(E.to_string())
j=json.load(open('data/backtest.json')); j['episodes_v2']=eps
j['basket_core']={d.strftime('%Y-%m'):round(v,2) for d,v in b.items()}
json.dump(j,open('data/backtest.json','w'),indent=1)
E.to_csv('data/clean/cycle_episodes.csv',index=False)
