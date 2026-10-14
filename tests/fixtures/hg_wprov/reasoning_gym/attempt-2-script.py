#!/usr/bin/env python3
"""CPU-only, read-only generated-pool custody check; never invokes score_answer.

Uses the currently installed package after verify.py authenticates its member hashes.
Audit hooks deny Python socket/process/file-write operations. They are a check on this
provenance tool, not a claim of production sandbox enforcement or scorer closure.
"""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import sys
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def deny_side_effects(event, args):
    if event == 'os.mkdir' and Path(args[0]).is_dir():
        # Path.mkdir(exist_ok=True) probes already-existing config directories.
        return
    if event.startswith(('socket.', 'subprocess.')) or event in {
        'os.system', 'os.exec', 'os.posix_spawn', 'os.fork', 'os.forkpty',
        'os.remove', 'os.rename', 'os.mkdir', 'os.rmdir', 'os.chmod', 'os.link', 'os.symlink',
    }:
        raise RuntimeError(f'provenance regeneration denies {event}')
    if event == 'open':
        _path, mode, flags = args
        if (mode and any(c in mode for c in 'wax+')) or (flags and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
            raise RuntimeError('provenance regeneration denies file writes')


def constants(path):
    names = {'PACKAGE', 'VERSION', 'SEED', 'PER_FAMILY', 'FAMILIES'}
    result = {}
    for node in ast.parse(path.read_bytes()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    result[target.id] = ast.literal_eval(node.value)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path, required=True)
    parser.add_argument('--pool', type=Path, required=True)
    args = parser.parse_args()
    config = constants(args.prepare)
    installed = importlib.metadata.distribution(config['PACKAGE'])
    if installed.version != config['VERSION']:
        raise RuntimeError('installed version disagrees; authenticate installed bytes first')
    dependency_versions = {}
    for requirement in installed.requires or []:
        from packaging.requirements import Requirement
        req = Requirement(requirement)
        if req.marker is None or req.marker.evaluate({'extra': ''}):
            dependency_versions[req.name] = importlib.metadata.version(req.name)
    expected_bytes = args.pool.read_bytes()
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 ** 3, 4 * 1024 ** 3))
    sys.dont_write_bytecode = True
    sys.addaudithook(deny_side_effects)
    started = time.monotonic()
    from reasoning_gym import create_dataset
    rows = []
    for family in config['FAMILIES']:
        for index in range(config['PER_FAMILY']):
            # Same construction order as prepare._entry; no scorer method is called.
            item = create_dataset(family, size=config['PER_FAMILY'], seed=config['SEED'])[index]
            rows.append({'family': family, 'index': index,
                         'question': str(item['question']).strip(),
                         'entry': json.loads(json.dumps(item, default=str))})
    body = ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows).encode()
    receipt = {
        'command': 'PYTHONDONTWRITEBYTECODE=1 timeout 180s python3 tests/fixtures/hg_wprov/reasoning_gym/regenerate.py --prepare data/datasets/reasoning_gym/prepare.py --pool /mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl',
        'interpreter': sys.executable, 'python_version': sys.version,
        'package': config['PACKAGE'], 'version': installed.version,
        'prepare_sha256': sha(args.prepare.read_bytes()),
        'regenerate_script_sha256': sha(Path(__file__).read_bytes()),
        'seed': config['SEED'], 'family_count': len(config['FAMILIES']),
        'items_per_family': config['PER_FAMILY'], 'row_count': len(rows),
        'dependency_versions': dependency_versions,
        'generated_size': len(body), 'generated_sha256': sha(body),
        'installed_pool_size': len(expected_bytes), 'installed_pool_sha256': sha(expected_bytes),
        'whole_pool_byte_equality': body == expected_bytes,
        'elapsed_seconds': time.monotonic() - started,
        'cpu_limit_seconds': 120, 'address_space_limit_bytes': 4 * 1024 ** 3,
        'network_and_process_audit_denials': True, 'file_write_audit_denials': True,
        'score_answer_calls': 0, 'model_gpu_pilot_execution': False,
        'scope': 'Observed interpreter and installed dependencies; does not prove behavioral eligibility, scorer offline closure, pristine runtime, or run selection.'}
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt['whole_pool_byte_equality'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
