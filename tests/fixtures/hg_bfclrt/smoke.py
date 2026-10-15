#!/usr/bin/env python3
"""OFFLINE IMPORT SMOKE ONLY. No scorer/handler call, inference, or network.

Run with -B. Network connection and child-process audit events are refused.
The BFCL scratch projection contains symlinks to the original retained bytes.
"""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import sysconfig


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'subprocess.Popen', 'os.system', 'os.exec'):
        raise RuntimeError('offline import smoke refused event: ' + event)


sys.addaudithook(audit)
sys.path.insert(0, '/mnt/20t/xubuqiang/hg-work/bfclrt/projection')
print(json.dumps({'kind': 'interpreter', 'executable': sys.executable,
                  'real_executable': os.path.realpath(sys.executable),
                  'executable_sha256': sha(sys.executable), 'version': sys.version,
                  'implementation': {'name': sys.implementation.name,
                                     'version': list(sys.implementation.version),
                                     'cache_tag': sys.implementation.cache_tag,
                                     'hexversion': sys.implementation.hexversion,
                                     '_multiarch': getattr(sys.implementation, '_multiarch', None)},
                  'platform': sysconfig.get_platform(),
                  'config': {k: sysconfig.get_config_var(k) for k in (
                      'SOABI', 'EXT_SUFFIX', 'MULTIARCH', 'ABIFLAGS', 'Py_DEBUG',
                      'CC', 'CFLAGS', 'CONFIG_ARGS', 'LDLIBRARY', 'LIBDIR')},
                  'sys_path': sys.path, 'kind_of_test': 'offline import smoke; NOT scorer execution'},
                 sort_keys=True), flush=True)
if sys.argv[1] == 'base':
    modules = ['numpy', 'pandas', 'requests', 'tqdm', 'dotenv', 'tenacity',
               'overrides', 'openai', 'anthropic', 'boto3',
               'tree_sitter', 'tree_sitter_java', 'tree_sitter_javascript',
               'cohere', 'mistralai', 'google.genai', 'qwen_agent.llm',
               'writerai', 'datamodel_code_generator',
               'bfcl_eval.model_handler.parser.java_parser',
               'bfcl_eval.model_handler.parser.js_parser']
else:
    modules = ['tree_sitter', 'tree_sitter_java', 'tree_sitter_javascript',
               'bfcl_eval.model_handler.parser.java_parser',
               'bfcl_eval.model_handler.parser.js_parser']
for name in modules:
    try:
        mod = importlib.import_module(name)
        path = getattr(mod, '__file__', None)
        row = {'kind': 'requested-import', 'module': name, 'status': 'FOUND imported',
               'path': path, 'sha256': sha(path) if path and Path(path).is_file() else None}
        if name == 'tree_sitter':
            row['Parser_has_set_language'] = hasattr(mod.Parser, 'set_language')
    except Exception as e:
        row = {'kind': 'requested-import', 'module': name, 'status': 'FAILED import',
               'exception': type(e).__name__, 'message': str(e)}
    print(json.dumps(row, sort_keys=True), flush=True)
for name, mod in sorted(sys.modules.copy().items()):
    path = getattr(mod, '__file__', None)
    if path and Path(path).is_file():
        print(json.dumps({'kind': 'observed-module', 'module': name, 'path': os.path.realpath(path),
                          'sha256': sha(path)}, sort_keys=True), flush=True)
    elif getattr(mod, '__spec__', None):
        print(json.dumps({'kind': 'observed-module', 'module': name,
                          'origin': mod.__spec__.origin, 'path': None}, sort_keys=True), flush=True)
mapped = set()
for line in Path('/proc/self/maps').read_text().splitlines():
    pieces = line.split(maxsplit=5)
    if len(pieces) == 6 and pieces[5].startswith('/'):
        p = Path(pieces[5])
        if p.is_file():
            mapped.add(p.resolve())
for p in sorted(mapped):
    print(json.dumps({'kind': 'observed-mapped-file', 'path': str(p),
                      'sha256': sha(p), 'bytes': p.stat().st_size}, sort_keys=True), flush=True)
