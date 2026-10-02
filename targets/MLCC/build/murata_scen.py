"""Prototype of the Murata scenario math (mirrored by formulas in the Excel model)."""
import json
A = dict(price=8467, sh=1820.292, netcash=650441, cap26=936418, cap27=1157500, oth27=2110000-1157500, ebitda26=460047,
         ebitda_hist=[579643,467505,391320,453037,460047], da=[178000,190000,200000,205000], capex=[255000,240000,230000,220000],
         m_vol=0.40, m_price=0.90, tax=0.25, dps=[70,75,80,85], coe=0.08, exit_year_frac=3.5)
# FY27 EBITDA from guidance: OP 430bn + D&A 178bn
E27 = 430000 + 178000
m_oth = 0.13; m_cap27 = (E27 - A['oth27']*m_oth)/A['cap27']
S = {'Bear':dict(p=.25,vol=[.05,-.08,.02],pr=[-.03,-.10,-.03],oth=.02,mult=10.4),
     'Base':dict(p=.50,vol=[.15,.08,-.02],pr=[.03,.01,-.05],oth=.03,mult=11.6),
     'Bull':dict(p=.25,vol=[.20,.12,.05],pr=[.10,.03,-.02],oth=.04,mult=13.5)}
out={}
for k,s in S.items():
    cap=A['cap27']; oth=A['oth27']; capE=cap*m_cap27; eb=[E27]; div=A['dps'][0]*A['sh']; cash=A['netcash']
    ni27=430000*0.77; cash+= ni27+A['da'][0]-A['capex'][0]-div
    for i in range(3):
        vol_rev=cap*s['vol'][i]; base_rev=cap+vol_rev; pr_rev=base_rev*s['pr'][i]
        capE = capE*(1+s['vol'][i]) + pr_rev*A['m_price']; cap=base_rev+pr_rev
        oth*=1+s['oth']; e=capE+oth*m_oth; eb.append(e)
        ni=(e-A['da'][i+1])*0.77; cash+=ni+A['da'][i+1]-A['capex'][i+1]-A['dps'][i+1]*A['sh']
    mean5=(A['ebitda26']+sum(eb))/5
    ev=s['mult']*mean5; eq=ev+cash; vps=eq/A['sh']; divs=sum(A['dps'])
    irr=((vps+divs)/A['price'])**(1/A['exit_year_frac'])-1
    pv=(vps)/(1+A['coe'])**A['exit_year_frac'] + sum(d/(1+A['coe'])**(i+0.5) for i,d in enumerate(A['dps']))
    entry20=(vps+divs)/(1.2**A['exit_year_frac'])
    out[k]=dict(ebitda=[round(x) for x in eb],mean5=round(mean5),cash=round(cash),vps=round(vps),irr=round(irr,3),pv=round(pv),entry20=round(entry20),cap30=round(cap))
pw=sum(S[k]['p']*out[k]['pv'] for k in S); pwv=sum(S[k]['p']*out[k]['vps'] for k in S)
print(json.dumps(out,indent=0)); print('m_cap27',round(m_cap27,3),'PW PV',round(pw),'PW exit value',round(pwv),'entry20 PW',round(sum(S[k]['p']*out[k]['entry20'] for k in S)))
# reverse: multiple implied today on base mean5
print('implied exit mult at today price (base, 0% IRR):', round((A['price']*A['sh']-out['Base']['cash'])/out['Base']['mean5'],1))
