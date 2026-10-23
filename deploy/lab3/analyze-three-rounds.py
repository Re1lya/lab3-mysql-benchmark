"""Recompute all 54 archived runs. Reads files only; never connects to a server."""
import csv, hashlib, json, math, re, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/实验数据/三轮复核'
RAW = OUT / 'supplement-20261018'
rows = []
manifest = []
for path in sorted(RAW.glob('*/*')):
    if path.is_file():
        manifest.append({'path': str(path.relative_to(OUT)), 'bytes': path.stat().st_size,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
for path in sorted(RAW.glob('*/samples.jtl')):
    match = re.fullmatch(r'(jpa|mybatis)-r(\d)-(ReadProduct|WriteProduct)-t(\d+)-l(\d+)', path.parent.name)
    if not match:
        raise ValueError('Unexpected run directory: ' + path.parent.name)
    framework, run, operation, threads, loops = match.groups()
    with path.open(encoding='utf-8', newline='') as stream:
        samples = list(csv.DictReader(stream))
    values = sorted(int(s['elapsed']) for s in samples)
    count = len(values)
    assert count == int(threads) * int(loops), path
    assert all(s['responseCode'] == ('200' if operation == 'ReadProduct' else '201') for s in samples), path
    def quantile(q):
        index = (count - 1) * q
        low = int(index)
        return values[low] + (values[math.ceil(index)] - values[low]) * (index - low)
    start = min(int(s['timeStamp']) for s in samples)
    end = max(int(s['timeStamp']) + int(s['elapsed']) for s in samples)
    errors = sum(s['success'] != 'true' for s in samples)
    rows.append(dict(framework=framework, run=int(run), operation=operation,
        threads=int(threads), loops=int(loops), n=count, errors=errors,
        mean=statistics.mean(values), p95=quantile(.95), p99=quantile(.99), maximum=max(values),
        rps=count * 1000 / (end-start),
        ok40=100 * sum(s['success']=='true' and int(s['elapsed'])<=40 for s in samples) / count,
        peak_threads=max(int(s['allThreads']) for s in samples), duration=(end-start)/1000,
        start=start, path=str(path.relative_to(ROOT)),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
assert len(rows)==54 and sum(r['n'] for r in rows)==93600
assert sum(r['errors'] for r in rows)==0
# The archived r1 files must match the existing submission byte for byte.
legacy = {hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'results/实验数据/原始数据').rglob('*.jtl')}
assert all(r['sha256'] in legacy for r in rows if r['run']==1)
(OUT/'统计结果.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'SHA256清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'三轮逐组统计.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('54 runs, 93600 samples; 0 assertion failures; 18 original r1 hashes match; '
      + str(sum(r['ok40']>=80 for r in rows)) + '/54 runs meet the selected 80% within-40ms criterion.')
