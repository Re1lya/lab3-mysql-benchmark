"""Recompute the submitted 18 cases from unmodified JTL and verify against JMeter."""
import csv,hashlib,json,math,statistics,collections,zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'results/实验数据'
if not EV.exists():EV=ROOT/'output/playwright/lab3-final-20261018'
OUT=EV/'统计与图表';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def quantile(a,q):
    a=sorted(a);i=(len(a)-1)*q;k=int(i);return a[k]+(a[math.ceil(i)]-a[k])*(i-k)
with (EV/'原始数据/测试组索引.csv').open(encoding='utf-8-sig',newline='') as f:index=list(csv.DictReader(f))
rows=[];raws={}
for entry in index:
    jtl=EV/entry['原始数据文件'];folder=jtl.parent
    assert hashlib.sha256(jtl.read_bytes()).hexdigest()==entry['SHA256']
    with jtl.open(encoding='utf8',newline='') as f:a=list(csv.DictReader(f))
    mon=read(EV/entry['监控文件']);m=mon['测试参数'];values=[float(x['elapsed']) for x in a]
    success=sum(x['success']=='true' for x in a)
    start=min(int(x['timeStamp']) for x in a);end=max(int(x['timeStamp'])+int(x['elapsed']) for x in a)
    r=dict(name=m['name'],label=jtl.stem,profile=m['profile'],operation=m['operation'],threads=m['threads'],loops=m['loops'],
        samples=len(a),errors=len(a)-success,mean_ms=statistics.mean(values),p95_ms=quantile(values,.95),
        within40_pct=100*sum(x['success']=='true' and float(x['elapsed'])<=40 for x in a)/len(a),
        success_rps=1000*success/(end-start),min_ms=min(values),max_ms=max(values),sha256=entry['SHA256'])
    assert len(a)==m['samples']==m['threads']*m['loops'] and r['errors']==m['errors']==0
    assert m['baseline_count']==3912
    assert m['final_count']==3912+(success if m['operation']=='WriteProduct' else 0)
    with zipfile.ZipFile(EV/'JMeter测试报告.zip') as z:j=json.loads(z.read(jtl.stem+'/statistics.json'))['Total']
    assert j['sampleCount']==len(a) and j['errorCount']==r['errors']
    assert abs(j['meanResTime']-r['mean_ms'])<1e-7 and abs(j['throughput']-r['success_rps'])<1e-4
    assert j['minResTime']==r['min_ms'] and j['maxResTime']==r['max_ms']
    rows.append(r);raws[r['name']]=(a,mon,start/1000)
assert len(rows)==18 and sum(r['samples'] for r in rows)==31200
(OUT/'统计结果.json').write_text(json.dumps(dict(groups=18,samples=31200,selected_repeat=1,rows=rows),indent=2,ensure_ascii=False),encoding='utf8')
fields=['测试项目','线程数','循环次数','请求数','失败数','平均响应毫秒','P95毫秒','四十毫秒内成功比例','吞吐量每秒']
with (OUT/'各配置测试统计.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(fields)
    for r in rows:w.writerow([('JPA' if r['profile']=='jpa' else 'MyBatis')+('读取' if r['operation']=='ReadProduct' else '写入'),r['threads'],r['loops'],r['samples'],r['errors'],r['mean_ms'],r['p95_ms'],r['within40_pct'],r['success_rps']])
(OUT/'数据核验.json').write_text(json.dumps(dict(verified_runs=18,requests=31200,jtl_hashes_unchanged=True,jmeter_counts_mean_range_throughput_match=True,database_counts_match=True),indent=2),encoding='utf8')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
colors={'jpa':'#2166ac','mybatis':'#d6604d'}
for op,ns,filename in [('ReadProduct',[1000,1050,1100,1150,1200],'读取响应分布与趋势'),('WriteProduct',[1000,1100,1200,1300],'写入响应分布与趋势')]:
    fig,axes=plt.subplots(len(ns),2,figsize=(9,1.7*len(ns)),squeeze=False)
    for (left,right),n in zip(axes,ns):
        for profile in ['jpa','mybatis']:
            r=next(x for x in rows if x['operation']==op and x['threads']==n and x['profile']==profile)
            a,_,start=raws[r['name']];values=sorted(float(x['elapsed']) for x in a)
            left.plot(values,[100*(i+1)/len(values) for i in range(len(values))],label=profile.upper(),color=colors[profile])
            buckets=collections.defaultdict(list)
            for x in a:buckets[int(int(x['timeStamp'])/1000-start)].append(max(0,int(x['elapsed'])-int(x['Connect'])))
            right.plot(sorted(buckets),[statistics.mean(buckets[k]) for k in sorted(buckets)],color=colors[profile],label=profile.upper())
        left.axvline(40,color='gray',ls=':',lw=.7);left.axhline(80,color='gray',ls=':',lw=.7)
        left.set(title=f'{n} threads | response percentiles',xlabel='Elapsed (ms)',ylabel='Requests (%)',ylim=(0,102))
        right.set(title=f'{n} threads | response over time',xlabel='Seconds from first request',ylabel='Elapsed - Connect (ms)')
        for ax in [left,right]:ax.grid(alpha=.18);ax.legend(fontsize=7,loc='best')
    fig.tight_layout();fig.savefig(OUT/(filename+'.png'));plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(9,5.2))
for profile in ['jpa','mybatis']:
    r=next(x for x in rows if x['operation']=='WriteProduct' and x['threads']==1300 and x['profile']==profile)
    _,mon,start=raws[r['name']]
    for ax,file,label in zip(axes,['活跃线程监控.json','CPU使用率监控.json','内存使用率监控.json'],['Live JVM threads','Application CPU (%)','Application memory (%)']):
        d=mon[{'活跃线程监控.json':'活跃线程','CPU使用率监控.json':'CPU使用率','内存使用率监控.json':'内存使用率'}[file]]
        candidates=[x for x in d['response']['data']['result'] if (x['metric'].get('persistence')==profile if file.startswith('活跃') else x['metric'].get('instance')=='172.31.1.202:9100')]
        assert len(candidates)==1
        v=candidates[0]['values'];ax.plot([t-start for t,n in v],[float(n) for t,n in v],label=profile.upper(),color=colors[profile]);ax.set_ylabel(label);ax.grid(alpha=.18);ax.legend(fontsize=8)
axes[-1].set_xlabel('Seconds from first request');fig.tight_layout();fig.savefig(OUT/'写入测试运行监控.png');plt.close(fig)
print('Verified 18 cases and regenerated all submitted statistics and charts')
