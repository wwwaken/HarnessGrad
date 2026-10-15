"""Record exact offline validation commands and outputs for this review packet."""
import hashlib
import json
import pathlib
import shlex
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
DEST = ROOT / 'registry/w-trivia3-validation.txt'


def run(args):
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    assert result.returncode == 0, (args, result.stdout)
    return f'$ {shlex.join(args)}\n{result.stdout}exit_code={result.returncode}\n'


def check_external():
    records = json.loads((HERE/'external-evidence-manifest.json').read_text())
    for record in records:
        p=pathlib.Path(record['path'])
        assert p.stat().st_size == record['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256']
    print(json.dumps({'external_manifest_files_verified': len(records)}, sort_keys=True))


if __name__ == '__main__':
    import sys
    if '--external-only' in sys.argv:
        check_external()
        raise SystemExit()
    parts = ['w-trivia3 validation: payload-free metadata and identity audit\n',
             'Reproduce: python3 tests/fixtures/hg_trivia3/validate_packet.py\n']
    commands = [
        ['git','branch','--show-current'],
        ['python3','tests/fixtures/hg_trivia3/enumerate_declarations.py'],
        ['sed','-n','994,1000p','tests/fixtures/hg_trivia2/responses/hub-card-proxy-retry.body'],
        ['python3','tests/fixtures/hg_trivia3/verify_evidence.py'],
        ['python3','tests/fixtures/hg_trivia3/validate_packet.py','--external-only'],
        ['python3','tools/check_dataset_blockers.py'],
        ['git','diff','--exit-code','HEAD','--','AGENTS.md','registry/dataset-blockers.json',
         'registry/withdrawn-requirements.md','docs/adapter-integration-journal.md',
         'data/datasets/triviaqa.py','tests/fixtures/hg_wsel/triviaqa.json',
         'tests/fixtures/hg_trivia','tests/fixtures/hg_trivia2','tests/fixtures/triviaqa_upstream',
         'tests/fixtures/triviaqa_hub_codex225','tests/fixtures/external_provenance_b5'],
        ['git','diff','--check'],
        ['git','diff','--cached','--check'],
    ]
    parts.extend(run(cmd) for cmd in commands)
    parts.append('Acquisition commands (nonzero exits are incomplete acquisition, not benchmark zero scores):\n'
        '1. python3 -u tests/fixtures/hg_trivia3/audit_keys.py\n'
        '   Exit 1; 4 complete shards / 23 errors in retained partial-attempt-summary.json.\n'
        '   This invocation used the earlier all-no-context-plus-validation scope (27 shards).\n'
        '2. python3 -u tests/fixtures/hg_trivia3/audit_keys.py\n'
        '   Exit 1; 4 complete validation shards / 15 errors in validation-attempt2-summary.json.\n'
        '3. python3 -u tests/fixtures/hg_trivia3/audit_keys.py > '
        '/mnt/20t/xubuqiang/hg-work/trivia3/attempt3-output.txt 2>&1\n'
        '   Exit 1; exact stdout follows. Earlier process stdout was shown in the tool transcript; '
        'it was not saved as a byte transcript. Earlier structured error/result summaries are retained.\n')
    parts.append((pathlib.Path('/mnt/20t/xubuqiang/hg-work/trivia3')/'attempt3-output.txt').read_text())
    for name in ['partial-attempt-summary.json','validation-attempt2-summary.json','key-audit-summary.json']:
        parts.append(run(['cat','tests/fixtures/hg_trivia3/'+name]))
    parts.append('Renderer command and exact observed output from final render:\n'
        '$ AM_HOME=/mnt/20t/xubuqiang/hg-work/trivia3/am node '
        '/home/xubuqiang/.agents/skills/answer-me-with-html/scripts/am.mjs render '
        'reports/w-trivia3-page.md -o reports/w-trivia3-page.html --no-open\n'
        '✓ /mnt/20t/xubuqiang/hg-wt/w-trivia3/reports/w-trivia3-page.html\n'
        '  sheet · paper · 4 panels\n'
        '  STE ✓ 0 warnings\n'
        'Task-owned renderer state /mnt/20t/xubuqiang/hg-work/trivia3/am was removed after rendering.\n'
        'No pytest/basetemp/TMPDIR materialisation was used. No task-owned /tmp files were created.\n'
        'Raw range bytes / inventory JSONL / metadata footers are persistent evidence outside git.\n')
    parts.append('NOT VERIFIED / NOT EXECUTED:\n'
        '- No complete validation inventory: four of nineteen key shards complete; remaining transport failures preserved.\n'
        '- Train/test key coverage incomplete; thirteen observed footers include three train/test footers.\n'
        '- No complete four-shard rc validation footer total; only rc.nocontext single-shard total corroborated.\n'
        '- Original consumed-input Domain/VerifiedEval and question/document verification memberships unobserved.\n'
        '- HumanAnswers consumed-input incidence, normalized containment, preservation and redundancy unobserved.\n'
        '- Official original/export key correspondence and numeric denominator unestablished.\n'
        '- No full row content equality, duplicate answer agreement, canonical-value alias membership or writer behavior measured.\n'
        '- No full Parquet-file SHA-256 recomputation; declared LFS identity bound by HTTPS redirect only.\n'
        '- No new execution-receipt search; no upstream converter execution inference.\n'
        '- No dataset loader, benchmark, scorer, model/API endpoint or GPU execution.\n'
        '- No payload answer strings decoded/printed/committed; footer statistic values were not inspected.\n'
        '- No original archives or row payload comparison; no first-five custody packet re-derivation.\n'
        '- No registry edit, withdrawal, journal edit, merge, push, branch deletion or main checkout write.\n'
        '- No browser screenshot/interactive visual verification of HTML; renderer reported zero lint warnings.\n')
    files=sorted([ROOT/'registry/w-trivia3-review.md',ROOT/'registry/proposals/w-trivia3.json',
                  ROOT/'reports/w-trivia3-page.md',ROOT/'reports/w-trivia3-page.html',DEST]
                 + [p for p in HERE.iterdir() if p.is_file()])
    assert len(files)==len(set(files))
    # Include this validation file's exact size by reaching a decimal-width fixed point.
    size=0
    while True:
        sizes=''.join(f'{size if p==DEST else p.stat().st_size} {p.relative_to(ROOT)}\n' for p in files)
        result='\n'.join(parts)+'\nCOMMITTED FILE SIZES (bytes):\n'+sizes
        new_size=len(result.encode())
        if new_size==size:
            break
        size=new_size
    DEST.write_text(result)
    assert all(p.stat().st_size<1_000_000 for p in files)
    print(json.dumps({'validation_file':str(DEST.relative_to(ROOT)),
                      'validation_bytes':size,'files':len(files),
                      'all_files_under_1mb':True},sort_keys=True))
