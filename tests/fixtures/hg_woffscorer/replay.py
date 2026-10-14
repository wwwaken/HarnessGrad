"""Parent replay of bounded scorer controls only; never reacquire or run tasks."""
import contextlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = Path('tests/fixtures/hg_woffscorer')


def call(script, args=(), stdout=None, stderr=None, offline=True):
    command = (['timeout', '150s', 'env', 'PYTHONDONTWRITEBYTECODE=1', 'CUDA_VISIBLE_DEVICES=',
                'python3', str(PREFIX / 'offline_exec.py')] if offline else
               ['env', 'PYTHONDONTWRITEBYTECODE=1', 'python3']) + [str(script)] + list(args)
    command_text = shlex.join(command)
    for symbol,path in [('>',stdout),('2>',stderr)]:
        if path:
            command_text += ' ' + symbol + ' ' + shlex.quote(str(path))
    print('+ ' + command_text, flush=True)
    with (open(ROOT/stdout,'w') if stdout else contextlib.nullcontext(sys.stdout)) as out:
        with (open(ROOT/stderr,'w') if stderr else contextlib.nullcontext(sys.stderr)) as err:
            result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
    assert result.returncode == 0, (command, result.returncode)


for side,name in [('official','official'),('local','local'),('compare','comparison')]:
    call(PREFIX/'fever/run.py', [side], PREFIX/f'fever/{name}.json', PREFIX/f'fever/{side}-offline.txt')
call(PREFIX/'bigbench/import_probe.py', stdout=PREFIX/'bigbench/full-module-import-output.json',
     stderr=PREFIX/'bigbench/full-module-import-offline-receipt.txt')
for side,name in [('official','official-output'),('local','local-output'),('compare','comparison')]:
    call(PREFIX/'bigbench/run.py', [side], PREFIX/f'bigbench/{name}.json', PREFIX/f'bigbench/{side}-offline-receipt.txt')
for ds in ['gsm8k','strategyqa']:
    for side in ['official','local']:
        call(PREFIX/'numeric_boolean/execute.py', [ds,side], PREFIX/f'numeric_boolean/{ds}-{side}.json',
             PREFIX/f'numeric_boolean/{ds}-{side}-offline.txt')
call(PREFIX/'numeric_boolean/execute.py', ['strategyqa','local','--canonical-boolean-projection'],
     PREFIX/'numeric_boolean/strategyqa-local-projected.json', PREFIX/'numeric_boolean/strategyqa-local-projected-offline.txt')
for panel in ['valid_official_boolean','adapter_text_official_out_of_contract']:
    stem=PREFIX/f'numeric_boolean/strategyqa-{panel}'
    call(PREFIX/'numeric_boolean/source/strategyqa/eval.py',
         ['--golds_file',str(stem)+'-golds.json','--predictions_file',str(stem)+'-predictions.json',
          '--metrics_output_file',str(stem)+'-cli-metrics.json'],
         Path(str(stem)+'-cli-stdout.txt'),Path(str(stem)+'-cli-offline.txt'))
call(PREFIX/'numeric_boolean/compare.py',stdout=PREFIX/'numeric_boolean/comparison.json',offline=False)
for ds in ['hotpotqa','triviaqa','musique','twowikimultihopqa']:
    for side in ['official','local']:
        call(PREFIX/'public_qa/execute.py', [side,ds], PREFIX/f'public_qa/outputs/{ds}/{side}.stdout.json',
             PREFIX/f'public_qa/outputs/{ds}/{side}.offline-receipt.txt')
call(PREFIX/'public_qa/compare.py',stdout=PREFIX/'public_qa/comparison-summary.stdout.json',offline=False)
print('PASS: parent replay of bounded scorer controls; no task runner invoked',flush=True)
