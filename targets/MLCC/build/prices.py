import json,glob,os,pandas as pd
out={}
for f in glob.glob('data/raw/px_*.json'):
    t=os.path.basename(f)[3:-5]
    try: r=json.load(open(f))['chart']['result'][0]
    except Exception: continue
    ts=r['timestamp']; adj=r['indicators'].get('adjclose',[{}])[0].get('adjclose') or r['indicators']['quote'][0]['close']
    s=pd.Series(adj,index=pd.to_datetime(ts,unit='s')).dropna()
    s.index=s.index.to_period('M').to_timestamp()
    out[t]=s.groupby(level=0).last()
df=pd.DataFrame(out).sort_index()
df.to_csv('data/clean/monthly_prices.csv')
print(df.apply(lambda c:(c.first_valid_index().date(),round(c.dropna().iloc[-1],1))))
