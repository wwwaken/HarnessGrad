"""Render the review report from computed records, without importing scorers."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(name):
    return json.loads((OUT / name).read_text())


def link(name, label):
    return f'[{label}](../tests/fixtures/hg_wclo_actor/{name})'


scope = read('scope.json')
records = {name: read('datasets/' + name + '.json') for name in scope['datasets']}
gold = {name: read('gold/' + name + '.json') for name in scope['datasets']}
host = read('interpreter.json')
common = read('common-sources.json')
check = next(s for s in common if s['path'] == 'data/scaffolds/qa/verify/check.py')
check_main = next(d for d in check['definitions'] if d['symbol'] == 'main')
members = [row for value in gold.values() for row in value.get('archive_member_bindings', [])]
equal = sum(any(c['equals_local_artifact'] for c in row.get('candidates', [])) for row in members)

lines = [
    '# Actor-workdir pinned scorer closure records — w-clo-actor', '',
    f'Source baseline: `{scope["source_git_commit"]}`. Review date: 2026-10-15.', '',
    '**Disposition: `scorer-offline-closure` remains open.** There are 19 new partial local',
    'byte-closure records; zero complete provisioned offline scorer closures are certified.',
    'These records make the source, installed runtime/package members, and local expected-data',
    'identities reviewable. They do not supply offline-installable runtime payloads, per-task',
    'trusted materialization bindings, or new class-specific runtime observations.', '',
    '## Scope established from the survey', '',
    'The topology survey has **19 `actor-workdir` routes: 12 shared QA commands (Q) and seven',
    'native commands (F)**. All are included, including Alfworld, BIRD Mini-Dev, ChessBench,',
    'DS-1000, Jericho, LiveCodeBench, ScienceWorld and SpreadsheetBench in addition to the',
    'eleven named QA adapters. AppWorld, GAIA, tau-bench and Terminal-Bench are the four',
    '`snapshot-service` rows and are outside this inventory. ChessBench’s alternate trusted',
    'stepwise controller is `in-process`; its default QA record does not cover that branch.',
    'The survey predates its recorded-class fix; current controller source is independently',
    'hashed in `common-sources.json`. Routes in this report describe source wiring, not new',
    'executed observations. Full verbatim survey rows are preserved in each record.', '',
    'Read first: `reports/w-shared-topology-survey.md`,',
    '`reports/w-tbdep-transitive-inventory.md`, `tests/fixtures/hg_wtbdep/`,',
    '`reports/w-net-receipts.md` and its committed evidence. The inherited dependency report',
    'cites `hg_wtbdep/python/` and `hg_wtbdep/runtime/`, which are absent in this checkout.',
    'Those missing fixture hashes are not reused. Existing inventory paths are leads for',
    'new hashes of actual installed files, not a substitute for reading the bytes.', '',
    '## Common interpreter, check and package custody', '',
    f'- `python3` currently resolves to `{host["which"]}` → `{host["resolved_executable"]}`.',
    f'  Version: `{host["version"]}`; SOABI `{host["soabi"]}`.',
    f'  Binary SHA-256: `{host["executable"]["sha256"]}`.',
    f'- QA check entry: `{check["path"]}:{check_main["line"]}` (`main`),',
    f'  file SHA-256 `{check["sha256"]}`.',
    '  Each QA record also resolves `base.QASpec.verifier`, gold read, adapter import,',
    '  structured `score_prediction` and legacy `score` calls to exact source lines/hashes.',
    '- These native files environments have no Docker image. `python3`/PATH, installed',
    '  packages, libc/loader and host prefix are observations, not adapter-enforced locks.',
    '- Guarded fresh imports execute only installed package imports, with networking denied',
    '  and GPU visibility disabled. No adapter import, score call, constructor, submitted',
    '  code, task, model, endpoint, Docker or benchmark run is performed. Preexisting',
    '  startup/inspection packages are separated from requested package imports.',
    f'- {len(read("packages.json"))} installed-distribution manifests cover observed imports plus',
    '  recursive default metadata requirements (including TextWorld PDDL). Every existing',
    '  metadata-enumerated member is hashed directly, excluding regenerable bytecode.',
    '  RECORD’s claimed member hashes are never substituted for a fresh hash. A declared',
    '  dependency superset is not a claim that every library executes in every task.',
    '  Unlisted files, lazy/plugin selection and offline wheel payload custody remain open.',
    '- `interpreter-files.json`, `native-files.json` and `jre-files.json` bind current',
    '  stdlib/extension/library/JRE bytes. Native inventory is bounded by imported modules',
    '  and existing ABI leads; it is not complete transitive OS/dlopen/plugin closure.', '',
    '## Per-dataset closure table', '',
    'Every row pins the implemented adapter/check bytes, interpreter observation and',
    'source/expected-data files in the linked manifests. “Still unpinned” includes the',
    'common gaps below in addition to the dataset-specific finding in the table.', '',
    '| Dataset / class | Scoring entry reached by source route | Expected-data bytes now pinned | Still unpinned / qualification |',
    '| --- | --- | --- | --- |',
]
brief = {
    'alfworld': ('134 released game files; stripped-game recipe', 'Stripped staged game binding; native dlopen/custody; control lacks complete resources/lifecycle'),
    'bfcl_v3': ('simple/irrelevance tables + simple answers', 'Official AST scorer absent; selected-index/per-task custody'),
    'bird_minidev': ('question table + SQL gold + 11 SQLite databases', 'Per-task gold.sql binding; Python/SQLite ABI enforcement'),
    'chessbench_puzzles': ('puzzles.csv with FEN and moves', 'Wheel/runtime enforcement; stepwise is a separate class/metric'),
    'ds1000': ('test.jsonl context tests + four seaborn CSVs', 'Actor context authentication; upstream environment mismatch; candidate imports/cache misses'),
    'fever': ('valid.jsonl labels + evidence', 'Hub export has no configured digest; official execution/custody'),
    'gsm8k': ('main test + train parquet answer source', 'Adapter numeric metric differs from upstream EM; startup PyArrow visibility'),
    'hotpotqa': ('fullwiki validation answers + supporting facts', 'Conditional PyArrow startup; official joint execution/custody'),
    'jericho': ('57 archive ROM members (not an eligible-task count)', 'Selected official-game/seed binding; Frotz/native custody'),
    'livecodebench': ('1,055 decoded test files + metadata pool', 'Decoded-to-shard derivation not rerun; arbitrary candidate imports'),
    'musique': ('Ans v1.0 dev answers, aliases and support', 'Canonical mirror verification; platform joint vs legacy mode'),
    'physicsquestions': ('ReWOO accepted-spelling CSV', 'Direct upstream metric provenance/execution; staged gold'),
    'reasoning_gym': ('pool.jsonl entries + package resources', '0.1.25 metadata vs 0.1.19 code; family construction/lazy resources not exercised'),
    'scienceworld': ('repository fold + package JAR/tasks/object data', 'Selected JVM/IPC lifecycle and ABI; expected result is world state'),
    'sportsunderstanding': ('ReWOO label CSV', 'Ambiguous-label refusal differs from historical substring rule; staged gold'),
    'spreadsheetbench': ('400 golden workbooks + dataset.json', 'LibreOffice/plugin closure; formula branch vs read-only mount; staged task metadata'),
    'strategyqa': ('ReWOO Yes/No CSV', 'Vendor-source metric provenance/execution; staged gold'),
    'triviaqa': ('rc.nocontext validation + train alias source', 'Startup PyArrow; staged alias serialization; withheld test excluded'),
    'twowikimultihopqa': ('dev.json + entity alias table', 'Official-release mirror provenance; joint vs legacy binding'),
}
for name, record in records.items():
    entries = [e for e in record['entry_points'] if e['role'] in
               ('adapter scorer reached by shared QA check', 'native check/reduction entry')]
    main = next((e for e in entries if e['symbol'] == ('score' if name in scope['qa_command'] else 'main')), entries[0])
    other = ', score_prediction' if any(e['symbol'] == 'score_prediction' for e in entries) else ''
    source = f'`{main["path"]}:{main["line"]}` (`{main["symbol"]}{other}`)'
    desc, finding = brief[name]
    lines.append(f'| {link("datasets/" + name + ".json", "`" + name + "`")} / actor-workdir '
                 f'{"Q" if name in scope["qa_command"] else "F"} | {source} | '
                 f'{link("gold/" + name + ".json", desc)} | {finding} |')
lines += ['', '## Source and expected-data manifest SHA-256s', '',
    'The adapter hashes below are hashes of complete files, not functions. Native check',
    'hashes and upstream child entry points are in each dataset record; the common QA',
    'check hash is above. The expected-data manifest hash binds all individual full',
    'SHA-256s, local paths, provenance pins and archive-member comparisons.', '',
    '| Dataset | Adapter file SHA-256 | Expected-data manifest SHA-256 |',
    '| --- | --- | --- |']
for name, record in records.items():
    adapter = next(s for s in record['adapter_and_check_sources'] if s['path'] == 'data/datasets/' + name + '.py')
    lines.append(f'| `{name}` | `{adapter["sha256"]}` | `{record["gold_expected_data"]["sha256"]}` |')
lines += ['', '## Installed third-party imports', '',
    'Full versions, METADATA/WHEEL/RECORD hashes, installed-member hashes and default',
    'dependency graphs are linked in the dataset records. These are current local',
    'identities; no lock file is represented as an offline payload. The following',
    'table lists every distribution observed during the requested imports, separating',
    'them from preexisting startup/inspection modules. Conditional startup surfaces',
    '(PyArrow) are explicitly included; declaration-only requirements remain separate.', '',
    '| Dataset(s) | Installed distributions observed in requested imports |',
    '| --- | --- |']
stdlib = [n for n, r in records.items() if not r['directly_observed_imported_packages']]
lines.append('| ' + ', '.join('`' + n + '`' for n in stdlib) + ' | No special third-party comparison/replay import observed; BIRD still uses SQLite native ABI. |')
for name, record in records.items():
    packages = record['directly_observed_imported_packages']
    if packages:
        lines.append('| `' + name + '` | ' + ', '.join('`' + p + '==' + d['version'] + '`' for p, d in sorted(packages.items())) + ' |')
lines += ['', '## Gold/provenance and remaining findings', '',
    f'- {sum(g["artifact_count"] for g in gold.values())} source/expected-data files are hashed,',
    f'  with no missing expected-data pattern. {equal} local members were independently',
    '  matched byte-for-byte to local provenance archives without extraction or task execution.',
    '  Direct configured digest matches are marked individually. Archive-member equality',
    '  establishes local extraction identity, not independent upstream authenticity.',
    '- QA `gold.json` is inline JSON constructed by the hashed adapter/scaffold and read by',
    '  the shared check. This inspection hashes its source data and projection code, not a',
    '  fabricated run-specific gold file. Native staged gold.sql, stripped PDDL, task.json',
    '  and context.json likewise require trusted selected-task bindings. No raw expected',
    '  answers, test contents or references are copied into this fixture directory.',
    '- Reasoning Gym family entry-point candidates and package resources are inventoried',
    '  statically. No family constructor or `score_answer` is called. Complete runtime',
    '  lazy-import/resource behavior is not inferred from successful package import.',
    '- FEVER’s Hub export has a revision but no configured byte digest. This work adds a',
    '  current local byte pin without claiming immutable export reconstruction. MuSiQue',
    '  and 2Wiki retain their mirror-provenance qualifications. GSM8K and BFCL retain their',
    '  explicit adapter/diagnostic metric identities, not an official-equivalence claim.', '',
    '## Existing class evidence and blocker disposition', '',
    '`prior-evidence.json` recomputes the identities of existing reports and ALFWorld',
    'review copies. The ALFWorld noop result records a real `actor-workdir` verifier',
    'with raw `score=0.0` and scorer `measured=true`, but enforcement publication is',
    'unmeasured/non-comparable; CPU/RAM enforcement and formal lifecycle remain unknown.',
    'It is relevant partial runtime evidence, not proof for every actor-workdir scorer.',
    'The Terminal-Bench report provides official raw scorer/image/resource/snapshot/cleanup',
    'observations in `snapshot-service`, with publication withheld. It is a model for',
    'receipts and cannot be transferred across isolation classes. No old receipt is',
    'edited, rerun, resumed or upgraded.', '',
    '**Still unmet in the shared blocker’s own next_action:** complete provisioned',
    'transitive runtime/image/ABI closures and trusted byte custody; official provenance',
    'and execution for the required dataset/metric; class-specific resource/lifecycle/',
    'cleanup observations and valid live offline controls before pilots. The four',
    'snapshot/service datasets remain outside this work; their connectivity and snapshot',
    'semantics must be retained. Comparisons still require matching known classes.',
    'No manifest here establishes those execution requirements or licenses a pilot.', '',
    'Registry change is limited to appending this partial inventory to the shared',
    'blocker’s `observed` and adding a literal report evidence locator. Status, its full',
    '`next_action`, every dataset/shared reference, dataset-local blocker and historical',
    'record remain unchanged. Dataset-local changes are unwarranted because no local',
    'blocker’s requested runtime/official-execution result was produced.', '',
    'Validation commands and outputs: `reports/w-clo-actor-validation.txt`. Fixtures and',
    'their complete SHA-256 inventory: `tests/fixtures/hg_wclo_actor/SHA256SUMS`.',
]
(ROOT / 'reports/w-clo-actor-closures.md').write_text('\n'.join(lines) + '\n')
print('Rendered reports/w-clo-actor-closures.md from 19 computed dataset records')
