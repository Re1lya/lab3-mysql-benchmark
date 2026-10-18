// Standard-library analysis of unmodified teacher-plan JTL files.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const EV=path.join(ROOT,'output/playwright/lab3-teacher-20261018');
const OUT=path.join(EV,'analysis');fs.mkdirSync(OUT,{recursive:true});
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sd=a=>a.length<2?0:Math.sqrt(a.reduce((s,x)=>s+(x-mean(a))**2,0)/(a.length-1));
const quantile=(a,p)=>{let x=[...a].sort((x,y)=>x-y),i=(x.length-1)*p,j=Math.floor(i);return x[j]+(x[Math.ceil(i)]-x[j])*(i-j);};
function csv(text){
 let rows=[],row=[],field='',quoted=false;
 for(let i=0;i<text.length;i++){
  const c=text[i];
  if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}
  else if(c===','&&!quoted){row.push(field);field='';}
  else if(c==='\n'&&!quoted){row.push(field.replace(/\r$/,''));rows.push(row);row=[];field='';}
  else field+=c;
 }
 if(quoted)throw Error('Unclosed CSV quote');
 if(field||row.length){row.push(field);rows.push(row);}
 const head=rows.shift();return rows.filter(r=>r.length>1).map(r=>{
  if(r.length!==head.length)throw Error('CSV column mismatch');
  return Object.fromEntries(head.map((h,i)=>[h,r[i]]));
 });
}
const roles={'172.31.1.202:9100':'app','172.31.8.46:9100':'mysql','172.31.12.156:9100':'jmeter','172.31.1.19:9100':'prometheus'};
const meta=read(path.join(EV,'completed-runs.json'));
const rows=[],plots=[];
for(const m of meta){
 const folder=path.join(EV,'runs',m.name),raw=fs.readFileSync(path.join(folder,'samples.jtl'));
 const samples=csv(raw.toString('utf8'));
 const elapsed=samples.map(s=>Number(s.elapsed));
 const start=Math.min(...samples.map(s=>Number(s.timeStamp)))/1000;
 const end=Math.max(...samples.map(s=>Number(s.timeStamp)+Number(s.elapsed)))/1000;
 const success=samples.filter(s=>s.success==='true').length;
 if(samples.length!==m.samples||success!==m.successful||m.samples!==m.threads*m.loops)throw Error('Sample count mismatch '+m.name);
 if(m.final_count!==3912+(m.operation==='WriteProduct'?success:0))throw Error('Database count mismatch');
 const r={...m,wall_seconds:end-start,success_rps:success/(end-start),error_pct:100*(samples.length-success)/samples.length,
  mean_ms:mean(elapsed),min_ms:Math.min(...elapsed),max_ms:Math.max(...elapsed),
  p50_ms:quantile(elapsed,.5),p90_ms:quantile(elapsed,.9),p95_ms:quantile(elapsed,.95),p99_ms:quantile(elapsed,.99),
  peak_active_threads:Math.max(...samples.map(s=>Number(s.allThreads))),
  mean_connect_ms:mean(samples.map(s=>Number(s.Connect))),mean_ttfb_ms:mean(samples.map(s=>Number(s.Latency))),
  jtl_sha256:crypto.createHash('sha256').update(raw).digest('hex'),http_codes:JSON.stringify(samples.reduce((a,s)=>(a[s.responseCode]=(a[s.responseCode]||0)+1,a),{}))};
 const monitoring={};
 for(const [index,metric] of [[0,'threads'],[1,'cpu_pct'],[2,'memory_pct']]){
  for(const series of read(path.join(folder,`prometheus-${String(index).padStart(2,'0')}.json`)).response.data.result){
   if(index===0&&series.metric.persistence!==m.profile)continue;
   const role=index===0?'app':roles[series.metric.instance];if(!role)continue;
   const selected=series.values.filter(([t,v])=>t>=start&&t<=end&&Number.isFinite(Number(v)));
   const values=selected.map(([t,v])=>Number(v));if(!values.length)continue;
   r[`${role}_${metric}_mean`]=mean(values);r[`${role}_${metric}_max`]=Math.max(...values);r[`${role}_${metric}_points`]=values.length;
   monitoring[`${role}_${metric}`]=series.values.map(([t,v])=>[t-start,Number(v)]);
  }
 }
 rows.push(r);
 plots.push({name:m.name,profile:m.profile,operation:m.operation,threads:m.threads,repeat:m.repeat,
  response:samples.map(s=>[(Number(s.timeStamp)/1000-start),Number(s.elapsed),Number(s.allThreads)]),monitoring});
}
const grouped=new Map();
for(const r of rows){const k=[r.profile,r.operation,r.threads].join('|');if(!grouped.has(k))grouped.set(k,[]);grouped.get(k).push(r);}
const groups=[];
const metrics=['success_rps','mean_ms','p50_ms','p90_ms','p95_ms','p99_ms','peak_active_threads','app_cpu_pct_mean','mysql_cpu_pct_mean','jmeter_cpu_pct_mean','prometheus_cpu_pct_mean','app_memory_pct_mean','mysql_memory_pct_mean','jmeter_memory_pct_mean','prometheus_memory_pct_mean','app_threads_mean'];
for(const values of grouped.values()){
 const {profile,operation,threads}=values[0];const g={profile,operation,threads,repeats:values.length,samples:values.reduce((s,r)=>s+r.samples,0),errors:values.reduce((s,r)=>s+r.errors,0)};
 for(const metric of metrics){const a=values.map(r=>r[metric]).filter(Number.isFinite);if(!a.length)continue;
  g[metric+'_mean']=mean(a);g[metric+'_sd']=sd(a);g[metric+'_min']=Math.min(...a);g[metric+'_max']=Math.max(...a);
 }
 groups.push(g);
}
groups.sort((a,b)=>a.operation.localeCompare(b.operation)||a.threads-b.threads||a.profile.localeCompare(b.profile));
function writeCSV(file,records){
 if(!records.length)return;const cols=[...new Set(records.flatMap(Object.keys))];
 const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';
 fs.writeFileSync(file,'\ufeff'+[cols,...records.map(r=>cols.map(k=>r[k]))].map(r=>r.map(quote).join(',')).join('\r\n')+'\r\n','utf8');
}
const result={teacher_commit:'fce17e7dd6a204b91bbe89181ad6a30b09aa0270',completed:rows.length,
 samples:rows.reduce((s,r)=>s+r.samples,0),errors:rows.reduce((s,r)=>s+r.errors,0),
 complete:rows.length===36&&fs.existsSync(path.join(EV,'experiment-complete.json')),rows,groups};
fs.writeFileSync(path.join(OUT,'results.json'),JSON.stringify(result,null,2));
fs.writeFileSync(path.join(OUT,'plot-data.json'),JSON.stringify(plots));
writeCSV(path.join(OUT,'all-runs.csv'),rows);writeCSV(path.join(OUT,'group-summary.csv'),groups);
console.log(JSON.stringify({completed:result.completed,samples:result.samples,errors:result.errors,complete:result.complete}));
