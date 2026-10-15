"""Build line-addressable evidence index from retained metadata and source bytes."""
import base64
import hashlib
import json
import pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            url = dict(attrs).get('href')
            if url:
                self.urls.append(url)


def build():
    for response, filename in [('project-converter-blob-direct', 'project-converter.py'),
                               ('project-readme-current', 'project-current-README.md')]:
        obj = json.loads((ROOT / 'responses' / (response + '.body')).read_bytes())
        dest = ROOT / 'decoded' / filename
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(base64.b64decode(obj['content']))
    paths = ['data/datasets/triviaqa.py',
             'tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py',
             'tests/fixtures/triviaqa_upstream/utils/dataset_utils.py',
             'tests/fixtures/triviaqa_upstream/provenance.json',
             'tests/fixtures/triviaqa_hub_codex225/historical_loader/dataset_infos.json']
    write_json('source-identities.json', [dict(path=p, bytes=len((REPO / p).read_bytes()),
               sha256=hashlib.sha256((REPO / p).read_bytes()).hexdigest()) for p in paths])
    parser = Links()
    parser.feed((ROOT / 'responses/paper-artifact-page.body').read_text())
    write_json('paper-link-inventory.json', dict(
        source='responses/paper-artifact-page.body',
        scope='All href attributes of HTML a elements; no paper PDF/source or data links fetched',
        links=sorted(set(parser.urls))))
    records = []
    roots = []
    for p in sorted((ROOT / 'responses').glob('*.receipt.json')):
        receipt = json.loads(p.read_text())
        records.append((p, receipt))
        if receipt['name'].startswith('history-root-'):
            root = dict(name=receipt['name'], url=receipt['url'],
                        status=receipt.get('status'), error=receipt.get('error'),
                        receipt=str(p.relative_to(ROOT)))
            if receipt.get('status') == 200:
                entries = json.loads((ROOT / receipt['body']).read_bytes())
                root['root_paths'] = [i['path'] for i in entries]
                root['loader_and_info_declarations'] = [i for i in entries
                    if i['path'] in ['trivia_qa.py', 'dataset_infos.json']]
            roots.append(root)
    write_json('history-root-inventory.json', roots)
    lines = ['# Exact response catalog — w-trivia2', '',
             'FOUND means bytes were retrieved, including error responses; it does not mean a receipt was found.',
             'UNKNOWN means no HTTP response was observed. Every body is exact, unmodified received bytes.',
             'JSON views are parsed/indented copies. Digests below are locally recomputed SHA-256 of raw bodies.',
             'Requests and headers (including pagination Link, when supplied) are in the linked receipts.', '',
             '| Request name | State / HTTP | URL | Bytes | SHA-256 | Verbatim excerpt / error | Evidence |',
             '| --- | --- | --- | ---: | --- | --- | --- |']
    for p, record in records:
        if 'body' in record:
            body = (ROOT / record['body']).read_bytes()
            assert hashlib.sha256(body).hexdigest() == record['sha256']
            text = body.decode('utf-8')
            try:
                obj = json.loads(text)
            except ValueError:
                excerpt = next((s for s in text.splitlines() if s.strip()), '')[:90]
            else:
                if isinstance(obj, list) and obj:
                    first = obj[0]
                    excerpt = first.get('title', first.get('path', first.get('commit', {}).get('message', '')))[:90]
                elif isinstance(obj, dict) and 'dataset_info' in obj:
                    excerpt = '"pending":[]' if '"pending":[]' in text else text[:90]
                elif isinstance(obj, dict) and 'sha' in obj:
                    excerpt = obj['sha']
                else:
                    excerpt = text[:90]
            state = 'FOUND / ' + str(record['status'])
            digest, size = record['sha256'], record['bytes']
            evidence = (f"`{ROOT.relative_to(REPO) / record['body']}:1`; "
                        f"`{p.relative_to(REPO)}:1`")
        else:
            state, digest, size = 'UNKNOWN / unobserved', 'unobserved', 'unobserved'
            excerpt = record['error']
            evidence = f'`{p.relative_to(REPO)}:1`'
        excerpt = excerpt.replace('\n', ' ').replace('|', '\\|').replace('`', '\\`')
        lines.append(f"| {record['name']} | {state} | {record['url']} | {size} | `{digest}` | `{excerpt}` | {evidence} |")
    (ROOT / 'response-catalog.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(dict(indexed_requests=len(records),
                         indexed_history_root_attempts=len(roots),
                         paper_link_count=len(set(parser.urls))), sort_keys=True))


if __name__ == '__main__':
    build()
