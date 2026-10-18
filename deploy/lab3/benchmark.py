"""Run the paired experiment from the trusted Windows host; credentials stay outside Git."""
import csv, json, time, random, threading, urllib.request, urllib.parse
from remote import ROOT, EVIDENCE, run, get

REMOTE = '/root/lab3-results/comparison-20261018'
BACKUP = '/root/backups/20261018-lab3-comparison'
IMAGE = 'xmu-javaee/productdemoaop:lab3-comparison-20261018'
BASE_COUNT, BASE_MAX = 3913, 5609
MONITOR = 'http://127.0.0.1:19090'
stop_heartbeat = threading.Event()
heartbeat_failed = threading.Event()

def record(name, data):
    target = EVIDENCE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')

def checked(node, command, key, timeout=180):
    result = run(node, command, timeout)
    record('logs/' + key + '.json', dict(time=time.time(), command=command, **result))
    if result['exit']:
        raise RuntimeError(f'{key}: exit {result["exit"]}: {result["stderr"][-800:]}')
    return result['stdout']

def sql(statement, key):
    assert statement.isascii()
    command = """CID=$(docker ps -q --filter name=lab_mysql | head -1)
docker exec -i "$CID" sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N oomall_lab3' <<'LAB3SQL'
""" + statement + '\nLAB3SQL\n'
    return checked(2, command, key)

def reset_data(key):
    # Remove only benchmark-created rows in the dedicated database.
    value = sql("DELETE FROM goods_product WHERE id > 5609 AND barcode='lab3-comparison';\n"
                "SELECT COUNT(*),MAX(id) FROM goods_product;", key + '-reset').strip()
    if value != f'{BASE_COUNT}\t{BASE_MAX}':
        raise RuntimeError('Baseline mismatch: ' + value)
    sql('ALTER TABLE goods_product AUTO_INCREMENT=5610;', key + '-sequence')

def api(path, **params):
    url = MONITOR + '/api/v1/' + path + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        result = json.load(response)
    if result['status'] != 'success': raise RuntimeError('Prometheus query failed')
    return result

def assert_monitoring():
    result = api('targets')
    targets = result['data']['activeTargets']
    if len(targets) != 6 or any(t['health'] != 'up' for t in targets):
        raise RuntimeError('Monitoring is not entirely UP')
    return result

def heartbeat():
    while not stop_heartbeat.is_set():
        try:
            result = run(1, 'touch ' + BACKUP + '/heartbeat', 30)
            if result['exit']: raise RuntimeError('heartbeat failed')
        except Exception:
            heartbeat_failed.set()
            return
        stop_heartbeat.wait(15)

def deploy(profile, block, database='oomall_lab3'):
    print('DEPLOY', block, profile, database, flush=True)
    checked(1, f'APP_IMAGE={IMAGE} PERSISTENCE={profile} LAB_DATABASE={database} '
            f'LAB3_BLOCK={block} bash /root/spring-fundamentals/deploy/lab3/deploy.sh', block + '-deploy')
    deadline = time.time() + 180
    while time.time() < deadline:
        result = run(1, "CID=$(docker ps -q --filter name=lab_productdemoaop | head -1); "
            "docker inspect \"$CID\" --format '{{range .Config.Env}}{{println .}}{{end}}' "
            "| grep '^LAB3_BLOCK='; curl -sf http://127.0.0.1:8080/actuator/health; "
            "curl -sf http://127.0.0.1:8080/actuator/prometheus "
            "| grep '^jvm_threads_live_threads'", 30)
        text = result['stdout']
        if f'LAB3_BLOCK={block}' in text and '"UP"' in text and f'persistence="{profile}"' in text:
            record('logs/' + block + '-ready.json', result)
            time.sleep(10)
            return
        time.sleep(5)
    raise RuntimeError('Application did not become ready: ' + block)

def case(profile, repeat, operation, threads, kind='formal', duration=35):
    name = f'{profile}-r{repeat}-{operation}-t{threads}-{kind}'
    if heartbeat_failed.is_set(): raise RuntimeError('Recovery heartbeat lost')
    if checked(1, "docker inspect demo --format '{{.State.Running}}'", name+'-demo').strip() != 'false':
        raise RuntimeError('Demo running during benchmark')
    reset_data(name)
    record('runs/' + name + '/targets-before.json', assert_monitoring())
    timed = kind != 'example'
    ramp, loops = (5,-1) if timed else (10,1)
    before = time.time()
    print('RUN', name, flush=True)
    checked(3, f'bash /root/spring-fundamentals/deploy/lab3/run-comparison-case.sh '
            f'{operation} {threads} {ramp} {loops} {duration} {str(timed).lower()} {name}',
            name + '-execution', duration + 120)
    after = time.time()
    directory = EVIDENCE / 'runs' / name
    directory.mkdir(parents=True, exist_ok=True)
    for filename in ['samples.jtl', 'jmeter.log', 'console.log', 'start.txt', 'end.txt']:
        get(3, f'{REMOTE}/{name}/{filename}', directory/filename)
    with (directory/'samples.jtl').open(encoding='utf8') as stream:
        rows = list(csv.DictReader(stream))
    if not rows: raise RuntimeError('No samples in ' + name)
    begin = min(int(r['timeStamp']) for r in rows)/1000
    end = max(int(r['timeStamp'])+int(r['elapsed']) for r in rows)/1000
    successes = sum(r['success']=='true' for r in rows)
    ids = [r['response_id'] for r in rows if r['success']=='true']
    counts = sql(f"SELECT COUNT(*),MAX(id) FROM goods_product;\n"
                 f"SELECT COUNT(*) FROM goods_product WHERE name LIKE 'LAB3-{name}-%';", name+'-database')
    actual_count = int(counts.splitlines()[0].split('\t')[0])
    write_count = int(counts.splitlines()[1])
    if operation == 'WriteProduct':
        if write_count != successes or actual_count != BASE_COUNT+successes or len(set(ids)) != successes:
            raise RuntimeError('Write integrity mismatch: ' + name)
    elif actual_count != BASE_COUNT:
        raise RuntimeError('Read modified data: ' + name)
    metadata = dict(name=name, profile=profile, repeat=repeat, operation=operation,
        threads=threads, ramp=ramp, loops=loops, duration=duration, kind=kind,
        command_start=before, command_end=after, start=begin, end=end,
        samples=len(rows), successful=successes, errors=len(rows)-successes,
        baseline_count=BASE_COUNT, final_count=actual_count,
        unique_response_ids=len(set(ids)), write_count=write_count)
    record('runs/'+name+'/metadata.json', metadata)
    time.sleep(6)
    metrics = ['spring:jvm_threads_live_threads', 'node:cpu_usage_percent', 'node:memory_usage_percent',
        'jvm_memory_used_bytes{area="heap"}', 'jvm_gc_pause_seconds_count', 'jvm_gc_pause_seconds_sum',
        'process_cpu_usage', 'up', 'rate(node_disk_read_bytes_total[15s])',
        'rate(node_disk_written_bytes_total[15s])', 'rate(node_network_receive_bytes_total{device!="lo"}[15s])',
        'rate(node_network_transmit_bytes_total{device!="lo"}[15s])']
    for index, query in enumerate(metrics):
        record(f'runs/{name}/prometheus-{index:02d}.json',
            dict(query=query,response=api('query_range',query=query,start=begin-10,end=end+5,step=5)))
    record('runs/'+name+'/targets-after.json', assert_monitoring())
    if checked(1, "docker inspect demo --format '{{.State.Running}}'", name+'-demo-after').strip() != 'false':
        raise RuntimeError('Demo restarted during run')
    if kind=='example' and len(rows) != threads: raise RuntimeError('Example user count mismatch')
    print('DONE', name, 'samples', len(rows), 'errors', len(rows)-successes, flush=True)
    if len(rows)-successes > max(5, len(rows)*.05): raise RuntimeError('Error rate exceeds 5%')
    return metadata

def main():
    if (EVIDENCE/'experiment-started.json').exists():
        raise RuntimeError('Already started. Preserve evidence and explicitly resume instead.')
    original_demo = checked(1,"docker inspect demo --format '{{.State.Running}}'",'demo-original').strip()=='true'
    record('experiment-started.json', dict(time=time.time(),demo_was_running=original_demo,
        design='2 frameworks x 2 APIs x 3 concurrency levels x 3 repeats; 35s, 5s ramp; plus four 1000/10/1 examples'))
    results=[]
    try:
        if original_demo:
            checked(1, """touch /root/backups/20261018-lab3-comparison/heartbeat
nohup bash -c 'while test -f /root/backups/20261018-lab3-comparison/heartbeat; do
  age=$(( $(date +%s) - $(stat -c %Y /root/backups/20261018-lab3-comparison/heartbeat) ))
  if [ "$age" -gt 180 ]; then docker start demo; date -Is; exit; fi
  sleep 15
done' > /root/backups/20261018-lab3-comparison/recovery-watchdog.log 2>&1 < /dev/null &
docker stop -t 30 demo""", 'demo-stop')
        threading.Thread(target=heartbeat,daemon=True).start()
        for repeat in [1,2,3]:
            profiles=['jpa','mybatis'] if repeat%2 else ['mybatis','jpa']
            workload=[(op,n) for n in [10,50,100] for op in ['ReadProduct','WriteProduct']]
            random.Random(20261018+repeat).shuffle(workload)
            for profile in profiles:
                deploy(profile,f'{profile}-r{repeat}')
                for op in ['ReadProduct','WriteProduct']: case(profile,repeat,op,10,'warmup',20)
                for op,n in workload:
                    results.append(case(profile,repeat,op,n))
                    record('completed-runs.json',results)
                if repeat==3:
                    for op in ['ReadProduct','WriteProduct']:
                        results.append(case(profile,repeat,op,1000,'example',20))
                        record('completed-runs.json',results)
        reset_data('experiment-final')
        record('experiment-complete.json',dict(time=time.time(),runs=len(results)))
    finally:
        try:
            deploy('jpa','restored','oomall_demo')
        finally:
            if original_demo: checked(1,'docker start demo','demo-restore')
            stop_heartbeat.set()
            checked(1,'unlink '+BACKUP+'/heartbeat','heartbeat-stop')
            record('restored.json',dict(time=time.time(),demo_was_running=original_demo))

if __name__=='__main__':
    main()

