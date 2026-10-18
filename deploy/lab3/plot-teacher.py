"""Plot only teacher-run analysis JSON; raw JTL statistics are computed independently in Node."""
import json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/playwright/lab3-teacher-20261018/analysis'
D=json.loads((OUT/'results.json').read_text());P=json.loads((OUT/'plot-data.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':200})
colors={'jpa':'#2166ac','mybatis':'#d6604d'}
def save(fig,name):
 fig.tight_layout();fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
for metric,label,name in [('success_rps','Successful requests / s','throughput'),('p95_ms','Mean of per-run P95 (ms)','p95'),('mean_ms','Mean response time (ms)','mean-latency')]:
 fig,axes=plt.subplots(1,2,figsize=(10,3.8))
 for ax,op in zip(axes,['ReadProduct','WriteProduct']):
  for profile in ['jpa','mybatis']:
   a=sorted([g for g in D['groups'] if g['operation']==op and g['profile']==profile],key=lambda x:x['threads'])
   if a:ax.errorbar([g['threads'] for g in a],[g[metric+'_mean'] for g in a],yerr=[g[metric+'_sd'] for g in a],color=colors[profile],marker='o',capsize=4,label=profile.upper())
  ax.set(title=op,xlabel='Total threads / 10-second ramp / 1 iteration',ylabel=label,xticks=[100,400,1000]);ax.grid(alpha=.2);ax.legend()
 fig.suptitle('Means across three repeats; error bars = sample standard deviation',fontsize=10);save(fig,name)
for op in ['ReadProduct','WriteProduct']:
 chosen=[p for p in P if p['operation']==op and p['threads']==1000 and p['repeat']==3]
 if len(chosen)!=2:continue
 fig,axes=plt.subplots(1,2,figsize=(10,3.8));fig2,axes2=plt.subplots(2,2,figsize=(10,5.5))
 for p in chosen:
  color=colors[p['profile']];label=p['profile'].upper();values=sorted(v for t,v,n in p['response'])
  axes[0].plot(values,[100*(i+1)/len(values) for i in range(len(values))],label=label,color=color)
  buckets={}
  for t,v,n in p['response']:buckets.setdefault(int(t),[]).append(v)
  axes[1].plot(sorted(buckets),[statistics.mean(buckets[i]) for i in sorted(buckets)],marker='.',label=label,color=color)
  for ax,key in zip(axes2.flat,['app_threads','app_cpu_pct','app_memory_pct','jmeter_cpu_pct']):
   points=p['monitoring'].get(key,[])
   if points:ax.plot(*zip(*points),marker='.',label=label,color=color)
 axes[0].set(xlabel='Response time (ms)',ylabel='Cumulative requests (%)',title='Full-run response distribution')
 axes[1].set(xlabel='Seconds since first request',ylabel='Mean response time (ms)',title='1-second response trend')
 for ax in axes:ax.grid(alpha=.2);ax.legend()
 fig.suptitle(op+' / 1000 threads / 10-second ramp / 1 iteration / repeat 3');save(fig,op+'-latency')
 for ax,title,ylabel in zip(axes2.flat,['JVM live threads','Application CPU: rate[5m]','Application memory usage','Load-generator CPU: rate[5m]'],['Threads','CPU (%)','Memory (%)','CPU (%)']):
  ax.set(title=title,xlabel='Seconds since first request',ylabel=ylabel);ax.axvspan(0,10,color='#dddddd',alpha=.3);ax.grid(alpha=.2);ax.legend()
 fig2.suptitle(op+' / repeat 3; CPU values include the preceding 5 minutes',fontsize=10);save(fig2,op+'-monitoring')
print('Plots saved:',D['completed'],'runs')
