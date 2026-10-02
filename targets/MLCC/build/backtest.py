"""MLCC basket backtest: equal-weight monthly-rebalanced basket of pure-play MLCC names
(local-currency, split/div-adjusted Yahoo adjclose). Finds historical months that match
today's phase and measures forward returns."""
import pandas as pd, numpy as np, json
df=pd.read_csv('data/clean/monthly_prices.csv',index_col=0,parse_dates=True)
CORE=['6981.T','009150.KS','6976.T','2327.TW','2492.TW']        # pure-ish MLCC
BROAD=CORE+['6762.T','6971.T']
print({c:str(df[c].first_valid_index().date()) for c in BROAD})
def basket(cols):
    r=df[cols].pct_change(fill_method=None)
    r=r.where(r.abs()<1.5)            # guard bad prints
    b=(1+r.mean(axis=1,skipna=True).fillna(0)).cumprod()
    return b[b.index>='2001-01-01']
B=basket(CORE); BB=basket(BROAD)
b=B/B.iloc[0]*100
feat=pd.DataFrame({'idx':b})
feat['hi36']=b.rolling(36,min_periods=12).max()
feat['dd']=b/feat['hi36']-1
feat['ret12']=b.pct_change(12)
feat['run18']=b/b.rolling(18,min_periods=12).min()-1      # run-up off 18m low
feat['m_since_peak']=[ (i - b.loc[:i].tail(36).idxmax()).days//30 for i in b.index]
for h in (6,12,24): feat[f'fwd{h}']=b.shift(-h)/b-1
now=feat.iloc[-1]; print('NOW',now.round(3).to_dict())
# Analog rule: run-up >= 100% off the 18m low occurred, and now 25-50% below the 36m high, 2-6 months after the peak
cond=(feat.run18.shift(0).rolling(9).max()>=1.0)&(feat.dd.between(-0.50,-0.25))&(feat.m_since_peak.between(2,6))
an=feat[cond & (feat.index<feat.index[-1])]
print(an[['idx','dd','run18','m_since_peak','fwd6','fwd12','fwd24']].round(2).to_string())
# Episode-level (first qualifying month per peak)
an=an.copy(); an['peak']=[b.loc[:i].tail(36).idxmax() for i in an.index]
ep=an.groupby('peak').head(1)
print(ep[['dd','m_since_peak','fwd6','fwd12','fwd24']].round(2).to_string())
# Broad, unconditional
uncond={h:feat[f'fwd{h}'].dropna().describe()[['mean','50%']].round(3).to_dict() for h in (6,12,24)}
# drawdown buckets
feat['ddb']=pd.cut(feat.dd,[-1,-.5,-.35,-.25,-.15,-.05,0.01])
bk=feat.groupby('ddb',observed=True)[['fwd12','fwd24']].agg(['mean','median','count']).round(3)
print(bk)
# Peaks/troughs of the basket (cycle chronology)
roll=b.rolling(25,center=True,min_periods=6)
pk=b[(b==roll.max())]; tr=b[(b==roll.min())]
print('PEAKS',[d.strftime('%Y-%m') for d in pk.index]); print('TROUGHS',[d.strftime('%Y-%m') for d in tr.index])
out={'basket_core':{d.strftime('%Y-%m'):round(v,2) for d,v in b.items()},
     'basket_broad':{d.strftime('%Y-%m'):round(v,2) for d,v in (BB/BB.iloc[0]*100).items()},
     'now':{k:(None if pd.isna(v) else round(float(v),4)) for k,v in now.items()},
     'episodes':[{'peak':p.strftime('%Y-%m'),'entry':i.strftime('%Y-%m'),'dd':round(r.dd,3),
                  **{f'fwd{h}':(None if pd.isna(r[f'fwd{h}']) else round(r[f'fwd{h}'],3)) for h in (6,12,24)}} for (i,r),p in zip(ep.iterrows(),ep.peak)],
     'analog_months':len(an),'analog_stats':{f'fwd{h}':{'mean':round(an[f'fwd{h}'].mean(),3),'median':round(an[f'fwd{h}'].median(),3),'hit':round((an[f'fwd{h}']>0).mean(),2),'n':int(an[f'fwd{h}'].notna().sum())} for h in (6,12,24)},
     'unconditional':uncond,
     'dd_buckets':{str(k):{'fwd12_med':round(v[('fwd12','median')],3),'fwd24_med':round(v[('fwd24','median')],3),'n':int(v[('fwd12','count')])} for k,v in bk.iterrows()},
     'peaks':[d.strftime('%Y-%m') for d in pk.index],'troughs':[d.strftime('%Y-%m') for d in tr.index]}
json.dump(out,open('data/backtest.json','w'),indent=1)
