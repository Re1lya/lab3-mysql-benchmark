"""Local orchestration helpers. Credentials are supplied only through the environment."""
import os, json, pathlib, datetime
import paramiko

HOSTS = {int(k): v for k, v in json.loads(os.environ['LAB3_HOSTS_JSON']).items()}
ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'output/playwright/lab3-comparison-20261018'

def connect(node):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTS[node], username=os.environ['SSH_USER'], password=os.environ['SSH_PASS'],
                   timeout=25, look_for_keys=False, allow_agent=False)
    return client

def run(node, command, timeout=120):
    client = connect(node)
    try:
        _, out, err = client.exec_command(command, timeout=timeout)
        # Commands must keep stdout/stderr bounded; long jobs redirect to remote log files.
        stdout = out.read().decode('utf8', 'replace')
        stderr = err.read().decode('utf8', 'replace')
        return dict(node=node, exit=out.channel.recv_exit_status(), stdout=stdout, stderr=stderr)
    finally:
        client.close()

def capture(node, key, command, timeout=120):
    result = run(node, command, timeout)
    directory = EVIDENCE / 'logs'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / (key + '.json')).write_text(json.dumps(dict(
        time=datetime.datetime.now().astimezone().isoformat(), command=command, **result),
        ensure_ascii=False, indent=2), encoding='utf8')
    print(key, json.dumps(result, ensure_ascii=False), flush=True)
    return result

def put(node, local, remote):
    client = connect(node)
    try:
        with client.open_sftp() as sftp:
            sftp.put(str(local), remote)
    finally:
        client.close()

def get(node, remote, local):
    pathlib.Path(local).parent.mkdir(parents=True, exist_ok=True)
    client = connect(node)
    try:
        with client.open_sftp() as sftp:
            sftp.get(remote, str(local))
    finally:
        client.close()
