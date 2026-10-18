"""Render real recorded outputs into clearly labelled evidence pages."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'output/playwright/lab3-teacher-20261018'
style='body{font:17px Consolas,monospace;margin:30px;color:#17243a;background:#f5f7fa}h1{font:26px Arial}p{font:16px Arial}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #ccd5df;padding:20px;line-height:1.45}a{color:#154c8b}'
for filename in ['tests-final','teacher-database-init','image-loaded','teacher-monitoring-reload','teacher-environment-node1','teacher-environment-node3','final-verification']:
 p=EV/'logs'/(filename+'.json')
 if not p.exists():continue
 d=json.loads(p.read_text(encoding='utf8'));content=d.get('stdout',json.dumps(d,ensure_ascii=False,indent=2))
 text=f'<html><meta charset="utf-8"><style>{style}</style><h1>Lab 3 teacher version — {html.escape(filename)}</h1><p>Real recorded output rendered as a page. This is not a native terminal screenshot.</p><p>Source: logs/{filename}.json · exit {d.get("exit","see JSON")}</p><pre>{html.escape(content)}</pre></html>'
 (EV/'pages'/(filename+'.html')).write_text(text,encoding='utf8')
lines=['Teacher commit: fce17e7dd6a204b91bbe89181ad6a30b09aa0270','Original teacher file SHA-256:']
for k,v in json.loads((EV/'teacher-source-hashes.json').read_text()).items():lines.extend([k,v])
lines+=['','Only execution fixes in adapted JMX: host IP; write ramp property spelling; output path.','Teacher payload, assertions and one-iteration semantics retained.','Teacher run: -Jthread.num=1000 -Jrampup.period=10 -Jloop.count=1']
(EV/'pages/teacher-source.html').write_text(f'<html><meta charset="utf-8"><style>{style}</style><h1>Teacher source provenance</h1><p>Recorded source hashes and adaptation notes.</p><pre>{html.escape(chr(10).join(lines))}</pre></html>',encoding='utf8')
items=[]
for p in sorted((EV/'pages').glob('*.html')):items.append(f'<li><a href="pages/{p.name}">{p.stem}</a></li>')
if (EV/'completed-runs.json').exists():
 for m in json.loads((EV/'completed-runs.json').read_text()):
  name=m['name'];items.append(f'<li>{name}: {m["samples"]} samples, {m["errors"]} errors — <a href="reports/{name}/index.html">JMeter HTML</a> | <a href="runs/{name}/samples.jtl">raw JTL</a></li>')
(EV/'index.html').write_text(f'<html><meta charset="utf-8"><style>{style}</style><h1>Lab 3 teacher-version evidence</h1><p>Final experiment uses teacher fce17e7 JMX and recording rules. Earlier exploratory data is excluded.</p><ul>'+''.join(items)+'</ul></html>',encoding='utf8')
print('Evidence pages updated')
