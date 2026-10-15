"""Read-only fresh task/cache inventory. Never pulls or executes a task."""
import datetime, hashlib, json, pathlib, shutil, subprocess, tomllib

repo = pathlib.Path(__file__).resolve().parents[2]
out = repo / 'reports/w-tb89-evidence'
raw = out / 'inventory'
raw.mkdir(exist_ok=False)
tasks = pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
def capture(name, argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    (raw / (name + '.json')).write_text(json.dumps(dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr), indent=2)+'\n')
    return p
capture('clock', ['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'])
capture('platform-commit', ['git', '-C', str(repo), 'rev-parse', 'HEAD'])
capture('worktrees', ['git', '-C', str(repo), 'worktree', 'list', '--porcelain'])
capture('dataset-commit', ['git', '-C', str(tasks), 'rev-parse', 'HEAD'])
capture('dataset-status', ['git', '-C', str(tasks), 'status', '--short'])
capture('docker-version', ['docker', 'version'])
capture('processes-before', ['ps', '-eo', 'pid,args'])
capture('containers-before', ['docker', 'ps', '-a', '--no-trunc', '--format', '{{json .}}'])
capture('disk-before', ['df', '-B1', '/', '/tmp'])
rows = []
for task in sorted(tasks.glob('*/task.toml')):
    td = task.parent
    meta = tomllib.loads(task.read_text())
    image = meta['environment']['docker_image']
    result = capture('image-' + td.name, ['docker', 'image', 'inspect', image])
    images = json.loads(result.stdout) if result.returncode == 0 else []
    source = raw / 'sources' / td.name
    source.mkdir(parents=True)
    hashes = {}
    for rel in ['task.toml', 'instruction.md', 'environment/Dockerfile'] + [str(p.relative_to(td)) for p in sorted((td/'tests').rglob('*')) if p.is_file()]:
        p = td / rel
        if p.is_file():
            dest = source / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    rows.append(dict(task_id=td.name, image_ref=image, image_id=images[0]['Id'] if images else None, repo_digests=images[0].get('RepoDigests') if images else None, image_present=bool(images), missing_source=[p for p in ['task.toml','instruction.md','environment/Dockerfile','tests/test.sh','tests/test_outputs.py'] if not (td/p).is_file()], environment=meta['environment'], verifier=meta['verifier'], source_hashes=hashes))
summary = dict(task_references=len(rows), cached=sum(r['image_present'] for r in rows), absent=[r['task_id'] for r in rows if not r['image_present']], rows=rows)
(out/'inventory.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='rows'}, indent=2))
