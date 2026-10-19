"""One local HTTP model loop trial through native run_one, using a named env file.

This is a connectivity/integration diagnostic, not a full benchmark or production
admission. One full conversation is selected by ID hash before model execution.
Raw answers/trace and scorer evidence are local receipts; never publish API keys.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ''):
    sys.path.insert(0, str(ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-steps', type=int, default=12)
    parser.add_argument('--max-output-tokens', type=int, default=8192)
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args(argv)
    if not args.env_file.is_file():
        parser.error('the explicitly selected .env must exist')
    if not 1 <= args.max_steps <= 32 or not 1 <= args.max_output_tokens <= 16384 or not 1 <= args.timeout <= 1800:
        parser.error('diagnostic bounds exceeded')
    from driver import load_env
    from ckpt.git_state import stage_workspace
    from eval.run.runner import run_one
    from eval.run.metrics import diagnostic_task_set
    from data.datasets import locomo
    summarize = locomo._load_asset("report.py").summarize
    loaded = load_env(args.env_file)
    required = ('HG_AGENT_BACKEND', 'HG_AGENT_BASE_URL', 'HG_AGENT_MODEL', 'HG_AGENT_API_KEY')
    if any(not loaded.get(key) for key in required) or loaded['HG_AGENT_BACKEND'] != 'openai':
        parser.error('.env must specify the OpenAI-compatible agent backend, URL, model and key')
    parsed = urlsplit(loaded["HG_AGENT_BASE_URL"])
    if (parsed.scheme != "http" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment):
        parser.error("native offline model route requires a plain HTTP model base URL")
    # This command explicitly promises the selected file's endpoint, not ambient values.
    for key in required:
        os.environ[key] = loaded[key]
    os.environ.update(HG_AGENT_MAX_STEPS=str(args.max_steps), HG_AGENT_MAX_OUTPUT_TOKENS=str(args.max_output_tokens),
                      HG_AGENT_RETRIES='1', HG_AGENT_TIMEOUT_S='120')
    from harnessgrad.config import reset
    reset()
    task_id = diagnostic_task_set(list(locomo.rows()))[0]
    task = locomo.control_task(task_id)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    run_id = 'locomo-api-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    receipt = {'schema': 'hg-locomo-diagnostic-v1', 'run_id': run_id,
               'purpose': 'single-conversation native integration diagnostic',
               'dataset': 'locomo', 'eligible_tasks': len(locomo.rows()), 'selected_tasks': [task_id],
               'selected_questions': len(locomo.rows()[task_id]['qa']), 'trials': 1, 'jobs': 1,
               'model': loaded['HG_AGENT_MODEL'], 'base_url': loaded['HG_AGENT_BASE_URL'],
               'source_sha256': locomo.DATA_SHA256, 'harbor_commit': locomo.HARBOR_COMMIT,
               'metric': locomo.METRIC, 'sandbox': True, 'network': 'none',
               'budget': {'max_steps': args.max_steps, 'max_output_tokens': args.max_output_tokens,
                          'agent_timeout_s': args.timeout, 'provider_retries': 1},
               'harness_sha256': hashlib.sha256((ROOT / 'base_harness/loop/agent.py').read_bytes()).hexdigest(),
               'production_authorized': False, 'comparable_benchmark_result': False}
    (output / 'plan.json').write_text(json.dumps(receipt, indent=2) + '\n')
    work_root = Path(tempfile.mkdtemp(prefix='hg-locomo-diagnostic-'))
    os.environ['HARNESSGRAD_WORK_ROOT'] = str(work_root)
    started = time.monotonic()
    try:
        harness = work_root / 'loop'
        stage_workspace(ROOT / 'base_harness/loop', harness)
        result = run_one(harness, task, setup=locomo.SETUP[task_id], verifier=locomo.VERIFY[task_id],
                         env=locomo.ENV[task_id], sandbox=True, timeout_s=args.timeout,
                         run_id=run_id, run_seed='0')
        # Defensive redaction for exception text; keys never belong to receipts.
        serialized = json.dumps(result, ensure_ascii=False, indent=2)
        for key, value in loaded.items():
            if value and ('KEY' in key or 'TOKEN' in key or 'SECRET' in key):
                serialized = serialized.replace(value, '[REDACTED]')
        (output / 'result.json').write_text(serialized + '\n')
        verdict = result.get('verdict') or {}
        evidence = verdict.get('evidence') or {}
        complete = (result.get('exit_code') == 0 and verdict.get('score') is not None
                    and evidence.get('measured') is True
                    and evidence.get('num_answered') == receipt['selected_questions'])
        receipt.update(completed=complete, exit_code=result.get('exit_code'),
                       answered=evidence.get('num_answered'), score=verdict.get('score'),
                       scorer_isolation_class=verdict.get('scorer_isolation_class'),
                       model_gateway=result.get('model_gateway'))
        if evidence:
            (output / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
            (output / 'report.json').write_text(json.dumps(summarize([evidence], [task_id]), indent=2) + '\n')
        return 0 if complete else 2
    finally:
        shutil.rmtree(work_root)
        receipt.update(wall_time_s=round(time.monotonic() - started, 3), work_root_cleaned=not work_root.exists())
        (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'run_id': run_id, 'task_id': task_id, 'completed': receipt.get('completed', False),
                          'output': str(output)}))


if __name__ == '__main__':
    raise SystemExit(main())
