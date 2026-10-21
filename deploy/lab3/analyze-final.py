"""Recompute the submitted 18 cases from unmodified JTL and verify against JMeter."""
import csv,hashlib,json,math,statistics,collections,zipfile
from pathlib import Path
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
print('Verified 18 cases and regenerated submitted statistics')
