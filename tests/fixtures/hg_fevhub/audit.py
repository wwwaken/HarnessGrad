#!/usr/bin/env python3
"""Offline inventory/checks over this packet only; never imports upstream code."""
import base64
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent

def digest(b):
    return hashlib.sha256(b).hexdigest()

def git_blob(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()

def read(name):
    return json.loads((P / (name + '.body')).read_text())

records = sorted((json.loads(f.read_text()) for f in P.glob('*.request.json')),
                 key=lambda r: (r['started_utc'], r['name']))
by_url = {}
for r in records:
    if r.get('status') is not None and r.get('sha256'):
        body = (P / r['body']).read_bytes() if 'body' in r else Path(r['body_external']).read_bytes()
        assert len(body) == r['bytes'] and digest(body) == r['sha256'], r['name']
        if r['status'] == 200:
            by_url[r['url']] = r
        if r['status'] == 200 and r['url'].startswith('https://api.github.com/'):
            x = json.loads(body)
            if isinstance(x, dict) and x.get('encoding') == 'base64' and 'content' in x:
                decoded = base64.b64decode(x['content'])
                assert git_blob(decoded) == x['sha'], r['name']
                (P / (r['name'] + '.decoded.txt')).write_bytes(decoded)
    elif r.get('status') is None:
        assert not r.get('sha256') and not r.get('body'), r['name']
    for d in r['redirects']:
        assert digest(bytes.fromhex(d['body_hex'])) == d['body_sha256']

lines = ['# HTTP request inventory', '',
         'GET; HTTPS with default CA/hostname verification. No account token. Bodies are exact response entities (Accept-Encoding: identity).',
         'NULL means no HTTP response/status/body observed. Full headers, redirect bodies/statuses, proxy and observed UTC times: each `<name>.request.json`.', '',
         '| Name / receipt | URL | HTTP status | Bytes | Response SHA-256 |',
         '| --- | --- | --- | ---: | --- |']
for r in records:
    lines.append('| '+r['name']+' | '+r['url']+' | '+str(r['status'])+' | '+str(r.get('bytes', 'unobserved'))+' | '+r.get('sha256', 'unobserved: '+r.get('error',''))+' |')
(P / 'requests.md').write_text('\n'.join(lines)+'\n')

scope = {'definition': 'Inventories are searched metadata, not retrieved export/NEI payloads.',
         'main_history': [], 'generated_history': [], 'source_histories': {},
         'github_ref_trees': [], 'cards': [], 'loaders': []}
main = read('hub-commits')
gen = read('hub-parquet-commits') + read('hub-parquet-history-page2')
assert len({x['id'] for x in gen}) == len(gen)
main_ids = {x['id'] for x in main}
for group, commits in [('main_history', main), ('generated_history', [x for x in gen if x['id'] not in main_ids])]:
    for c in commits:
        url = 'https://huggingface.co/api/datasets/copenlu/fever_gold_evidence/tree/'+c['id']+'?recursive=true'
        r = by_url.get(url)
        if r is None:
            prefix = ('hub-tree-' if group == 'main_history' else 'parquet-tree-') + c['id']
            r = next((q for q in records if q['status'] == 200 and q['name'].startswith(prefix)), None)
        scope[group].append({'commit': c, 'tree_state': 'FOUND' if r else 'UNKNOWN',
                             'tree_response': r['body'] if r else None,
                             'tree': json.loads((P/r['body']).read_text()) if r else None})
for key in ['create_nli_dataset-py','aggregate_papelo_nei-py','merge_nli_files-py','README-md']:
    cs = read('gh-history-'+key)
    scope['source_histories'][key] = cs
for r in records:
    if r['status'] != 200: continue
    name = r['name']
    if name.startswith('gh-tree') or name == 'papelo-tree':
        tree = read(name); assert tree['truncated'] is False
        scope['github_ref_trees'].append({'name': name, 'sha': tree['sha'], 'tree': tree['tree']})
    if name.startswith('hub-card') or name.startswith('hub-loader'):
        b = (P/r['body']).read_bytes()
        scope['cards' if name.startswith('hub-card') else 'loaders'].append(
            {'name': name, 'url': r['url'], 'body': r['body'], 'sha256': digest(b), 'git_blob': git_blob(b)})
# The PR diff carries one complete old README hunk, including its original CRLF bytes.
old_lines = []
in_hunk = False
previous_old = False
for line in (P/'hub-pr-diff.body').read_bytes().splitlines(keepends=True):
    if line.startswith(b'@@'):
        assert not in_hunk
        in_hunk = True
        continue
    if not in_hunk:
        continue
    if line.startswith((b'-', b' ')):
        old_lines.append(line[1:])
        previous_old = True
    elif line.startswith(b'+'):
        previous_old = False
    elif line.startswith(b'\\ No newline'):
        if previous_old:
            old_lines[-1] = old_lines[-1].removesuffix(b'\n')
    else:
        raise AssertionError(repr(line))
old_card = b''.join(old_lines)
assert git_blob(old_card) == '4a5ce872c186404a8ebdc7f860479eaeec0a08b4'
(P/'hub-pr-diff.old-card.txt').write_bytes(old_card)
scope['cards'].append({'name':'old-card-recovered-from-pr-diff',
    'url':'https://huggingface.co/datasets/copenlu/fever_gold_evidence/discussions/1/files.diff',
    'body':'hub-pr-diff.old-card.txt', 'sha256':digest(old_card),
    'git_blob':git_blob(old_card), 'source_response':'hub-pr-diff.body'})
expected = {}
for item in scope['main_history']:
    for obj in item['tree'] or []:
        if obj['path'] in ('README.md', 'fever_gold_evidence.py'):
            expected[obj['oid']] = {'path': obj['path'], 'oid': obj['oid'], 'size': obj['size']}
for oid, obj in expected.items():
    hits = [x for x in scope['cards'] + scope['loaders'] if x['git_blob'] == oid]
    obj.update(state='FOUND' if hits else 'UNKNOWN', responses=[x['body'] for x in hits])
scope['hub_text_objects'] = list(expected.values())
(P / 'scope.json').write_text(json.dumps(scope, indent=2, ensure_ascii=False)+'\n')

# Exact regex/scope and line matches retained separately; absence claims require manual reading as well.
pattern = r'fever_gold_evidence|valid\.jsonl|create_nli_dataset|aggregate_papelo_nei|merge_nli_files|papelo|original_id|uuid|annotation|random\.seed|predicted_sentences|zenodo|checksum|revision|receipt|execution'
files = sorted(set([P/r['body'] for r in records if r.get('status')==200 and 'body' in r and (
    r['name'].startswith(('hub-card','hub-loader')) or r['name'] in ['gh-commits','gh-issues','gh-actions','gh-comments-1','gh-comments-3','gh-comments-4','gh-comments-5','hub-discussions','hub-discussion-1','server-info','server-parquet','server-splits','hub-commits','hub-parquet-commits','hub-parquet-history-page2','hub-metadata-full','hub-refs-retry','hub-pr-diff','gh-history-create_nli_dataset-py','gh-history-aggregate_papelo_nei-py','gh-history-merge_nli_files-py','gh-history-README-md'])]
    + list(P.glob('*.decoded.txt')) + [P/'paper-pdf.txt', P/'paper-html.body', P/'hub-pr-diff.old-card.txt']))
search = {'command': 'python3 tests/fixtures/hg_fevhub/audit.py', 'regex': pattern,
          'flags': 're.IGNORECASE; splitlines(); UTF-8 errors=replace',
          'enumerated_files': [str(f.relative_to(P)) for f in files], 'matches': []}
for f in files:
    for i,line in enumerate(f.read_text(errors='replace').splitlines(),1):
        if re.search(pattern, line, re.IGNORECASE):
            search['matches'].append({'file':str(f.relative_to(P)), 'line':i,'text':line})
(P/'search.json').write_text(json.dumps(search, indent=2, ensure_ascii=False)+'\n')
assert (P/'search.json').stat().st_size < 1_000_000
stats = {'http_requests':len(records), 'http_responses':sum(r['status'] is not None for r in records),
         'http_200':sum(r['status']==200 for r in records),
         'transport_failures':sum(r['status'] is None for r in records),
         'main_commits':len(main), 'generated_only_commits':len(scope['generated_history']),
         'main_trees_found':sum(x['tree_state']=='FOUND' for x in scope['main_history']),
         'generated_trees_found':sum(x['tree_state']=='FOUND' for x in scope['generated_history']),
         'hub_card_versions':len({x['git_blob'] for x in scope['cards']}),
         'hub_loader_versions':len({x['git_blob'] for x in scope['loaders']}),
         'source_history_versions':{k:len(v) for k,v in scope['source_histories'].items()},
         'search_files':len(files), 'search_matching_lines':len(search['matches']),
         'verified_base64_blobs':len(list(P.glob('*.decoded.txt')))}
(P/'audit-summary.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,sort_keys=True))
