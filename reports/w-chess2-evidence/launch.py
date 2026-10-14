"""One authorized released-task diagnostic via the documented trusted-caller API.

No patched loaders, gates, harness, controller, scorer or reference data.
This script is an observer/orchestrator, never an admission attestation.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ckpt.git_state import stage_workspace, content_sha
from data.datasets import chessbench_puzzles as chess
from eval.containers import sandbox
from eval.policy import diagnostic_policy as policy
from eval.policy.unobserved_diagnostic import Authorization
from eval.run.integrity import snapshot, diff
from eval.run.runner import run_one


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sampling', choices=['diagnostic'], required=True)
    ap.add_argument('--rounds', type=int, required=True)
    ap.add_argument('--trials', type=int, required=True)
    ap.add_argument('--jobs', type=int, required=True)
    ap.add_argument('--authorize-unobserved-diagnostic', required=True)
    args = ap.parse_args()
    policy.staged_task_set([], args.sampling, rounds=args.rounds,
                           trials=args.trials, jobs=args.jobs)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_id = 'w-chess2-stepwise-' + stamp + '-' + secrets.token_hex(4)
    run = policy.reserve_run_directory(ROOT / 'runs', run_id)
    work_root = Path('/tmp') / (run_id + '-work')
    work_root.mkdir(exist_ok=False)
    workspace = work_root / run_id / 'workspace'
    workspace.parent.mkdir(exist_ok=False)
    launch = run / 'launch'
    launch.mkdir()

    def write(name, value):
        with (run / name).open('x') as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.write('\n')

    write('identity.json', dict(run_id=run_id, run_dir=str(run), work_root=str(work_root),
                               workspace=str(workspace), caller='eval.run.runner.run_one',
                               side='train', harness='codex_agent'))
    print(json.dumps(dict(run_id=run_id, run_dir=str(run))), flush=True)
    shutil.copy2(__file__, launch / 'launch.py')
    (launch / 'command.txt').write_text(shlex.join(['env'] + [
        f'{key}={os.environ[key]}' for key in (
            'HG_EGRESS_PROXY', 'HG_AGENT_BACKEND', 'HG_AGENT_MODEL',
            'HG_AGENT_BASE_URL', 'HG_AGENT_API_KEY', 'HG_AGENT_CODEX_COMMAND')]
        + ['python3', str(Path(__file__).resolve()), *sys.argv[1:]]) + '\n')
    assert os.environ['HG_AGENT_BASE_URL'] == 'http://127.0.0.1:8002/v1'
    assert os.environ['HG_AGENT_MODEL'] == 'qwen3.5-9b-local'
    assert os.environ['HG_AGENT_BACKEND'] == 'openai'
    with urllib.request.urlopen(os.environ['HG_AGENT_BASE_URL'] + '/models', timeout=15) as r:
        models = json.load(r)
        write('launch/endpoint.json', dict(url=r.url, status=r.status, models=models))
        assert r.status == 200 and any(m['id'] == os.environ['HG_AGENT_MODEL'] for m in models['data'])

    # Count released rows without deriving unselected boards or reference lines.
    assert sha(chess.CSV_PATH) == chess.CSV_SHA256
    with chess.CSV_PATH.open(newline='') as f:
        pool = [f'chessbench_puzzles/test/{i}' for i, _ in enumerate(csv.DictReader(f))]
    eligible = [tid for tid in pool if not chess.base.is_eval(tid)]
    selected = policy.staged_task_set(eligible, args.sampling, trials=args.trials,
                                     jobs=args.jobs, rounds=args.rounds)
    record = chess.control_task(selected[0])
    tasks, _ = chess.load_selected(selected)
    task = dict(tasks[0], interaction=chess.STEPWISE_CONTRACT)
    setup, verifier = chess.setup_for(record), chess.verify_for(record)
    auth = Authorization(run_id, selected[0], args.authorize_unobserved_diagnostic)
    auth.require_scope(run_id, selected, trials=args.trials, jobs=args.jobs, round_no=args.rounds)
    env = dict(chess.DEFAULT_ENV)
    write('launch/selection.json', dict(pool_tasks=len(pool), eligible_tasks=len(eligible),
        eligible_task_ids_sha256=policy.eligible_digest(eligible), selected_task_ids=selected,
        split_rule='data.scaffolds.qa.base.is_eval: sha256(task_id)[0] % 3 == 0',
        split_source='hash', official_payload_split='test',
        split_sha256=policy.receipt_digest(dict(train=eligible, eval=[t for t in pool if chess.base.is_eval(t)]))))
    write('launch/task.json', task)
    write('launch/source.json', dict(path=str(chess.CSV_PATH), sha256=sha(chess.CSV_PATH),
        expected_sha256=chess.CSV_SHA256, revision=chess.REVISION,
        adapter_sha256=sha(chess.__file__), model_weights_sha256=None))
    stage_workspace(ROOT / 'base_harness/codex_agent', workspace)
    files = {str(p.relative_to(workspace)): sha(p) for p in sorted(workspace.rglob('*'))
             if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}
    write('launch/harness-files.json', files)
    write('launch/manifest.json', dict(run_id=run_id, selected_task_ids=selected,
        task_sha256=sha(launch / 'task.json'), source_sha256=sha(launch / 'source.json'),
        harness_files_sha256=sha(launch / 'harness-files.json'),
        platform_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        protocol=chess.STEPWISE_CONTRACT, endpoint=os.environ['HG_AGENT_BASE_URL'],
        model=os.environ['HG_AGENT_MODEL'], actor_command=os.environ['HG_AGENT_CODEX_COMMAND'], env=env, timeout_s=300,
        rounds=args.rounds, trials=args.trials, jobs=args.jobs, work_root=str(work_root)))
    context = dict(dataset='chessbench_puzzles', side='train',
        metric=dict(name='ChessBench puzzle accuracy', scorer_sha256=sha(chess.__file__)),
        hashes=dict(source=sha(chess.CSV_PATH), split=json.loads((launch / 'selection.json').read_text())['split_sha256'],
                    manifest=sha(launch / 'manifest.json'), model=None, harness=sha(launch / 'harness-files.json')),
        endpoint=os.environ['HG_AGENT_BASE_URL'],
        limits=dict(resource=dict(agent_timeout_s=300, verifier_timeout_s=verifier['timeout_s']), budget=None),
        gates=dict(status='unknown', receipt_sha256=None,
                   detail='Explicit operator authorization for one diagnostic; shared scorer/export gates and backend observations remain unresolved.'),
        comparability_notes=[
            'Only chessbench_puzzles.stepwise.v1; no offline strict-replay evaluation or mixed point.',
            'Hash-train side selected before payload decoding; released CSV test slice has no official study split. No method tuning or improvement.',
            'Raw controller measurement is distinct from policy publication. Unknown model-weight digest, transitive dependency closure, CPU/memory enforcement and spend budget; no comparison, expansion or production authorization.'])
    policy.validate_context(context)
    write('launch/policy-input.json', dict(context=context, authorization=auth.record()))
    unknown = dict(status='unknown', receipt_sha256=None,
                   detail='No verified lifecycle admission receipt; not attested by this observer.')

    def receipt(result=None):
        return policy.build_receipt(run_id=run_id, stage=args.sampling, eligible=eligible,
            selected=selected, context=context,
            outcomes=policy.evaluation_outcomes(result, selected) if result is not None else [],
            cleanup=unknown, snapshot=unknown, enforcement=auth.record())

    policy.write_receipt(run / 'staged_plan.json', receipt())
    check = sandbox.self_check(ROOT, work_root)
    write('launch/sandbox-preflight.json', check)
    if not check['ok']:
        write('refusal.json', dict(stage='sandbox preflight', detail=check['detail']))
        normalized = dict(trials=1, invalid={selected[0]: dict(stage='sandbox preflight', detail=check['detail'])})
        policy.write_receipt(run / 'diagnostic_receipt.json', receipt(normalized))
        return 2
    os.environ['HARNESSGRAD_WORK_ROOT'] = str(work_root)
    before = snapshot(ROOT)
    write('launch/platform-before.json', before)
    result = run_one(workspace, task, sandbox=True, setup=setup, verifier=verifier,
                     env=env, timeout_s=300, run_id=run_id, run_seed=run_id,
                     recordings_root=run / 'recordings', diagnostic_authorization=auth)
    write('task-result.json', result)
    write('launch/platform-diff.json', diff(before, snapshot(ROOT)))
    # Feed the policy's existing outcome conversion observed facts, never inferred zeros.
    normalized = dict(trials=1, verdicts={selected[0]: result.get('verdict', {})},
        harness_output={selected[0]: dict(exit_code=result.get('exit_code'))},
        tampered=json.loads((launch / 'platform-diff.json').read_text()))
    if result.get('invalid'):
        normalized['invalid'] = {selected[0]: result['invalid']}
    if 'score' in (result.get('verdict') or {}):
        normalized['per_task'] = {selected[0]: result['verdict']['score']}
    write('outcome-input.json', normalized)
    policy.write_receipt(run / 'diagnostic_receipt.json', receipt(normalized))
    write('launch/harness-after.json', dict(content_sha=content_sha(workspace),
        status=subprocess.check_output(['git', '-C', str(workspace), 'status', '--short'], text=True)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
