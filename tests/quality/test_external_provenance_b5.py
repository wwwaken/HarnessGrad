"""Offline provenance checks: code/metadata only, never custody approval."""
import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
import socket

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/external_provenance_b5'
# Integrity pin only. It is not an independent review or source-gate pin.
SUMS_SHA256 = 'aebf74434643e759983e0483787d069d6562873492d4c3c618a47cd9269ea30b'
BFCL_COMMIT = 'ea13468e4423454d0c213704fb87cf7cb3990433'
BFCL_TREE = 'b34aa53a73491f42dc69b8b18c92448d7c311f50'
HUB_REVISION = '0f7faf33a3908546c6fd5b73a660e0f8ff173c2f'
PREDECESSOR = 'd63a76f01c8226449f76b437dd512cf8b17adf5d'


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('offline provenance tests attempted network')
    monkeypatch.setattr(socket, 'socket', forbidden)
    monkeypatch.setattr(socket, 'create_connection', forbidden)


#: The upstream bodies this packet cannot hold, classified from the packet's OWN receipts and
#: from the committed replay report - never from a hand-written list, so the disposition cannot
#: drift away from the evidence. A payload under `tests/fixtures/**/*.body` is deliberately not
#: committed (`.gitignore:361-375`: "the EVIDENCE is the recomputed digest list, not the payload"),
#: so absent bodies are expected here; what must be checked is WHY each one is absent.
REPLAY_REPORT = ROOT / 'reports' / 'w-b5restore-replay3-20261015.jsonl'

#: GitHub's unauthenticated rate-limit body. It is recorded as `status: 403` for 23 unrelated blob
#: paths, all pinning this one digest - and distinct upstream artifacts cannot share a digest, so
#: for those paths the pin is provably an error page rather than the artifact.
RATE_LIMIT_SHA256 = 'fdfea826e425097e5c9a8837c28e99ba8458ba5b55987f027beb9c87b208284b'


def _pins():
    manifest = {}
    for line in (FIXTURE / 'SHA256SUMS').read_text().splitlines():
        if line.strip():
            digest, name = line.split('  ', 1)
            manifest[name] = digest
    return manifest


def _receipt(name):
    path = FIXTURE / (name[:-len('.body')] + '.receipt.json')
    return json.loads(path.read_text()) if path.is_file() else None


def _replay_outcomes():
    """`path -> outcome` over the committed replay report, or {} if it is not present."""
    if not REPLAY_REPORT.is_file():
        return {}
    out = {}
    for line in REPLAY_REPORT.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            if 'path' in row:
                out[row['path']] = row
    return out


def _dispositions():
    """Classify every pinned-but-absent body. Structural classes are derived, not declared."""
    pins = _pins()
    shared = {d for d in pins.values() if list(pins.values()).count(d) > 1}
    replay = _replay_outcomes()
    out = {}
    for name, digest in pins.items():
        if (FIXTURE / name).is_file():
            continue
        receipt = _receipt(name)
        status = receipt.get('status') if receipt else None
        recorded = (receipt or {}).get('response_body', {}).get('sha256')
        row = replay.get(name) or {}
        if status == 403 and recorded == digest and digest in shared:
            out[name] = 'pinned_error_payload'
        elif status == 404:
            out[name] = 'upstream_404'
        elif row.get('outcome') == 'mismatch' and row.get('recorded_status') == 200:
            out[name] = 'live_or_changed_resource'
        elif status == 200:
            out[name] = 'retryable'
        else:
            out[name] = 'unclassified'
    return out


#: Classes whose absence is explained by the packet's own records and cannot be repaired by
#: fetching: an error page pinned as an artifact, a resource that has moved, or a gone URL.
STRUCTURAL_ABSENCE = {'pinned_error_payload', 'upstream_404', 'live_or_changed_resource'}


def _require_payload(label):
    """Skip explicitly, naming the file and the recorded reason - the repo's convention for a
    pinned payload that is deliberately not committed (`test_w_ujson_receipts.py:38-40`,
    `test_quiesce_evidence.py:54-58`). Only a STRUCTURAL absence may skip; anything else must
    fail, because it is evidence we could still hold and do not."""
    name = f'responses/{label}.body'
    if (FIXTURE / name).is_file():
        return
    why = _dispositions().get(name, 'unclassified')
    assert why in STRUCTURAL_ABSENCE, (
        f'{name} is absent and its absence is {why!r}, which is not a structural reason - '
        f'a fetchable pinned body must not be skipped over')
    pytest.skip(f'{name} is absent with a recorded structural reason ({why}); the packet pins '
                f'{_pins().get(name, "?")[:16]}... and the body is deliberately not committed')


def response(label):
    return json.loads((FIXTURE / 'responses' / (label + '.body')).read_bytes())


def git_hash(kind, body):
    return hashlib.sha1(kind.encode() + b' ' + str(len(body)).encode() + b'\0' + body).hexdigest()


def tree_hash(entries):
    return git_hash('tree', b''.join(
        e['mode'].lstrip('0').encode() + b' ' + Path(e['path']).name.encode()
        + b'\0' + bytes.fromhex(e['sha']) for e in entries))


def test_inventory_and_every_raw_response_are_intact():
    sums = (FIXTURE / 'SHA256SUMS').read_bytes()
    assert hashlib.sha256(sums).hexdigest() == SUMS_SHA256
    dispositions = _dispositions()
    listed = set()
    for name, digest in _pins().items():
        path = FIXTURE / name
        assert path.resolve().is_relative_to(FIXTURE.resolve())
        if name in dispositions:
            # Absent. The packet's own receipts and the committed replay report must explain WHY,
            # and a body we could still fetch must not be quietly tolerated.
            if dispositions[name] not in STRUCTURAL_ABSENCE:
                fetchable = sorted(n for n, d in dispositions.items()
                                   if d not in STRUCTURAL_ABSENCE)
                raise AssertionError(
                    f'{name} is absent with disposition {dispositions[name]!r}; '
                    f'{len(fetchable)} pinned bodies are still fetchable and missing '
                    f'({fetchable[:4]}), so this packet is not at its honest floor')
            continue
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        listed.add(name)
    absent = set(dispositions)
    assert listed == ({str(p.relative_to(FIXTURE)) for p in FIXTURE.rglob('*')
                       if p.is_file() and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts}
                      - absent)
    # Every structural class must be represented by exactly the paths the records name, so a
    # future re-pin cannot silently move a body from `retryable` to `structural` either way.
    tally = {k: sorted(n for n, d in dispositions.items() if d == k) for k in STRUCTURAL_ABSENCE}
    assert tally['pinned_error_payload'], 'the 23 error-page pins are the packet\'s central defect'
    assert len(tally['pinned_error_payload']) == 23, tally['pinned_error_payload']
    assert len(tally['live_or_changed_resource']) == 3, tally['live_or_changed_resource']
    assert len(tally['upstream_404']) == 1, tally['upstream_404']
    inventory = json.loads((FIXTURE / 'inventory.json').read_bytes())
    assert inventory['custodian_approved'] is False
    assert inventory['independent_review'] is None
    assert inventory['production_authorized'] is inventory['measured'] is False
    for row in inventory['responses']:
        receipt = json.loads((ROOT / row['receipt']['path']).read_bytes())
        assert row['receipt']['sha256'] == hashlib.sha256(
            (ROOT / row['receipt']['path']).read_bytes()).hexdigest()
        if receipt['response_body'] is None:
            assert receipt['status'] is None and receipt['error']
            continue
        body_path = receipt['response_body']['path']
        if body_path in dispositions:
            # Structurally absent. Verify the recorded identity against the DERIVATION instead of
            # reading bytes that the payload policy keeps out of git and the records say are not
            # the artifact - and keep asserting the exact recorded status, so the error-page pins
            # stay pinned as error pages rather than becoming an unexamined gap.
            why = dispositions[body_path]
            assert why in STRUCTURAL_ABSENCE, (body_path, why)
            if why == 'pinned_error_payload':
                assert receipt['status'] == 403, body_path
                assert receipt['response_body']['sha256'] == RATE_LIMIT_SHA256, body_path
            elif why == 'upstream_404':
                assert receipt['status'] == 404, body_path
            else:
                assert receipt['status'] == 200, body_path
            continue
        body = (FIXTURE / body_path).read_bytes()
        assert len(body) == receipt['response_body']['bytes']
        assert hashlib.sha256(body).hexdigest() == receipt['response_body']['sha256']


def test_bfcl_tag_signed_commit_and_all_original_git_trees():
    tag = response('bfcl-tag')
    assert tag['object']['type'] == 'commit' and tag['object']['sha'] == BFCL_COMMIT
    commit = response('bfcl-commit')
    verification = commit['verification']
    header, message = verification['payload'].split('\n\n', 1)
    signed = (header + '\ngpgsig ' + verification['signature'].replace('\n', '\n ')
              + '\n\n' + message).encode()
    assert git_hash('commit', signed) == commit['sha'] == BFCL_COMMIT
    assert commit['tree']['sha'] == BFCL_TREE
    release = response('bfcl-release')
    assert release['tag_name'] == 'v1.3' and 'Leaderboard V3' in release['body']
    root = response('bfcl-root-tree')
    assert root['truncated'] is False
    assert tree_hash(root['tree']) == root['sha'] == BFCL_TREE
    recursive = response('bfcl-tree')
    assert recursive['truncated'] is False
    parents = {}
    by_path = {e['path']: e for e in recursive['tree']}
    for entry in recursive['tree']:
        parents.setdefault(str(Path(entry['path']).parent), []).append(entry)
    for parent, entries in parents.items():
        expected = BFCL_TREE if parent == '.' else by_path[parent]['sha']
        assert tree_hash(entries) == expected
    assert len(parents) == 93
    assert not any(e['path'].rsplit('/', 1)[-1] in ('LICENSE', 'NOTICE', 'COPYING')
                   for e in recursive['tree']
                   if e['path'].startswith('berkeley-function-call-leaderboard/'))


def test_bfcl_projection_matches_tree_and_retained_blob_bodies():
    inventory = json.loads((FIXTURE / 'inventory.json').read_bytes())['bfcl_v3']
    entries = {e['path']: e for e in response('bfcl-tree')['tree']}
    acquired = {}
    for path in (FIXTURE / 'responses').glob('bfcl-*.body'):
        try:
            api = json.loads(path.read_bytes())
        except ValueError:
            continue
        if isinstance(api, dict) and api.get('encoding') == 'base64' and 'content' in api:
            body = base64.b64decode(api['content'])
            assert len(body) == api['size']
            assert git_hash('blob', body) == api['sha']
            acquired[api['sha']] = body
    for item in inventory['files']:
        body = (ROOT / item['path']).read_bytes()
        assert len(body) == item['bytes'] == entries[item['original_path']]['size']
        assert hashlib.sha256(body).hexdigest() == item['sha256']
        assert git_hash('blob', body) == item['git_blob_sha1'] == entries[item['original_path']]['sha']
        assert item['archive_member_verified'] is False
        if item['path'].startswith('tests/fixtures/external_provenance_b5/'):
            assert acquired[item['git_blob_sha1']] == body
        if item['original_path'].endswith('.py'):
            ast.parse(body)  # Do not import or execute acquired code.
    assert inventory['archive']['body_downloaded'] is False
    assert inventory['archive']['digest_verified'] is False
    assert inventory['complete_import_closure'] is False
    assert inventory['source_gate_approved_pin'] is None
    modules = {f['original_path'].removeprefix('berkeley-function-call-leaderboard/')
               .removesuffix('.py').replace('/', '.')
               for f in inventory['files'] if f['original_path'].endswith('.py')}
    actual_missing = {m for f in inventory['files'] for m in f.get('imports', [])
                      if m.startswith('bfcl_eval.') and m not in modules}
    assert actual_missing == set(inventory['unacquired_imports'])


def test_changed_tree_and_code_cannot_reproduce_original_identities():
    tree = copy.deepcopy(response('bfcl-root-tree')['tree'])
    tree[0]['sha'] = '0' * 40
    assert tree_hash(tree) != BFCL_TREE
    loader = (FIXTURE / 'triviaqa/trivia_qa.py').read_bytes()
    assert git_hash('blob', loader + b'\n') != git_hash('blob', loader)


def test_triviaqa_mirror_revision_config_splits_and_file_metadata():
    meta = response('triviaqa-mirror-revision')
    assert meta['sha'] == HUB_REVISION
    card = meta['cardData']
    config = next(c for c in card['configs'] if c['config_name'] == 'rc.nocontext')
    assert config['data_files'] == [
        {'split': split, 'path': 'rc.nocontext/' + split + '-*'}
        for split in ('train', 'validation', 'test')]
    info = next(c for c in card['dataset_info'] if c['config_name'] == 'rc.nocontext')
    assert next(s for s in info['splits'] if s['name'] == 'validation')['num_examples'] == 17944
    root = response('triviaqa-mirror-tree')
    assert not any(e['path'].endswith('.py') for e in root)
    selected = response('triviaqa-selected-tree')
    # Verify LFS pointer blob identity without retrieving a single payload byte.
    for entry in selected:
        pointer = ('version https://git-lfs.github.com/spec/v1\n'
                   + 'oid sha256:' + entry['lfs']['oid'] + '\n'
                   + 'size ' + str(entry['lfs']['size']) + '\n').encode()
        assert len(pointer) == entry['lfs']['pointerSize']
        assert git_hash('blob', pointer) == entry['oid']
    selected_tree = [{'mode': '100644', 'path': e['path'], 'sha': e['oid']} for e in selected]
    assert tree_hash(selected_tree) == next(e['oid'] for e in root if e['path'] == 'rc.nocontext')
    assert selected == response('triviaqa-added-tree')


def test_triviaqa_predecessor_and_conversion_history_do_not_self_attest_execution():
    _require_payload('triviaqa-conversion-discussion')
    loader = (FIXTURE / 'triviaqa/trivia_qa.py').read_bytes()
    assert loader == (FIXTURE / 'responses/triviaqa-predecessor-loader.body').read_bytes()
    sha = git_hash('blob', loader)
    assert sha == 'a9a6932c23d378b9e5628ecec1f0509496806d77'
    for label in ('triviaqa-predecessor-tree', 'triviaqa-initial-tree', 'triviaqa-predelete-tree'):
        assert next(e['oid'] for e in response(label) if e['path'] == 'trivia_qa.py') == sha
    ast.parse(loader)
    assert b'Licensed under the Apache License, Version 2.0' in loader
    assert b'HumanAnswers' not in loader and b'VerifiedEval' not in loader
    commits = response('triviaqa-mirror-commits')
    assert [c['id'] for c in commits[:2]] == [HUB_REVISION, PREDECESSOR]
    discussion = response('triviaqa-conversion-discussion')
    assert discussion['num'] == 8 and discussion['status'] == 'merged'
    events = [e['data'] for e in discussion['events'] if e['type'] == 'commit']
    assert events[0]['parents'] == [PREDECESSOR]
    assert events[1]['subject'] == 'Add rc.nocontext data files'
    assert events[1]['parents'] == [events[0]['oid']]
    assert any(e['subject'] == 'Delete loading script' for e in events)
    manifest = json.loads((FIXTURE / 'inventory.json').read_bytes())['triviaqa']
    assert manifest['actual_converter_execution_attested'] is False
    assert manifest['conversion_execution_receipt_acquired'] is False
    assert manifest['mirror_independently_authenticated'] is False
    assert manifest['scorer_equivalence_certified'] is False
