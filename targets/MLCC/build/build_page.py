import json
t=open('build/page_template.html').read(); d=open('data/dashboard.json').read()
open('mlcc_cycle_watch.html','w').write(t.replace('__DATA__', d.replace('</','<\\/')))
print('ok', len(t)+len(d))
