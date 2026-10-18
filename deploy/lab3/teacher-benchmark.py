"""Teacher fce17e7 JMX/rules, 10-second ramp and one iteration, both profiles."""
import csv,json,time,threading,random,urllib.request,urllib.parse
from remote import ROOT,run,get
EV=ROOT/'output/playwright/lab3-teacher-20261018'
BACK='/root/backups/20261018-lab3-teacher'
REMOTE='/root/lab3-results/teacher-20261018'
IMAGE='xmu-javaee/productdemoaop:lab3-teacher-20261018'
stop=threading.Event();heartbeat_failed=threading.Event()

def save(name,data):
    p=EV/name;p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(p)

def checked(n,cmd,key,timeout=180):
    r=run(n,cmd,timeout);save('logs/'+key+'.json',dict(time=time.time(),command=cmd,**r))
    if r['exit']:raise RuntimeError(key+' failed: '+r['stderr'][-500:])
    return r['stdout']

def api(path,**kw):
    url='http://127.0.0.1:19090/api/v1/'+path+'?'+urllib.parse.urlencode(kw)
    with urllib.request.urlopen(url,timeout=30) as f:d=json.load(f)
    assert d['status']=='success';return d

def monitoring():
    d=api('targets');a=d['data']['activeTargets']
    assert len(a)==6 and all(x['health']=='up' for x in a),[(x['labels'],x['health']) for x in a]
    return d

def sql(statement,key):
    assert statement.isascii()
    return checked(2,"CID=$(docker ps -q --filter name=lab_mysql | head -1); "
        "docker exec -i \"$CID\" sh -c 'MYSQL_PWD=\"$MYSQL_ROOT_PASSWORD\" mysql -uroot -N oomall_lab3_teacher' <<'SQL'\n"+statement+'\nSQL\n',key)

def reset(key):
    v=sql('DELETE FROM goods_product WHERE id>5461; SELECT COUNT(*),MAX(id) FROM goods_product;',key+'-reset').strip()
    assert v=='3912\t5461',v
    sql('ALTER TABLE goods_product AUTO_INCREMENT=5609;',key+'-sequence')

def heartbeat():
    while not stop.is_set():
        try:assert run(1,'touch '+BACK+'/heartbeat',30)['exit']==0
        except Exception:heartbeat_failed.set();return
        stop.wait(15)

def cancelled():
    if (EV/'STOP_REQUESTED').exists():raise RuntimeError('User requested cancellation; retaining evidence')
    if heartbeat_failed.is_set():raise RuntimeError('Recovery heartbeat lost')

def deploy(profile,block,database='oomall_lab3_teacher'):
    print('DEPLOY',profile,block,flush=True)
    checked(1,f'APP_IMAGE={IMAGE} PERSISTENCE={profile} LAB_DATABASE={database} LAB3_BLOCK={block} '
        'bash /root/spring-fundamentals/deploy/lab3/deploy-teacher.sh',block+'-deploy')
    deadline=time.time()+240
    while time.time()<deadline:
        r=run(1,"CID=$(docker ps -q --filter name=lab_productdemoaop | head -1); "
            "docker inspect \"$CID\" --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^LAB3_BLOCK='; "
            "curl -sf http://127.0.0.1:8080/actuator/health; "
            "curl -sf http://127.0.0.1:8080/actuator/prometheus | grep '^jvm_threads_live_threads'",30)
        if f'LAB3_BLOCK={block}' in r['stdout'] and '"UP"' in r['stdout'] and f'persistence="{profile}"' in r['stdout']:
            save('logs/'+block+'-ready.json',r);time.sleep(15);return
        time.sleep(5)
    raise RuntimeError('Application readiness timeout')

def case(profile,repeat,op,threads):
    name=f'{profile}-r{repeat}-{op}-t{threads}'
    cancelled();reset(name)
    assert checked(1,"docker inspect demo --format '{{.State.Running}}'",name+'-demo').strip()=='false'
    save('runs/'+name+'/targets-before.json',monitoring())
    time.sleep(15);cancelled();print('RUN',name,flush=True)
    checked(3,f'bash /root/spring-fundamentals/deploy/lab3/run-teacher-case.sh {op} {threads} 10 1 {name}',name+'-execution',210)
    folder=EV/'runs'/name
    for fn in ['samples.jtl','console.log','jmeter.log','start.txt','end.txt']:get(3,f'{REMOTE}/{name}/{fn}',folder/fn)
    with (folder/'samples.jtl').open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==threads,(name,len(rows))
    success=sum(r['success']=='true' for r in rows)
    begin=min(int(r['timeStamp']) for r in rows)/1000
    end=max(int(r['timeStamp'])+int(r['elapsed']) for r in rows)/1000
    count=sql('SELECT COUNT(*),MAX(id) FROM goods_product; SELECT COUNT(*) FROM goods_product WHERE id>5461;',name+'-database').splitlines()
    final_count=int(count[0].split('\t')[0]);added=int(count[1])
    assert final_count==3912+(success if op=='WriteProduct' else 0)
    assert added==(success if op=='WriteProduct' else 0)
    meta=dict(name=name,profile=profile,repeat=repeat,operation=op,threads=threads,ramp=10,loops=1,
              samples=len(rows),successful=success,errors=len(rows)-success,start=begin,end=end,
              baseline_count=3912,final_count=final_count,write_count=added,
              teacher_commit='fce17e7dd6a204b91bbe89181ad6a30b09aa0270')
    save('runs/'+name+'/metadata.json',meta);time.sleep(12)
    metrics=['spring:jvm_threads_live_threads','node:cpu_usage_percent','node:memory_usage_percent',
             'jvm_memory_used_bytes{area="heap"}','jvm_gc_pause_seconds_count','jvm_gc_pause_seconds_sum',
             'process_cpu_usage','up','rate(node_disk_read_bytes_total[5m])',
             'rate(node_disk_written_bytes_total[5m])','rate(node_network_receive_bytes_total{device!="lo"}[5m])',
             'rate(node_network_transmit_bytes_total{device!="lo"}[5m])']
    for i,q in enumerate(metrics):save(f'runs/{name}/prometheus-{i:02d}.json',dict(query=q,response=api('query_range',query=q,start=begin-15,end=end+10,step=2)))
    save('runs/'+name+'/targets-after.json',monitoring())
    assert checked(1,"docker inspect demo --format '{{.State.Running}}'",name+'-demo-after').strip()=='false'
    if success!=threads:raise RuntimeError(f'{name}: {threads-success} assertion failures')
    print('DONE',name,'samples',len(rows),'errors',threads-success,flush=True)
    return meta

def main():
    if (EV/'experiment-started.json').exists():raise RuntimeError('Already started; do not overwrite data')
    original=checked(1,"docker inspect demo --format '{{.State.Running}}'",'demo-original').strip()=='true'
    results=[]
    save('experiment-started.json',dict(time=time.time(),demo_was_running=original,design='Teacher JMX, 100/400/1000 threads, ramp 10 s, loop 1, both APIs/profiles, 3 repeats'))
    try:
        checked(1,"""touch /root/backups/20261018-lab3-teacher/heartbeat
nohup bash -c 'while test -f /root/backups/20261018-lab3-teacher/heartbeat; do
 age=$(( $(date +%s) - $(stat -c %Y /root/backups/20261018-lab3-teacher/heartbeat) ))
 if [ "$age" -gt 180 ]; then docker start demo; date -Is; exit; fi
 sleep 15
done' > /root/backups/20261018-lab3-teacher/recovery-watchdog.log 2>&1 < /dev/null &
docker stop -t 30 demo""",'demo-stop')
        threading.Thread(target=heartbeat,daemon=True).start()
        for rep in [1,2,3]:
            profiles=['jpa','mybatis'] if rep%2 else ['mybatis','jpa']
            order=[(op,n) for n in [100,400,1000] for op in ['ReadProduct','WriteProduct']]
            random.Random(20261018+rep).shuffle(order)
            for profile in profiles:
                cancelled();deploy(profile,f'teacher-{profile}-r{rep}')
                if rep==1 and profile=='jpa':
                    print('BASELINE_IDLE 300 seconds',flush=True)
                    for _ in range(30):time.sleep(10);cancelled()
                for op,n in order:
                    results.append(case(profile,rep,op,n));save('completed-runs.json',results)
        reset('teacher-final');save('experiment-complete.json',dict(time=time.time(),runs=len(results)))
    finally:
        try:deploy('jpa','teacher-restored','oomall_demo')
        finally:
            if original:checked(1,'docker start demo','demo-restore')
            stop.set();checked(1,'test ! -f '+BACK+'/heartbeat || unlink '+BACK+'/heartbeat','heartbeat-stop')
            save('restored.json',dict(time=time.time(),demo_was_running=original))

if __name__=='__main__':main()
