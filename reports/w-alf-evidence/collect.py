"""Read preserved artifacts; copy receipts and summarize passive observations."""
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RAW = OUT / 'runtime-attempt'
identity = json.loads((RAW/'identity.json').read_text())
RUN = Path(identity['run_dir'])
WORK = Path(identity['work_root'])


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, value):
    with (OUT/name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


# Preserve the entire original launch evidence before creating review summaries.
archive = WORK / 'w-alf-original-evidence.tar.gz'
with tarfile.open(archive, 'x:gz') as f:
    f.add(OUT, arcname='launch-evidence')
    f.add(RUN, arcname='execution')
write('external-archive.json', dict(path=str(archive), sha256=sha(archive),
    note='Contains original observer streams and selected payload; retained outside git.'))
shutil.copytree(RUN, OUT/'execution')
selection = json.loads((RAW/'selection.json').read_text())
spec = selection['verifier']
spec['inputs'] = [dict(path=v['path'], **({'from': v['from']} if 'from' in v else
    {'content_sha256': hashlib.sha256(v['content'].encode()).hexdigest(),
     'note': 'inline selected game content omitted from git'})) for v in spec['inputs']]
write('selection-summary.json', selection)
calls = json.loads((RAW/'call-observations.json').read_text())
launches = [v for v in calls if v['event']=='subprocess.run' and '--' in v['args'][0]
            and any('hg-task-' in str(a) for a in v['args'][0])]
rows = []
for v in launches:
    argv = v['args'][0]
    # Preserve mount/command flags; omit unrelated --setenv triples from review copy.
    clean = []
    omitted = []
    i = 0
    while i < len(argv):
        if argv[i] == '--setenv' and argv[i+1] not in (
                'HG_AGENT_DEADLINE_S', 'HG_AGENT_MODEL', 'HG_AGENT_BACKEND',
                'HG_AGENT_BASE_URL', 'HOME', 'TMPDIR', 'HARNESSGRAD_WORK_ROOT'):
            omitted.append(argv[i+1])
            i += 3
        else:
            clean.append(argv[i])
            i += 1
    rows.append(dict(argv=clean, omitted_environment_names=omitted,
                     timeout_s=v['timeout'], deadline_env=v['deadline_env'], cwd=v['cwd']))
write('executed-commands.json', dict(original_path=str(RAW/'call-observations.json'),
      original_sha256=sha(RAW/'call-observations.json'), launches=rows))
processes = json.loads((RAW/'process-observations.json').read_text())
selected = [v for v in processes if '--' in (v.get('argv') or [])
            and any('hg-task-' in str(a) for a in v['argv'])]
for v in selected:
    argv = v['argv']
    v['command_after_bwrap'] = argv[argv.index('--')+1:]
    del v['argv']
    v['scope_note'] = 'Immediate Popen child sample (bwrap), not a later engine PID or peak usage.'
cgroup = {}
cg_path = selected[0]['cgroup'].strip().split(':', 2)[2]
cg_root = Path('/sys/fs/cgroup')
cg = cg_root / cg_path.lstrip('/')
for d in [cg, *cg.parents]:
    for name in ('cpu.max', 'memory.max', 'pids.max', 'cpuset.cpus.effective'):
        p = d/name
        try:
            cgroup[str(p)] = p.read_text()
        except OSError as exc:
            cgroup[str(p)] = {'unavailable': str(exc)}
    if d == cg_root:
        break
write('resource-observations.json', dict(processes=selected,
    cgroup_ancestor_files_sampled_after_execution=cgroup, observed_at_ns=time.time_ns(),
    caveat='No engine-PID/peak-utilization sample; later cgroup reads cannot prove unchanged configuration during execution. No per-task CPU/memory cap proven.'))
copied = RAW/'selected-task-at-verification'
hashes = json.loads((RAW/'source-hashes.json').read_text())
bindings = {}
for name, source in [('check.py', 'data/datasets/alfworld/verify/check.py'),
                     ('gym_env.py', 'data/datasets/alfworld/lib/gym_env.py'),
                     ('alf', 'data/datasets/alfworld/cli/alf')]:
    bindings[name] = dict(observed_sha256=sha(copied/name),
                         launch_source_sha256=hashes[str(ROOT/source)],
                         equal=sha(copied/name)==hashes[str(ROOT/source)])
    assert bindings[name]['equal']
for name in ('evidence.json', 'reward.txt'):
    shutil.copy2(copied/'verifier'/name, OUT/name)
game = json.loads((copied/'game.tw-pddl').read_text())
write('artifact-bindings.json', dict(materialized_inputs=bindings,
    selected_game_sha256=sha(copied/'game.tw-pddl'), walkthrough_present='walkthrough' in game,
    oracle_actions_present=(copied/'.oracle/actions.json').exists(),
    action_log=(copied/'alf_actions.jsonl').read_text(),
    reward_sha256=sha(OUT/'reward.txt'), evidence_sha256=sha(OUT/'evidence.json'),
    copied_original_task_tree=str(copied)))
cleanup = json.loads((RAW/'temporary-cleanup.json').read_text())
write('cleanup-observations.json', dict(temporary_directories=cleanup,
    removal_events=[r for r in calls if r['event']=='shutil.rmtree'],
    process_pids_after=[dict(pid=v['pid'], exists=Path('/proc',str(v['pid'])).exists())
                        for v in selected],
    retained=dict(run_dir=str(RUN), run_exists=RUN.exists(), work_root=str(WORK),
                  work_exists=WORK.exists(), original_evidence_archive=str(archive)),
    note='Observed absence of task/preflight directories; work, run and evidence retained deliberately. Private namespace tmpfs contents and any unobserved engine scratch were not inventoried. Formal driver cleanup/snapshot lifecycle remains unknown.'))
original = json.loads((OUT/'active-drivers-before.json').read_text())
write('import-attempt-process-summary.json', dict(original_path=str(OUT/'active-drivers-before.json'),
    original_sha256=sha(OUT/'active-drivers-before.json'),
    matching_lines=[l for l in original['stdout'].splitlines()
                    if ('driver.py' in l or 'control.py' in l) and 'rg ' not in l]))
original = json.loads((RAW/'active-drivers-before.json').read_text())
write('runtime-attempt-process-summary.json', dict(original_path=str(RAW/'active-drivers-before.json'),
    original_sha256=sha(RAW/'active-drivers-before.json'),
    matching_lines=[l for l in original['stdout'].splitlines()
                    if ('driver.py' in l or 'control.py' in l) and 'rg ' not in l]))
write('receipt-integrity.json', dict(
    run_copy_matches=all(sha(p)==sha(OUT/'execution'/p.relative_to(RUN))
                         for p in RUN.rglob('*') if p.is_file()),
    archive_sha256=sha(archive), scorer_input_bindings_match=all(v['equal'] for v in bindings.values())))
