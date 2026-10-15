"""Offline source/ID custody audit; no adapter import, scorer or dataset run."""
import ast
import base64
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CSV = Path('/mnt/20t/xubuqiang/datasets/strategyqa/ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/strategy_qa.csv')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(name, obj):
    (ROOT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def load(name):
    return json.loads((ROOT / name).read_bytes())

def blob(name, expected):
    record = load(name + '.body')
    raw = base64.b64decode(record['content'])
    actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert record['sha'] == actual == expected
    return raw, {'capture': name, 'bytes': len(raw), 'sha256': sha(raw), 'git_blob': actual}

def index(rows):
    result = defaultdict(list)
    for r in rows:
        result[r['question']].append(r)
    return result

def content(rows):
    return Counter((r['question'], r['answer']) for r in rows)

def main():
    receipts = [json.loads(p.read_text()) for p in sorted(ROOT.glob('*.receipt.json'))]
    for r in receipts:
        if 'raw_fixture' in r:
            raw = Path(r['raw_fixture']).read_bytes()
            assert len(raw) == r['bytes'] and sha(raw) == r['sha256'] and r['complete']
    ledger = '\n'.join(json.dumps({k: r.get(k) for k in [
        'url', 'command', 'status', 'sha256', 'bytes', 'raw_fixture', 'error'
    ]}, ensure_ascii=False) for r in receipts) + '\n'
    local_raw = CSV.read_bytes()
    ledger += json.dumps({'path': str(CSV),
        'command': 'python3 tests/fixtures/hg_stratsplit/analyze.py',
        'status': 'FOUND / local read_bytes', 'sha256': sha(local_raw),
        'bytes': len(local_raw), 'raw_fixture': None,
        'note': 'Existing installed payload read in place; not copied or modified'}) + '\n'
    (ROOT / 'attempts.jsonl').write_text(ledger)

    tree = load('repo-tree.body')
    assert tree['truncated'] is False
    assert load('repo-commit.body')['tree']['sha'] == tree['sha']
    repo_entries = {x['path']: x for x in tree['tree']}
    et = load('evaluator-tree.body')
    assert et['truncated'] is False
    assert load('evaluator-commit.body')['tree']['sha'] == et['sha']
    eval_entries = {x['path']: x for x in et['tree']}
    bindings = []
    author = {}
    for side in ['train', 'dev']:
        raw, info = blob('repo-' + side, repo_entries['data/strategyqa/' + side + '.json']['sha'])
        assert len(raw) == repo_entries['data/strategyqa/' + side + '.json']['size']
        author[side] = json.loads(raw)
        bindings.append(info)
    for name, entries, path, out in [
        ('repo-readme', repo_entries, 'README.md', 'author-README.md'),
        ('evaluator-readme', eval_entries, 'README.md', 'evaluator-README.md'),
    ]:
        raw, info = blob(name, entries[path]['sha'])
        (ROOT / out).write_bytes(raw)
        bindings.append(info)
    raw, info = blob('evaluator-dummy', eval_entries['predictions_dummy.json']['sha'])
    bindings.append(info)
    dummy_ids = set(json.loads(raw))  # Deliberately do not use prediction values.
    save('git-bindings.json', bindings)

    inventory = []
    with zipfile.ZipFile(ROOT / 'dataset-zip.body') as archive:
        for member in archive.infolist():
            raw = archive.read(member)  # zipfile validates each member's CRC.
            obj = json.loads(raw)
            inventory.append({'name': member.filename, 'bytes': len(raw),
                              'compressed_bytes': member.compress_size,
                              'sha256': sha(raw), 'crc32': member.CRC,
                              'json_type': type(obj).__name__, 'records': len(obj),
                              'record_key_signatures': dict(Counter(
                                  ','.join(sorted(r)) for r in obj)) if isinstance(obj, list) else None})
        train = json.loads(archive.read('strategyqa_train.json'))
        test = json.loads(archive.read('strategyqa_test.json'))
    save('zip-members.json', inventory)
    test_ids = {r['qid'] for r in test}
    train_ids = {r['qid'] for r in train}
    author_ids = {r['qid'] for side in author.values() for r in side}
    assert len(test_ids) == len(test) == 490 and dummy_ids == test_ids
    assert len(train_ids) == len(train) == 2290 and not (test_ids & train_ids)
    assert len(author_ids) == sum(map(len, author.values())) == 2290
    assert content(train) == content(author['train'] + author['dev'])
    assert not (train_ids & author_ids)  # Distinct observed ID namespaces.
    assert not (test_ids & author_ids)
    save('membership-ids.json', {
        'distribution_train': [r['qid'] for r in train],
        'official_evaluator_test': sorted(dummy_ids),
        'author_unofficial_train': [r['qid'] for r in author['train']],
        'author_unofficial_dev': [r['qid'] for r in author['dev']]})

    raw = CSV.read_bytes()
    assert len(raw) == 200453 and sha(raw) == 'c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055'
    local = list(csv.DictReader(io.StringIO(raw.decode(), newline='')))
    prefix = "Answer with 'Yes' or 'No': "
    assert len(local) == 2290 and all(r['input'].startswith(prefix) for r in local)
    assert all(type(r['answer']) is bool for r in train)
    assert Counter((r['input'][len(prefix):], r['target']) for r in local) == Counter(
        (r['question'], 'Yes' if r['answer'] else 'No') for r in train)
    # Evaluate only the local pure split predicate, extracted from current source.
    # Never import the adapter, harness, downloaded source or any evaluator.
    base = Path('data/scaffolds/qa/base.py').read_text()
    node = next(n for n in ast.parse(base).body if isinstance(n, ast.FunctionDef) and n.name == 'is_eval')
    scope = {'hashlib': hashlib}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<local-is_eval>', 'exec'), scope)
    is_eval = scope['is_eval']
    zip_index, test_index = index(train), index(test)
    author_index = index(author['train'] + author['dev'])
    author_side = {r['qid']: side for side, rows in author.items() for r in rows}
    counts, cross, ambiguities = Counter(), Counter(), []
    output = ROOT / 'installed-row-binding.tsv'
    with output.open('w', newline='') as handle:
        fields = ['row_index', 'task_id', 'imposed_side', 'csv_parsed_row_sha256',
                  'question_utf8_sha256', 'original_partition', 'zip_qid_candidates',
                  'author_qid_candidates', 'author_unofficial_partition']
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for i, row in enumerate(local):
            q = row['input'][len(prefix):]
            zrows, arows = zip_index[q], author_index[q]
            assert zrows and arows and not test_index[q]
            assert all(row['target'] == ('Yes' if r['answer'] else 'No') for r in zrows + arows)
            sides = {author_side[r['qid']] for r in arows}
            assert len(sides) == 1  # Duplicate rows do not create partition ambiguity.
            side = next(iter(sides))
            task = 'strategyqa/test/' + str(i)
            imposed = 'eval' if is_eval(task) else 'train'
            counts[imposed] += 1
            cross[(side, imposed)] += 1
            if len(zrows) != 1 or len(arows) != 1:
                ambiguities.append(i)
            writer.writerow(dict(zip(fields, [i, task, imposed,
                sha(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()),
                sha(q.encode()), 'Train', ','.join(sorted(r['qid'] for r in zrows)),
                ','.join(sorted(r['qid'] for r in arows)), side])))
    ns = {'s': 'http://doc.s3.amazonaws.com/2006-03-01'}
    listing = ET.fromstring((ROOT / 'gcs-prefix.body').read_bytes())
    assert listing.findtext('s:IsTruncated', namespaces=ns) == 'false'
    objects = [{e.tag.split('}')[-1]: e.text for e in x} for x in listing.findall('s:Contents', ns)]
    save('gcs-objects.json', objects)
    save('repo-files.json', [x for x in tree['tree'] if x['type'] == 'blob'])
    summary = {
        'installed_csv': {'path': str(CSV), 'bytes': len(raw), 'sha256': sha(raw), 'rows': len(local)},
        'prefix_removed_exactly': prefix,
        'original_partition_coverage': {'Train': 2290, 'Test': 0, 'unaccounted_installed_rows': 0,
                                        'Test_ids_missing_from_installed_pool': 490},
        'unofficial_partition_coverage': {side: len(rows) for side, rows in author.items()},
        'imposed_partition_coverage': dict(counts),
        'unofficial_by_imposed': {side: {i: cross[(side, i)] for i in ['train', 'eval']} for side in author},
        'id_namespaces': {'distribution_train_vs_author_qid_overlap': len(train_ids & author_ids)},
        'exact_id_ambiguity': {'installed_row_indices': ambiguities, 'count': len(ambiguities),
                               'reason': 'Two equal question/answer rows; retain both candidate IDs; no occurrence-order tie-break',
                               'partition_ambiguity': 0},
        'binding': {'path': str(output), 'bytes': output.stat().st_size, 'sha256': sha(output.read_bytes())},
        'zip_member_count': len(inventory), 'listed_gcs_objects': len(objects),
        'repo_blob_count': sum(x['type'] == 'blob' for x in tree['tree']),
        'missing_brief_paths': [p for p in ['registry/w-journalcov-review.md', 'tests/fixtures/hg_wjc2'] if not Path(p).exists()],
        'source_sha256': {p: sha(Path(p).read_bytes()) for p in ['data/datasets/strategyqa.py', 'data/scaffolds/qa/base.py']},
    }
    save('binding-summary.json', summary)
    paper = (ROOT / 'paper-text.txt').read_bytes()
    paper_lines = paper.decode().split('\n')
    excerpts = ['Exact line excerpts from pdftotext -layout of paper-pdf.body',
                'Full extracted text bytes: ' + str(len(paper)),
                'Full extracted text SHA-256: ' + sha(paper),
                'Raw PDF request: paper-pdf.receipt.json', '']
    for start, end in [(392, 399), (435, 456), (736, 738)]:
        excerpts += [str(i) + ': ' + paper_lines[i - 1] for i in range(start, end + 1)] + ['']
    (ROOT / 'paper-split-excerpts.txt').write_text('\n'.join(excerpts) + '\n')
    print(json.dumps(summary, indent=2))
    print('PASS: response digests; Git blobs and commit/tree bindings; ZIP member CRCs/digests; official evaluator Test IDs; complete installed multiset and per-row partition coverage.')

if __name__ == '__main__':
    main()
