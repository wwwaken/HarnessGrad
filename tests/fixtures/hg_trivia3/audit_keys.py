"""Read pinned export metadata and identity columns only; never load answers.

Raw footer metadata and approved key column chunks stay outside git. Parquet
statistics are not inspected or emitted. No datasets/loader/scorer import.
"""
import collections
import concurrent.futures
import datetime
import hashlib
import io
import json
import pathlib
import struct
import sys
import urllib.parse

import pyarrow as pa
import pyarrow.parquet as pq
import requests

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
REV = '0f7faf33a3908546c6fd5b73a660e0f8ff173c2f'
PROXY = 'http://172.17.0.1:17890'
EXTERNAL = pathlib.Path('/mnt/20t/xubuqiang/hg-work/trivia3')
APPROVED = {'question_id', 'question_source', 'entity_pages.filename.list.item',
            'entity_pages.doc_source.list.item', 'search_results.filename.list.item',
            'search_results.doc_source.list.item'}


def digest(b):
    return hashlib.sha256(b).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


class RangeFile(io.RawIOBase):
    def __init__(self, entry, out):
        self.entry, self.out, self.pos = entry, out, 0
        self.allowed, self.cache, self.receipts = set(), {}, []
        self.session = requests.Session()
        self.session.proxies = {'https': PROXY}
        self.session.headers['Connection'] = 'close'
        old = out / 'http-receipts.json'
        if old.exists():
            self.receipts = json.loads(old.read_text())
            for r in self.receipts:
                b = pathlib.Path(r['raw_path']).read_bytes()
                assert len(b) == r['bytes'] and digest(b) == r['sha256']
                start, end = map(int, r['requested_range'][6:].split('-'))
                self.cache[start, end] = b

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else (self.pos if whence == 1 else self.entry['size']) + offset
        return self.pos

    def read(self, length=-1):
        assert length >= 0, 'unbounded reads prohibited'
        start, end = self.pos, self.pos + length - 1
        b = self.fetch(start, end, 'approved-column')
        self.pos += len(b)
        return b

    def fetch(self, start, end, purpose):
        if (start, end) in self.cache:
            return self.cache[start, end]
        for (a, b), data in self.cache.items():
            if a <= start <= end <= b:
                return data[start-a:end-a+1]
        assert 0 <= start <= end < self.entry['size']
        assert end - start < 2_000_000, 'per-range byte cap'
        if purpose in {'approved-column', 'adjacent-approved-columns'}:
            assert (start, end) in self.allowed, ('unapproved read', start, end)
        url = (f'https://huggingface.co/datasets/mandarjoshi/trivia_qa/resolve/{REV}/'
               f'{self.entry["path"]}')
        rec = {'url': url, 'method': 'GET', 'purpose': purpose,
               'requested_range': f'bytes={start}-{end}', 'proxy': PROXY,
               'requested_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'tls_verification': True}
        with self.session.get(url, headers={'Range': rec['requested_range'],
                                           'Accept-Encoding': 'identity'},
                              timeout=(20, 35), stream=True) as r:
            rec.update(status=r.status_code, content_range=r.headers.get('Content-Range'),
                       date=r.headers.get('Date'),
                       redirect_bindings=[{
                           'status': h.status_code,
                           'host': urllib.parse.urlsplit(h.url).netloc,
                           'repo_commit': h.headers.get('X-Repo-Commit'),
                           'linked_etag': h.headers.get('X-Linked-ETag'),
                           'linked_size': h.headers.get('X-Linked-Size'),
                       } for h in r.history])
            assert r.status_code == 206, rec
            assert rec['content_range'] == f'bytes {start}-{end}/{self.entry["size"]}', rec
            bindings = [v for v in rec['redirect_bindings'] if v['repo_commit']]
            assert bindings and all(v['repo_commit'] == REV and
                v['linked_etag'].strip('"') == self.entry['lfs']['oid'] and
                int(v['linked_size']) == self.entry['size'] for v in bindings), rec
            b = r.raw.read(end - start + 2)
            assert len(b) == end - start + 1, rec
        raw = self.out / f'{len(self.receipts):04d}-{start}-{end}.range'
        raw.write_bytes(b)
        rec.update(bytes=len(b), sha256=digest(b), raw_path=str(raw))
        self.receipts.append(rec)
        write_json(self.out / 'http-receipts.json', self.receipts)
        self.cache[start, end] = b
        return b


def audit(entry):
    out = EXTERNAL / 'ranges' / entry['path'].replace('/', '__')
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'summary.json').exists():
        return json.loads((out / 'summary.json').read_text())
    f = RangeFile(entry, out)
    size = entry['size']
    tail = f.fetch(size - 8, size - 1, 'footer-tail')
    assert tail[4:] == b'PAR1'
    length = struct.unpack('<I', tail[:4])[0]
    footer = f.fetch(size - length - 8, size - 9, 'footer-metadata')
    # Parse metadata from a compact buffer, avoiding PyArrow's 64 KiB file prefetch.
    meta = pq.read_metadata(pa.BufferReader(b'PAR1' + footer + tail))
    columns = [meta.schema.column(i).path for i in range(meta.num_columns)]
    write_json(out / 'footer-summary.json', {'path': entry['path'],
               'footer_row_count': meta.num_rows, 'row_groups': meta.num_row_groups,
               'physical_column_paths': columns})
    selected = [c for c in columns if c in APPROVED]
    if '.nocontext/' in entry['path']:
        selected = [c for c in selected if c in {'question_id', 'question_source'}]
    assert 'question_id' in selected and 'question_source' in selected
    for g in range(meta.num_row_groups):
        rg = meta.row_group(g)
        previous = None
        for i, col in enumerate(columns):
            if col not in selected:
                previous = None
                continue
            c = rg.column(i)
            start = min(v for v in [c.dictionary_page_offset, c.data_page_offset] if v is not None and v >= 0)
            f.allowed.add((start, start + c.total_compressed_size - 1))
            end = start + c.total_compressed_size - 1
            # Consecutive approved columns may be fetched together. No gap crosses
            # a nonapproved column. Exact individual chunk reads use this cache.
            if previous:
                a, b = previous
                f.allowed.add((a, end))
                f.fetch(a, end, 'adjacent-approved-columns')
                previous = None
            else:
                previous = (start, end)
    pf = pq.ParquetFile(f, metadata=meta, pre_buffer=False, buffer_size=0)
    table = pf.read(columns=selected, use_threads=False)
    assert table.num_rows == meta.num_rows
    config, filename = entry['path'].split('/')
    split = filename.split('-')[0]
    records = table.to_pylist()
    inventory = []
    for ordinal, row in enumerate(records):
        item = {'shard_ordinal': ordinal, 'question_id': row['question_id'],
                'question_source': row['question_source']}
        for group in ['entity_pages', 'search_results']:
            if group in row:
                item[group] = row[group]
        inventory.append(item)
    inv = out / 'identity-inventory.jsonl'
    with inv.open('w') as stream:
        for item in inventory:
            stream.write(json.dumps(item, ensure_ascii=False, separators=(',', ':')) + '\n')
    counts = collections.Counter(r['question_id'] for r in inventory)
    sources = collections.Counter(r['question_source'] for r in inventory)
    result = {'path': entry['path'], 'config': config, 'split': split,
              'declared_lfs_sha256': entry['lfs']['oid'],
              'whole_file_sha256_measured': False, 'bytes': size,
              'footer_row_count': meta.num_rows, 'row_groups': meta.num_row_groups,
              'physical_column_paths': columns, 'read_column_paths': selected,
              'qid_count': len(inventory), 'distinct_qids': len(counts),
              'duplicate_qid_values': sum(n > 1 for n in counts.values()),
              'duplicate_qid_excess': sum(n - 1 for n in counts.values()),
              'question_source_counts': dict(sorted(sources.items())),
              'identity_inventory': {'path': str(inv), 'bytes': inv.stat().st_size,
                                     'sha256': digest(inv.read_bytes())},
              'http_receipts': str(out / 'http-receipts.json'),
              'http_requests': len(f.receipts),
              'http_bytes_read': sum(r['bytes'] for r in f.receipts)}
    write_json(out / 'summary.json', result)
    f.session.close()
    print(json.dumps({k: result[k] for k in ['path', 'footer_row_count', 'distinct_qids',
                                          'http_requests', 'http_bytes_read']}), flush=True)
    return result


def main():
    tree = json.loads((ROOT / 'tests/fixtures/hg_trivia2/views/hub-tree-final.json').read_text())
    entries = [e for e in tree if e['path'].endswith('.parquet') and '/validation-' in e['path']]
    if '--one' in sys.argv:
        entries = [next(e for e in entries if e['path'].startswith('rc.nocontext/validation'))]
    write_json(EXTERNAL / 'validation-key-audit-plan.json', {'revision': REV, 'entries': entries,
               'approved_column_paths': sorted(APPROVED),
               'scope': 'All 19 validation shards across all 8 exported configs; train/test membership excluded.'})
    results, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(audit, e): e for e in entries}
        for future in concurrent.futures.as_completed(futures):
            entry = futures[future]
            try:
                results.append(future.result())
            except Exception as error:
                errors.append({'path': entry['path'], 'error': type(error).__name__ + ': ' + str(error)})
                print(json.dumps(errors[-1]), flush=True)
    write_json(HERE / ('one-summary.json' if '--one' in sys.argv else 'key-audit-summary.json'),
               {'revision': REV, 'pyarrow_version': pa.__version__,
                'results': sorted(results, key=lambda r: r['path']), 'errors': errors})
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
