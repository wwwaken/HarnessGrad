"""AgentDojo v1.2.2, utility under registered ``ignore_previous`` injection.

949 user/injection pairs across 97 user tasks, pinned package/source 0.1.35. Scalar
reward is the official utility predicate; official attacker success is separately recorded,
never inverted into a utility score. This is not the paper's ``important_instructions``
attacker, all-attacks safety, or an adaptive attack. Goals carry no defence treatment.
Same-user attack variants stay on the same platform train/eval side to avoid split leakage.
Agent runtime contains upstream tool code but no tasks, ground_truth, or scorer modules.

**The initial environment is agent-readable, and that changes what the numbers mean.**
``SETUP`` materialises ``dojo.initial.json`` into the agent's working directory. The file
is ``bridge.snapshot(case)``: the whole initial environment (inbox, calendar, cloud drive,
bank, slack, web) plus the tool catalogue. It has to be there because ``cli/dojo`` is a
program the agent runs and it reads that file from its cwd on every command (``tools``,
``call``, ``submit``); the sandbox binds the task directory but not the prepared dataset
tree, so the source is not otherwise reachable, and deleting the copy stops the bridge
(``dojo.py tools`` -> FileNotFoundError). The registered injection payload is therefore
verbatim in that file, inside ``environment``, for all 949 prepared cases -- not only in
what a tool returns. The goal does not name the file, but ``dojo.py``, which it does name,
sits beside it. The verifier does not read it: ``VERIFY.inputs`` is check.py + bridge.py +
case.json + the trusted runtime, and ``check.py`` re-derives the environment from
``case.json`` with ``load_and_inject_default_environment``. Consequence: utility is an
upper bound, because the state is readable and a case is answerable with no tool call at
all (``submit`` alone yields utility 1 on case 0), and ``attack_success`` no longer
measures an instruction delivered inside a tool response -- it measures one the agent could
read directly. The published 0.2055 utility under ``ignore_previous`` (949 pairs) was
produced under this SETUP and is affected. No safe local fix exists: any state the
agent-side bridge can read the agent can read too, removing the copy breaks the bridge, and
redacting ``environment`` would strip the payload from tool responses as well (the same file
is what the bridge serves). A trusted tool service owning the environment (the tau-bench
pattern) is the real fix; it needs an image and a service spec, not an adapter edit.
"""
from __future__ import annotations

import json
from pathlib import Path

from data.scaffolds.qa.base import is_eval

KIND = 'dataset'

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"

#: The benchmark's own evaluation set, within this adapter's pool: **every task here belongs
#: to it**. The pool is the v1.2.2 suite's user x injection pairs; every one is an evaluation pair under the single fixed attack this adapter names.
#:
#: `None` is the accurate value only because nothing in the pool is study material -- it does
#: not claim the pool is the whole of the benchmark's evaluation set (see `ds1000`, which is a
#: measured subset). `--split official --side eval` is the comparable run: the whole pool, with
#: no study material in it. `--split declared` keeps this adapter's own division.
OFFICIAL_EVAL = None

DATASET_ROOT = Path('/mnt/20t/xubuqiang/datasets/agentdojo')
COMMIT = '089ed468cf3ed0322acc66b0211f26d9d90dbf60'
VERSION = 'v1.2.2'
ASSETS = Path(__file__).resolve().parent / 'agentdojo'
REWARD_REL = 'verifier/reward.txt'
EVIDENCE_REL = 'verifier/evidence.json'
PREPARED = 'prepared-ignore_previous'


def records():
    with (DATASET_ROOT / '_src/cases.json').open() as h:
        return json.load(h)


def _indices():
    """Public case IDs from directory names, without opening the mixed prompt catalog.

    The legacy roster can describe required paths before fresh attack-specific preparation;
    legacy snapshots themselves are never selected for SETUP or verification.
    """
    prepared = DATASET_ROOT / PREPARED
    if not prepared.is_dir():
        # Roster only: a pre-preparation checkout still has to enumerate its cases so
        # `load()` can say the dataset is unprovisioned. `provision_status` gates on
        # PREPARED, and SETUP/VERIFY never read this legacy directory.
        prepared = DATASET_ROOT / 'prepared'
    return sorted(int(p.name) for p in prepared.iterdir()
                  if p.is_dir() and p.name.isdecimal() and str(int(p.name)) == p.name)


def _task(index, record):
    return {'task_id': f'agentdojo/{index}', 'goal':
              record['prompt'] + '\n\nUse the AgentDojo tools through this CLI:\n'
              '  dojo_runtime/bin/python dojo.py tools\n'
              '  dojo_runtime/bin/python dojo.py call \'{"function":"name","args":{}}\'\n'
              '  dojo_runtime/bin/python dojo.py submit "final answer"\n'}


def load():
    rows = records()
    return ([_task(i, r) for i, r in enumerate(rows)],
            {f'agentdojo/{i}': 'official utility' for i in range(len(rows))})


def control_task(task_id):
    """Load one explicit control case without opening the mixed prompt catalog."""
    if task_id not in {f'agentdojo/{i}' for i in _indices()}:
        raise SystemExit(f'AgentDojo: unknown task id {task_id!r}')
    index = task_id.split('/')[-1]
    record = json.loads((DATASET_ROOT / PREPARED / index / 'case.json').read_text())
    return _task(index, record)


def oracle_files(task):
    index = task['task_id'].split('/')[-1]
    return {'action.json': (DATASET_ROOT / PREPARED / index / 'oracle.json').read_text()}


def __getattr__(name):
    if name == 'TASK_COUNT':
        return len(records())
    rows = records() if name == 'SPLIT' else None
    if name == 'SPLIT':
        return {side: [f'agentdojo/{i}' for i, r in enumerate(rows)
                       if is_eval(r['suite'] + '/' + r['user']) == want]
                for side, want in [('train', False), ('eval', True)]}
    if name == 'ENV':
        return {f'agentdojo/{i}': {'kind': 'files'} for i in _indices()}
    if name == 'SETUP':
        return {f'agentdojo/{i}': {'files': [
            {'path': 'dojo_runtime', 'from': str(DATASET_ROOT / 'agent_runtime'), 'immutable': True},
            {'path': 'dojo.py', 'from': str(ASSETS / 'cli/dojo')},
            {'path': 'dojo.initial.json', 'from': str(DATASET_ROOT / PREPARED / str(i) / 'initial.json')},
        ]} for i in _indices()}
    if name == 'VERIFY':
        return {f'agentdojo/{i}': {
            'kind': 'command', 'argv': ['python3', 'verify/check.py', '--reward-file', REWARD_REL,
                                      '--evidence-file', EVIDENCE_REL],
            'inputs': [
                {'path': 'verify/check.py', 'from': str(ASSETS / 'verify/check.py')},
                {'path': 'verify/bridge.py', 'from': str(ASSETS / 'bridge.py')},
                {'path': 'verify/case.json', 'from': str(DATASET_ROOT / PREPARED / str(i) / 'case.json')},
                {'path': 'trusted_runtime', 'from': str(DATASET_ROOT / 'runtime'), 'immutable': True},
            ], 'reward_file': '/'+REWARD_REL, 'evidence_file': '/'+EVIDENCE_REL,
        } for i in _indices()}
    raise AttributeError(name)


def downloads():
    return [
        {'kind': 'http', 'name': 'AgentDojo source + suites', 'version': COMMIT,
         'url': f'https://codeload.github.com/ethz-spylab/agentdojo/tar.gz/{COMMIT}',
         'size': '~200 KB compressed source', 'dst': '_src/agentdojo.tar.gz',
         'sha256': 'd7e0ee021be27a69e7e66647979b5a5e0dd10030d38d04ce4102e18a76a228d8',
         'extract_to': '_src',
         'note': 'Package 0.1.35 and suite v1.2.2 are different version axes. Provision isolated runtime and tool-only runtime using data/datasets/agentdojo/prepare.py; never expose full task/ground_truth modules to the agent. Registered ignore_previous attack only; fresh prepared-ignore_previous snapshots required.'},
        {'kind': 'pip', 'name': 'AgentDojo isolated runtime', 'package': 'agentdojo', 'version': '0.1.35',
         'size': '~200 MB with SDK dependencies',
         'note': 'Install only inside dataset runtime venv. Exact installed dependency versions are recorded in _src/runtime-requirements.lock; no model API calls are used by tools, gold audit or predicate evaluation.'},
    ]


def provision_status():
    rows = records()
    needed = [DATASET_ROOT / '_src/cases.json', DATASET_ROOT / 'runtime/bin/python',
              DATASET_ROOT / 'agent_runtime/bin/python']
    needed += [DATASET_ROOT / PREPARED / str(i) / name
               for i in range(len(rows)) for name in ('case.json', 'initial.json', 'oracle.json')]
    return {'root': str(DATASET_ROOT), 'split_dir': str(DATASET_ROOT),
            'present': bool(rows) and all(p.is_file() for p in needed), 'tasks': len(rows)}
