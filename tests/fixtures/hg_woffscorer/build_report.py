"""Assemble the review report from measured component comparisons and fragments."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(name):
    return json.loads((HERE / name).read_text())


fever = read('fever/comparison.json')
bigbench = read('bigbench/comparison.json')
numeric = read('numeric_boolean/comparison.json')
public = read('public_qa/comparison.json')
rows = [
    ('fever', 'complete unmodified module; strict predicate + full API',
     f"{fever['agreements']}/{fever['controlled_inputs']} strict; {fever['divergences']} flat-gold projection difference; {fever['singleton_fever_score_errors']} full singleton API errors"),
]
for name in ('physicsquestions', 'sportsunderstanding'):
    c = bigbench[name]
    qualifier = 'paired channel outcomes; not equivalence' if name == 'sportsunderstanding' else 'same strings/accepted targets'
    rows.append((name, 'unchanged official functions selected from AST; full import failed',
                 f"{c['agreement_count']}/{c['input_count']} agree; {c['divergence_count']} differ; {qualifier}"))
for name in ('gsm8k', 'strategyqa'):
    c = numeric[name]
    extra = '; Boolean semantic projection 4/4 agrees, separate from raw inputs' if name == 'strategyqa' else ''
    rows.append((name, 'complete unmodified official scorer module',
                 f"{c['counts'].get('agreement',0)}/{len(c['cases'])} raw outcomes agree; {c['counts'].get('divergence',0)} differ{extra}"))
for name in ('hotpotqa', 'triviaqa', 'musique', 'twowikimultihopqa'):
    c = public[name]
    text = f"{c['agreeing_inputs']}/{c['numeric_comparisons']} numeric input comparisons agree; {c['divergent_inputs']} differ; {c['non_numeric_inputs']} nonnumeric"
    if name == 'musique':
        text += f"; platform reward differs from answer-F1 on {c['platform_reward_vs_official_answer_f1_policy_difference_count']} inputs"
    rows.append((name, 'complete unmodified upstream evaluator', text))

header = '''# Offline official scorer execution and controlled comparisons - w-offscorer

**Disposition: `scorer-offline-closure` remains open. No dataset blocker is closed.**
Official execution evidence is bounded to the scored components and input domains listed below.

Baseline: `fdfdbce` in the registered `/tmp/hg-offscorer` worktree; review date
2026-10-15. Read first and built on: `reports/w-clo-actor-closures.md`,
`tests/fixtures/hg_wclo_actor/`, `reports/w-shared-topology-survey.md`, and
`reports/e1-fever-physics-bird-review.md` / `tests/fixtures/hg_e1_review/`.
The earlier actor byte closures established inventory, not official execution.
The E1 packet already acquired FEVER's scorer and BIG-bench's metric source.
This packet executes those sources and adds public-source scoring controls for
GSM8K, StrategyQA, HotpotQA, TriviaQA, MuSiQue-Ans and 2WikiMultiHopQA.

## Coverage and limits

Official scorer function execution: **nine QA datasets**. All controls are authored
synthetic input sets; this is neither benchmark-task execution nor a measured
accuracy estimate. Source-function execution is narrower than a successful complete
upstream module import; the table and BIG-bench findings preserve that distinction.
Different metrics, channels and representations are not combined into an aggregate
agreement rate. Every per-input value/count below comes from the raw command outputs.

All component-relative paths below resolve under `tests/fixtures/hg_woffscorer/`
and the named component directory. Source copies, authored inputs, official and local
outputs, comparison files, acquisition receipts and all commands are retained there.
The root `SHA256SUMS` covers the full fixture packet. The complete validation command
log and checker output are `reports/w-offscorer-validation.txt`.

| Dataset | Actual official execution | Controlled comparison result |
| --- | --- | --- |
'''
header += '\n'.join(f'| `{name}` | {mode} | {result} |' for name, mode, result in rows)
header += '''

All nine now have **bounded offline official scoring-component execution evidence**.
No new official execution evidence is supplied here for the other surveyed QA-command
routes `bfcl_v3`, `chessbench_puzzles` or `reasoning_gym`. Nor is new evidence supplied
for the seven native actor-workdir routes or the four snapshot-service routes. Existing
ALFWorld/Terminal-Bench/Chess observations and all historical/incomplete receipts keep
their original classifications. This report does not overwrite or generalize them.

## Offline execution and local scorer custody

Each successful scorer runs through `offline_exec.py`, which closes inherited socket
fds above stderr, installs a kernel seccomp EPERM filter for socket APIs and
`io_uring_setup`, and actively probes denied IPv4/IPv6/UNIX socket creation before
importing scoring code. Each invocation retains actual interpreter/libseccomp digests,
CPU/fd limits and `production_runtime_observation:false`; the outer timeout bounds
wall time. Acquisition commands are separate network-enabled public-source requests.
No model, GPU, endpoint, task runner, production verifier or container is run.

The original production adapter score functions and shared scorer sources remain
unchanged; `local-source-pins.json` recomputes their baseline byte identities. For
native PyArrow readers a Python audit hook alone cannot exclude data reads. Corrected
GSM8K, HotpotQA and TriviaQA imports therefore temporarily refuse only dataset row
construction, restore the fixture-only substitution before scoring, and assert empty
record caches. The earlier import attempts and their limitations are preserved in
`numeric_boolean/preserved-first-attempt/` and
`public_qa/historical-import-attempts/`, not represented as clean payload-exclusion
receipts. FEVER and BIG-bench CSV reads were refused by the Python audit hook. No
released task is scored in either the original or corrected controlled calls. This
fixture mechanism does not claim production filesystem isolation or trusted custody.

The following component sections contain exact source revisions and recomputed digests,
commands, per-input comparisons, measured divergence/error counts and domain caveats.

'''
parts = [header]
for name, file in [('FEVER', 'fever/report.md'), ('BIG-bench', 'bigbench/report-fragment.md'),
                   ('Numeric / Boolean', 'numeric_boolean/report-fragment.md'),
                   ('Public QA', 'public_qa/report-fragment.md')]:
    parts.append('\n<!-- Component: ' + name + ' -->\n\n' + (HERE / file).read_text())
parts.append('''
## Shared blocker decision - remains open

The shared registry observation is sharpened only for `scorer-offline-closure`, with
an appended verbatim evidence locator into this report. Its status, next_action and
all dataset records, historical records and other shared blockers remain unchanged.
The journal is append-only. Production adapters/shared scorers, runs/, archives and
frozen evidence are untouched.

Still unmet: complete portable transitive scorer/runtime/image/ABI closure and byte
custody; successful full BIG-bench module/task-runner execution; complete matched
response processing and metric comparability; dataset source/selected-gold provenance
gates; trusted class-specific lifecycle/resource/cleanup observations; and valid live
controls before pilots. Snapshot/service connectivity must remain available where
required and only matching known production isolation classes may be compared. The
kernel-offline fixture receipts do not satisfy those production requirements.
''')
report = ROOT / 'reports/w-offscorer-equivalence.md'
report.write_text(''.join(parts))
summary = {name: {'official_execution': mode, 'controlled_result': result} for name,mode,result in rows}
(HERE / 'coverage-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'report':str(report.relative_to(ROOT)), 'official_component_execution_datasets':list(summary)},indent=2))
