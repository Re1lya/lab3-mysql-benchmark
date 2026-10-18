import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const ev=path.join(root,'output/playwright/lab3-teacher-20261018');
const d=JSON.parse(fs.readFileSync(path.join(ev,'analysis/results.json'),'utf8'));
const verified=[];
for(const r of d.rows){
 const report=path.join(ev,'reports',r.name,'statistics.json');if(!fs.existsSync(report))continue;
 const j=JSON.parse(fs.readFileSync(report,'utf8')).Total;
 if(j.sampleCount!==r.samples||j.errorCount!==r.errors)throw Error('JMeter count mismatch '+r.name);
 if(Math.abs(j.meanResTime-r.mean_ms)>1e-7)throw Error('JMeter mean mismatch '+r.name);
 if(j.minResTime!==r.min_ms||j.maxResTime!==r.max_ms)throw Error('JMeter range mismatch '+r.name);
 if(Math.abs(j.throughput-r.success_rps)>1e-4)throw Error('JMeter throughput mismatch '+r.name);
 const sha=crypto.createHash('sha256').update(fs.readFileSync(path.join(ev,'runs',r.name,'samples.jtl'))).digest('hex');
 if(sha!==r.jtl_sha256)throw Error('Raw data changed '+r.name);
 verified.push({name:r.name,samples:r.samples,jmeter_mean_ms:j.meanResTime,node_mean_ms:r.mean_ms,
  jmeter_throughput:j.throughput,node_throughput:r.success_rps,sha256:sha});
}
if(d.complete&&(verified.length!==36||d.samples!==18000))throw Error('Incomplete final verification');
const result={time:new Date().toISOString(),verified_runs:verified.length,total_requests:verified.reduce((s,r)=>s+r.samples,0),
 criteria:'Independent Node raw-JTL analysis agrees with JMeter Java dashboard sample/error counts, mean, min/max and throughput; original SHA256 unchanged.',runs:verified};
fs.writeFileSync(path.join(ev,'analysis/independent-verification.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({verified:verified.length,requests:result.total_requests}));
