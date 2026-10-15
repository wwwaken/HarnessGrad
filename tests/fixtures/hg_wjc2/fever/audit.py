"""Recompute original FEVER correspondence; no scorer, selection or run executes."""
import collections
import gzip
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
INSTALLED = Path('/mnt/20t/xubuqiang/datasets/fever/valid.jsonl')
CHECK_ONLY = '--check' in sys.argv[1:]


def emit(path, raw):
    if CHECK_ONLY:
        assert path.read_bytes() == raw, 'Reproduction differs: ' + str(path)
    else:
        path.write_bytes(raw)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()


def normalized(page, line):
    return [unicodedata.normalize('NFC', page), int(line)]


def group_pairs(group):
    return [normalized(e[2], e[3]) for e in group if e[2] is not None and e[3] is not None]


def pair_set(pairs):
    return frozenset(map(tuple, pairs))


def main():
    receipts = []
    for receipt_path in sorted(ROOT.glob('*.receipt.json')):
        receipt = json.loads(receipt_path.read_text())
        packed = (ROOT / receipt['body_gzip']).read_bytes()
        raw = gzip.decompress(packed)
        assert sha(raw) == receipt['body_sha256']
        assert len(raw) == receipt['body_bytes']
        assert sha(packed) == receipt['gzip_sha256']
        receipts.append({'receipt': receipt_path.name, 'status': receipt['status'],
                         'body_bytes': len(raw), 'body_sha256': sha(raw),
                         'error': receipt['error']})
        if receipt['status'] == 200 and receipt_path.stem not in ['fever-dev.receipt', 'original-zenodo.receipt']:
            if receipt_path.stem in ['fever-download-page.receipt', 'producer-readme.receipt']:
                quoted = b''.join((json.dumps(line, ensure_ascii=False) + '\n').encode()
                                  for line in raw.decode().splitlines(keepends=True))
                emit(ROOT / receipt_path.name.replace('.receipt.json', '.lines.jsonl'), quoted)
            else:
                emit(ROOT / receipt_path.name.replace('.receipt.json', '.body'), raw)

    raw_original = gzip.decompress((ROOT / 'fever-dev.body.gz').read_bytes())
    zenodo_raw = gzip.decompress((ROOT / 'original-zenodo.body.gz').read_bytes())
    assert raw_original == zenodo_raw
    zenodo_receipt = json.loads((ROOT / 'original-zenodo.receipt.json').read_text())
    original_md5 = hashlib.md5(raw_original).hexdigest()
    assert zenodo_receipt['headers']['oc-checksum'] == 'MD5:' + original_md5
    original_rows = [json.loads(line) for line in raw_original.splitlines()]
    original = {r['id']: (line, r) for line, r in enumerate(original_rows, 1)}
    assert len(original) == len(original_rows)
    raw_installed = INSTALLED.read_bytes()
    installed = [json.loads(line) for line in raw_installed.splitlines()]
    counts = collections.Counter()
    seen_groups = collections.defaultdict(set)
    seen_original_ids = set()
    seen_non_nei_ids = set()
    inventory, examples = [], []
    for line, row in enumerate(installed, 1):
        counts['installed_rows'] += 1
        counts['original_id_present'] += 'original_id' in row
        original_line, source = original[row['original_id']]
        seen_original_ids.add(source['id'])
        counts['original_id_matches'] += 1
        for key in ['claim', 'label', 'verifiable']:
            counts[key + '_matches'] += row[key] == source[key]
        pairs = [normalized(e[0], e[1]) for e in row['evidence']]
        groups = [group_pairs(g) for g in source['evidence']]
        as_set = pair_set(pairs)
        exact_set_indices = [i for i, g in enumerate(groups) if as_set == pair_set(g)]
        ordered_indices = [i for i, g in enumerate(groups) if pairs == g]
        record = {'installed_line': line, 'export_id': row['id'],
                  'original_id': row['original_id'], 'original_line': original_line,
                  'installed_row_sha256': sha(canonical(row)),
                  'original_row_sha256': sha(canonical(source)),
                  'label': row['label'], 'export_pair_count': len(pairs),
                  'original_group_indices_set_equal': exact_set_indices,
                  'original_group_indices_ordered_equal': ordered_indices}
        inventory.append(record)
        if row['label'] == 'NOT ENOUGH INFO':
            counts['nei_rows'] += 1
            continue
        seen_non_nei_ids.add(source['id'])
        counts['non_nei_rows'] += 1
        counts['non_nei_complete_group_set_equal_rows'] += bool(exact_set_indices)
        counts['non_nei_complete_group_ordered_equal_rows'] += bool(ordered_indices)
        counts['non_nei_multisentence_rows'] += len(as_set) > 1
        seen_groups[source['id']].add(as_set)
        singleton_invalid = [list(pair) for pair in sorted(as_set)
                             if not any(pair_set(g) <= {pair} for g in groups)]
        counts['non_nei_rows_with_original_insufficient_singleton'] += bool(singleton_invalid)
        counts['original_insufficient_export_singleton_occurrences'] += len(singleton_invalid)
        if singleton_invalid and len(examples) < 3:
            examples.append(dict(record, export_pairs=pairs, original_group_pairs=groups,
                                 original_insufficient_singletons=singleton_invalid))
    original_group_count = 0
    absent_group_count = 0
    original_ids_missing_groups = 0
    for original_id in sorted(seen_non_nei_ids):
        source = original[original_id][1]
        all_groups = {pair_set(group_pairs(g)) for g in source['evidence']}
        original_group_count += len(all_groups)
        absent = all_groups - seen_groups[original_id]
        absent_group_count += len(absent)
        original_ids_missing_groups += bool(absent)
    counts.update(original_release_rows=len(original_rows),
                  installed_unique_original_ids=len(seen_original_ids),
                  installed_unique_non_nei_original_ids=len(seen_non_nei_ids),
                  original_non_nei_distinct_groups_for_represented_ids=original_group_count,
                  original_groups_absent_from_valid_for_represented_non_nei_ids=absent_group_count,
                  represented_non_nei_ids_with_groups_absent_from_valid=original_ids_missing_groups)
    inventory_raw = b''.join(canonical(r) + b'\n' for r in inventory)
    packed_inventory = gzip.compress(inventory_raw, mtime=0)
    emit(ROOT / 'row-correspondence.jsonl.gz', packed_inventory)
    emit(ROOT / 'examples.json', (json.dumps(examples, ensure_ascii=False, indent=2) + '\n').encode())
    source_lines = []
    for example in examples:
        for path, line, source_raw in [
                (str(INSTALLED), example['installed_line'], raw_installed),
                ('fever-dev.body.gz (decompressed)', example['original_line'], raw_original)]:
            source_lines.append({'file': path, 'line': line, 'file_sha256': sha(source_raw),
                                 'raw_line': source_raw.splitlines()[line - 1].decode()})
    emit(ROOT / 'source-examples.jsonl', b''.join(canonical(r) + b'\n' for r in source_lines))
    hashes = {}
    for path in [REPO / 'data/datasets/fever.py',
                 REPO / 'data/scaffolds/qa/evidence_scorers.py',
                 REPO / 'tests/fixtures/hg_e1_review/fever-create-nli-dataset.py',
                 REPO / 'tests/fixtures/hg_e1_review/fever-hub-proxy-tree.body']:
        hashes[str(path.relative_to(REPO))] = sha(path.read_bytes())
    tree = json.loads((REPO / 'tests/fixtures/hg_e1_review/fever-conversion-tree.body').read_text())
    tree_entries = {entry['path']: entry['sha'] for entry in tree['tree']}
    producer_blobs = {}
    for name, tree_path in [('producer-readme', 'README.md'),
                            ('producer-merge', 'scripts/merge_nli_files.py'),
                            ('producer-nei', 'scripts/aggregate_papelo_nei.py')]:
        body = gzip.decompress((ROOT / (name + '.body.gz')).read_bytes())
        blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        assert blob == tree_entries[tree_path]
        producer_blobs[name] = {'tree_path': tree_path, 'git_blob_sha1': blob,
                                'sha256': sha(body), 'matches_preserved_pinned_tree': True}
    summary = {'scope': 'full installed valid.jsonl versus public original dev; no admitted selection or run',
               'installed_path': str(INSTALLED), 'installed_bytes': len(raw_installed),
               'installed_sha256': sha(raw_installed),
               'installed_git_blob_sha1': hashlib.sha1(b'blob ' + str(len(raw_installed)).encode()
                                                     + b'\0' + raw_installed).hexdigest(),
               'original_body_sha256': sha(raw_original), 'original_body_md5': original_md5,
               'official_download_and_linked_zenodo_bytes_equal': True, 'counts': dict(counts),
               'normalization': 'page Unicode NFC; line int; group pair-set equality and ordered equality reported separately',
               'inventory_sha256': sha(inventory_raw), 'inventory_gzip_sha256': sha(packed_inventory),
               'source_sha256': hashes, 'producer_blobs': producer_blobs,
               'acquisitions': receipts,
               'producer_revision_bound_to_export': None, 'selected_manifest': None,
               'run_id': None, 'scorer_executed': False, 'blocker_closed': False}
    emit(ROOT / 'observations.json', (json.dumps(summary, indent=2, ensure_ascii=False) + '\n').encode())
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
