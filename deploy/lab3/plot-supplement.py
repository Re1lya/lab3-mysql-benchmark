"""Supplemental charts from original JTL statistics; no synthetic measurements."""
import json, statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/playwright/lab3-supplement-20261018/analysis'
D=json.loads((OUT/'results.json').read_text());P=json.loads((OUT/'plot-data.json').read_text())
assert D['complete'] and D['completed']==54
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
colors={'jpa':'#2166ac','mybatis':'#d6604d'}
def save(fig,name):
    fig.tight_layout();fig.savefig(OUT/(name+'.png'),bbox_inches='tight');fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
for op,parts in [('ReadProduct',[[1000,1050,1100],[1150,1200]]),('WriteProduct',[[1000,1100],[1200,1300]])]:
    loops=2 if op=='ReadProduct' else 1
    for part,ns in enumerate(parts,1):
        fig,axes=plt.subplots(len(ns),2,figsize=(10,2.45*len(ns)),squeeze=False)
        for (left,right),n in zip(axes,ns):
            for profile in ['jpa','mybatis']:
                p=next(p for p in P if p['profile']==profile and p['operation']==op and p['threads']==n and p['repeat']==3)
                vals=sorted(v for t,v,a,c in p['response']);bucket={}
                left.plot([100*(i+1)/len(vals) for i in range(len(vals))],vals,color=colors[profile],label='JPA' if profile=='jpa' else 'MyBatis')
                for t,v,a,c in p['response']:bucket.setdefault(int(t),[]).append(v)
                right.plot(sorted(bucket),[statistics.mean(bucket[k]) for k in sorted(bucket)],color=colors[profile],marker='.',label='JPA' if profile=='jpa' else 'MyBatis')
            left.set(title=f'{n}-10-{loops} / response percentiles',xlabel='Requests (%)',ylabel='Response time (ms)')
            right.set(title=f'{n}-10-{loops} / 1-second trend',xlabel='Seconds since first request',ylabel='Mean response time (ms)')
            for ax in [left,right]:ax.grid(alpha=.2);ax.legend(fontsize=8)
        fig.suptitle(f'{op} / repeat 3 / original elapsed including connect time',fontsize=11)
        save(fig,f'{op}-detail-{part}')
fig,axes=plt.subplots(2,2,figsize=(10,6.3))
for ax,(profile,op) in zip(axes.flat,[(p,o) for p in ['jpa','mybatis'] for o in ['ReadProduct','WriteProduct']]):
    groups=sorted([g for g in D['groups'] if g['profile']==profile and g['operation']==op],key=lambda g:g['threads'])
    for metric,label,color in [('within40_pct','Original elapsed','#2166ac'),('within40_adjusted_pct','Elapsed minus Connect','#d6604d')]:
        for r in [1,2,3]:
            values=[next(row[metric] for row in D['rows'] if row['profile']==profile and row['operation']==op and row['threads']==g['threads'] and row['repeat']==r) for g in groups]
            ax.plot([g['threads'] for g in groups],values,color=color,alpha=.3,linewidth=1)
        ax.plot([g['threads'] for g in groups],[g[metric+'_mean'] for g in groups],color=color,marker='o',label=label)
    ax.axhline(80,color='#444444',linestyle='--',linewidth=1,label='80% target')
    ax.set(title=f'{profile.upper()} / {op}',xlabel='Total threads',ylabel='Successful requests <= 40 ms (%)',ylim=(-2,102));ax.grid(alpha=.2);ax.legend(fontsize=7)
fig.suptitle('Bold lines: mean of three repeats; faint lines: individual repeats',fontsize=10)
save(fig,'within40-target')
for op,n in [('ReadProduct',1200),('WriteProduct',1300)]:
    fig,axes=plt.subplots(2,2,figsize=(10,5.5))
    for profile in ['jpa','mybatis']:
        p=next(p for p in P if p['profile']==profile and p['operation']==op and p['threads']==n and p['repeat']==3)
        for ax,key in zip(axes.flat,['app_threads','app_cpu_pct','app_memory_pct','jmeter_cpu_pct']):
            points=p['monitoring'].get(key,[])
            if points:ax.plot(*zip(*points),marker='.',label='JPA' if profile=='jpa' else 'MyBatis',color=colors[profile])
    for ax,title,ylabel in zip(axes.flat,['JVM live threads','Application CPU rate[5m]','Application memory usage','Load-generator CPU rate[5m]'],['Threads','CPU (%)','Memory (%)','CPU (%)']):
        ax.set(title=title,xlabel='Seconds since first request',ylabel=ylabel);ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle(f'{op} / {n} threads / repeat 3; CPU includes preceding 5 minutes',fontsize=10)
    save(fig,op+'-monitoring')
print('Supplement charts generated from',D['samples'],'requests')
