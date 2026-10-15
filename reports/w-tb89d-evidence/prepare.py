"""Fix a bounded selection before any model trial; retain every command output."""
import ast, datetime, hashlib, json, pathlib, secrets, subprocess

repo = pathlib.Path(__file__).resolve().parents[2]
packet = repo / 'reports/w-tb89d-evidence'
root = pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
def write(name, value):
    with (packet / name).open('x') as f:
        json.dump(value, f, indent=2); f.write('\n')
def capture(name, argv):
    r = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=60)
    write(name+'.json', dict(argv=argv, returncode=r.returncode, stdout=r.stdout, stderr=r.stderr))
    return r
inventory = json.loads((packet/'inventory.json').read_text())
# Purposeful surface coverage, chosen without any new task result or reference solution.
checks = {
    'log-summary-date-ranges': 'command -v bash; command -v apt-get; command -v sh; command -v python3; test -d /app/logs; test -n "$(find /app/logs -type f -name \*.log -print -quit)"',
    'write-compressor': 'command -v bash; command -v apt-get; command -v sh; command -v gcc; test -s /app/decomp.c; test -x /app/decomp; test -s /app/data.txt',
    'gcode-to-text': 'command -v bash; command -v apt-get; command -v sh; command -v python3; test -s /app/text.gcode',
    'git-multibranch': 'command -v bash; command -v apt-get; command -v sh; command -v git; command -v nginx; command -v sshd; command -v curl; command -v openssl; command -v python3; test -s /etc/nginx/sites-available/default; test -s /etc/ssl/certs/nginx-selfsigned.crt; test -s /etc/ssl/private/nginx-selfsigned.key',
    'sqlite-db-truncate': 'command -v bash; command -v apt-get; command -v sh; command -v python3; test -s /app/trunc.db',
}
verified = []
for tid, check in checks.items():
    row = next(r for r in inventory['rows'] if r['task_id'] == tid)
    e = row['environment']
    assert row['image_present'] and not row['missing_source']
    assert e['gpus'] == 0 and not e['mcp_servers'] and e['cpus'] <= 1 and e['memory_mb'] <= 2048
    assert row['agent']['timeout_sec'] <= 900 and row['verifier']['timeout_sec'] <= 900
    td = root / tid
    r = capture('shell-syntax-'+tid, ['bash', '-n', str(td/'tests/test.sh')]); assert r.returncode == 0
    for f in sorted((td/'tests').rglob('*.py')):
        ast.parse(f.read_text(), filename=str(f))
    r = capture('prerequisite-'+tid, ['docker','run','--rm','--pull=never','--network','none','--read-only','--cpus','1','--memory','2048m','--pids-limit','128','--entrypoint','/bin/sh',row['image_id'],'-ec',check])
    assert r.returncode == 0, tid
    verified.append(tid)
for name, url in [('proxy-debian','http://deb.debian.org/debian/dists/bookworm/InRelease'),('proxy-ubuntu','http://archive.ubuntu.com/ubuntu/dists/noble/InRelease'),('proxy-astral','https://astral.sh/uv/0.9.5/install.sh'),('proxy-pypi','https://pypi.org/simple/pytest-json-ctrf/'),('proxy-gitpython','https://pypi.org/simple/gitpython/')]:
    r = capture(name, ['curl','--max-time','30','-x','http://172.17.0.1:17890','-LsS','-o','/dev/null','-w','%{http_code}',url]); assert r.returncode == 0 and r.stdout == '200'
metadata_candidates = [r['task_id'] for r in inventory['rows'] if r['image_present'] and not r['missing_source'] and r['environment'].get('gpus',0)==0 and not r['environment'].get('mcp_servers') and r['environment']['cpus']<=1 and r['environment']['memory_mb']<=2048 and r['agent']['timeout_sec']<=900 and r['verifier']['timeout_sec']<=900]
runroot = pathlib.Path('/tmp') / ('w-tb89d-runs-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4))
runroot.mkdir(exist_ok=False)
write('batch.json', dict(runs_root=str(runroot), selected=verified, selection_rule='Fixed five new surfaces not in the prior 9 measured tasks: date-range log aggregation, constrained compression, G-code interpretation, SSH/Git multi-branch HTTPS deployment and truncated SQLite recovery. Require cached immutable image, complete official verifier sources, shell/Python parse success, read-only network-disabled tool/input existence probes, no GPU/MCP, <=1 CPU/2048 MiB, declared agent/verifier timeouts <=900s; standard uv/pytest bootstrap via documented proxy. All five selected before any model trial; no result-dependent substitution or rerun. Purposeful coverage, not a performance sample.', endpoint='http://127.0.0.1:8002/v1', model='qwen3.5-9b-local', total_serial_tasks=len(verified), metadata_candidates=metadata_candidates, prerequisite_verified=verified, prerequisite_verified_not_selected=[], cached_unselected=inventory['cached_images']-len(verified), note='Only these five have fresh image tool/input prerequisite probes. Other cached/metadata candidates are not certified runnable. Remote bootstrap is checked by host proxy probes and subsequently by actual verifier receipts, not certified offline.'))
print(json.dumps(dict(selected=verified, prerequisite_verified=len(verified), metadata_candidates=len(metadata_candidates), cached_images=inventory['cached_images'], cached_unselected=inventory['cached_images']-len(verified), runs_root=str(runroot)),indent=2))
