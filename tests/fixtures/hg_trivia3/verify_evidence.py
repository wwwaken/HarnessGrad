"""Recompute payload-free findings offline from retained range/key evidence."""
import collections
import hashlib
import io
import itertools
import json
import pathlib
import struct
import sys

import pyarrow as pa
import pyarrow.parquet as pq

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXTERNAL = pathlib.Path('/mnt/20t/xubuqiang/hg-work/trivia3')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build():
    ranges, footers, inventories, sets, doc_sets = [], [], [], {}, {}
    tree = json.loads((ROOT / 'tests/fixtures/hg_trivia2/views/hub-tree-final.json').read_text())
    by_path = {v['path']: v for v in tree}
    for directory in sorted((EXTERNAL / 'ranges').iterdir()):
        receipt_path = directory / 'http-receipts.json'
        if not receipt_path.exists():
            continue
        receipts = json.loads(receipt_path.read_text())
        entry = by_path[directory.name.replace('__', '/')]
        cache = {}
        for r in receipts:
            b = pathlib.Path(r['raw_path']).read_bytes()
            assert len(b) == r['bytes'] and sha(b) == r['sha256']
            a, z = map(int, r['requested_range'][6:].split('-'))
            assert r['content_range'] == f'bytes {a}-{z}/{entry["size"]}'
            assert r['status'] == 206 and len(b) == z-a+1
            bindings = [v for v in r['redirect_bindings'] if v['repo_commit']]
            assert bindings and all(v['repo_commit'] == '0f7faf33a3908546c6fd5b73a660e0f8ff173c2f'
                and v['linked_etag'].strip('"') == entry['lfs']['oid'] for v in bindings)
            cache[a, z] = b
        tail = cache.get((entry['size']-8, entry['size']-1))
        if tail:
            length = struct.unpack('<I', tail[:4])[0]
            footer = cache.get((entry['size']-length-8, entry['size']-9))
            if footer:
                m = pq.read_metadata(pa.BufferReader(b'PAR1' + footer + tail))
                columns = [m.schema.column(i).path for i in range(m.num_columns)]
                allowed_columns = {'question_id', 'question_source',
                    'entity_pages.filename.list.item', 'entity_pages.doc_source.list.item',
                    'search_results.filename.list.item', 'search_results.doc_source.list.item'}
                allowed_ranges = set()
                for g in range(m.num_row_groups):
                    previous = None
                    for i, column in enumerate(columns):
                        if column not in allowed_columns:
                            previous = None
                            continue
                        c = m.row_group(g).column(i)
                        a = min(v for v in [c.dictionary_page_offset,c.data_page_offset]
                                if v is not None and v >= 0)
                        z = a + c.total_compressed_size-1
                        allowed_ranges.add((a,z))
                        if previous:
                            allowed_ranges.add((previous[0],z))
                        previous = (a,z)
                for r in receipts:
                    if r['purpose'] not in {'footer-tail','footer-metadata'}:
                        assert tuple(map(int,r['requested_range'][6:].split('-'))) in allowed_ranges
                footers.append({'path':entry['path'],'rows':m.num_rows,
                                'physical_column_paths':columns,
                                'human_answer_field_present':any('human' in c.lower() for c in columns),
                                'verification_or_domain_field_present':any(
                                    'verified' in c.lower() or 'domain' in c.lower() for c in columns)})
        ranges.append({'path':entry['path'],'receipt_file':str(receipt_path),
                       'receipt_sha256':sha(receipt_path.read_bytes()),
                       'requests':len(receipts),'bytes':sum(r['bytes'] for r in receipts)})
        if (directory / 'summary.json').exists():
            summary=json.loads((directory/'summary.json').read_text())
            inv=pathlib.Path(summary['identity_inventory']['path'])
            b=inv.read_bytes()
            assert sha(b)==summary['identity_inventory']['sha256']
            rows=[json.loads(s) for s in b.decode().splitlines()]
            assert len(rows)==summary['footer_row_count']
            class OfflineRangeFile(io.RawIOBase):
                def __init__(self):
                    self.pos=0
                def readable(self):
                    return True
                def seekable(self):
                    return True
                def tell(self):
                    return self.pos
                def seek(self,offset,whence=0):
                    self.pos=offset if whence==0 else (self.pos if whence==1 else entry['size'])+offset
                    return self.pos
                def read(self,n=-1):
                    assert n>=0
                    a,z=self.pos,self.pos+n-1
                    self.pos+=n
                    for (start,end),data in cache.items():
                        if start<=a<=z<=end:
                            return data[a-start:z-start+1]
                    raise AssertionError(('missing approved range',a,z))
            table=pq.ParquetFile(OfflineRangeFile(),metadata=m,pre_buffer=False,buffer_size=0).read(
                columns=summary['read_column_paths'],use_threads=False)
            reconstructed=[]
            for ordinal,row in enumerate(table.to_pylist()):
                item={'shard_ordinal':ordinal,'question_id':row['question_id'],
                      'question_source':row['question_source']}
                for group in ['entity_pages','search_results']:
                    if group in row:
                        item[group]=row[group]
                reconstructed.append(item)
            assert reconstructed==rows, 'key inventory differs from approved column bytes'
            qids=[r['question_id'] for r in rows]
            sets[entry['path']]=set(qids)
            keys=[r['question_id']+'--'+filename for r in rows
                  for group in ['entity_pages','search_results']
                  for filename in r.get(group,{}).get('filename',[])]
            doc_sets[entry['path']]=set(keys)
            doc_sources=collections.Counter(
                source for r in rows for group in ['entity_pages','search_results']
                for source in r.get(group,{}).get('doc_source',[]))
            inventories.append({'path':entry['path'],'rows':len(rows),
                'distinct_question_ids':len(set(qids)),
                'question_id_duplicate_excess':len(qids)-len(set(qids)),
                'candidate_doc_key_occurrences':len(keys),
                'distinct_candidate_doc_keys':len(set(keys)),
                'candidate_doc_key_duplicate_excess':len(keys)-len(set(keys)),
                'document_source_label_counts':dict(sorted(doc_sources.items())),
                'question_source_counts':dict(sorted(collections.Counter(r['question_source'] for r in rows).items())),
                'inventory':summary['identity_inventory']})
    intersections=[{'a':a,'b':b,'shared_question_ids':len(sets[a]&sets[b]),
                    'shared_candidate_doc_keys':len(doc_sets[a]&doc_sets[b])}
                   for a,b in itertools.combinations(sorted(sets),2)]
    measured_a='rc/validation-00002-of-00004.parquet'
    measured_b='rc/validation-00003-of-00004.parquet'
    return {'revision':'0f7faf33a3908546c6fd5b73a660e0f8ff173c2f',
        'scope':'Partial acquisition only; no official Domain/VerifiedEval filtering; no answers decoded.',
        'range_receipts':ranges,'footers':footers,'key_inventories':inventories,
        'intersections':intersections,
        'two_rc_shards':{'rows':sum(len(sets[s]) for s in [measured_a,measured_b]),
                         'distinct_question_ids':len(sets[measured_a]|sets[measured_b]),
                         'shared_question_ids':len(sets[measured_a]&sets[measured_b])},
        'official_numeric_denominator':'UNKNOWN',
        'human_answers_input_incidence_preservation_redundancy':'UNKNOWN'}


if __name__=='__main__':
    result=build()
    encoded=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    p=HERE/'observations.json'
    if '--write' in sys.argv:
        p.write_text(encoded)
    else:
        assert p.read_text()==encoded
    print(json.dumps({'verified':True,'range_requests':sum(r['requests'] for r in result['range_receipts']),
        'range_bytes':sum(r['bytes'] for r in result['range_receipts']),
        'complete_key_shards':len(result['key_inventories']),
        'complete_footers':len(result['footers']),
        'two_rc_shards':result['two_rc_shards'],'official_numeric_denominator':'UNKNOWN'},sort_keys=True))
