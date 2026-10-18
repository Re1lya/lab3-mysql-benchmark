"""Read-only verification after the teacher experiment has restored services."""
import importlib.util
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from remote import ROOT, run

spec = importlib.util.spec_from_file_location('teacher', Path(__file__).with_name('teacher-benchmark.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
commands = {
    1: '''docker node ls
docker stack ls
docker service ls
docker ps -a --format '{{.Names}} {{.Status}}'
docker inspect demo --format 'demo_running={{.State.Running}}'
CID=$(docker ps -q --filter name=lab_productdemoaop | head -1)
docker inspect "$CID" --format 'image={{.Image}}'
curl -sf http://127.0.0.1:8080/actuator/health
curl -sf http://127.0.0.1:8080/actuator/prometheus | grep '^jvm_threads_live_threads'
test ! -f /root/backups/20261018-lab3-teacher/heartbeat && echo recovery_heartbeat_removed''',
    2: '''CID=$(docker ps -q --filter name=lab_mysql | head -1)
docker exec -i "$CID" sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N' <<'SQL'
SELECT 'original_products',COUNT(*) FROM oomall_demo.goods_product;
SELECT 'teacher_products',COUNT(*),MAX(id) FROM oomall_lab3_teacher.goods_product;
SELECT 'teacher_goods',COUNT(*) FROM oomall_lab3_teacher.goods_goods;
SELECT 'teacher_onsale',COUNT(*) FROM oomall_lab3_teacher.goods_onsale;
SELECT 'teacher_auto_increment',AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA='oomall_lab3_teacher' AND TABLE_NAME='goods_product';
SQL'''
}
with ThreadPoolExecutor(2) as pool:
    results = list(pool.map(lambda n: run(n, commands[n]), commands))
assert all(r['exit'] == 0 for r in results)
assert 'demo_running=true' in results[0]['stdout'] and '"UP"' in results[0]['stdout']
assert 'teacher_products\t3912\t5461' in results[1]['stdout']
assert 'original_products\t3913' in results[1]['stdout']
assert 'teacher_auto_increment\t5609' in results[1]['stdout']
targets = m.monitoring()
rules = m.api('rules')
groups = rules['data']['groups']
rr = [r for g in groups for r in g['rules']]
assert len(rr) == 13 and all(r['health'] == 'ok' for r in rr)
assert all(g['interval'] == 30 for g in groups)
summary = dict(time=time.time(), exit=0,
    stdout='\n\n'.join('NODE '+str(r['node'])+'\n'+r['stdout'] for r in results)
    +'\nMonitoring: 6 targets UP; 13 rules OK; both rule groups evaluate every 30 seconds.',
    nodes=results, targets=targets, rules=rules)
(ROOT/'output/playwright/lab3-teacher-20261018/logs/final-verification.json').write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf8')
print(summary['stdout'])
