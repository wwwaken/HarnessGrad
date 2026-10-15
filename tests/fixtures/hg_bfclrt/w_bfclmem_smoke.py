#!/usr/bin/env python3
"""No-model offline ABI/API smoke. Does not import the official scorer."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SCRATCH = Path('/mnt/20t/xubuqiang/hg-work/bfclmem')

if '--child' in sys.argv:
    def denied(*args, **kwargs):
        raise RuntimeError('w-bfclmem offline smoke denies network')
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.create_connection = denied
    rows = []
    targets = {
        'tree_sitter': ['Language', 'Parser'],
        'tree_sitter_java': ['language'], 'tree_sitter_javascript': ['language'],
        'anthropic': ['Anthropic', 'AnthropicBedrock', 'RateLimitError'],
        'cohere': ['ClientV2'], 'mistralai': ['Mistral'],
        'google.genai': ['Client'],
        'google.genai.types': ['AutomaticFunctionCallingConfig', 'Content', 'GenerateContentConfig',
                               'Part', 'ThinkingConfig', 'Tool'],
        'datamodel_code_generator': ['InputFileType', 'DataModelType'],
        'datamodel_code_generator.model': ['get_data_model_types'],
        # BFCL minicpm_fc.py:150 chooses the <0.26.2 branch for 0.25.7.
        'datamodel_code_generator.format': ['PythonVersion'],
        'datamodel_code_generator.parser.jsonschema': ['JsonSchemaParser'],
        'datamodel_code_generator.model.pydantic_v2': ['BaseModel', 'DataModelField'],
        'qwen_agent.llm': ['get_chat_model'], 'writerai': ['Writer'],
    }
    for name, symbols in targets.items():
        try:
            m = importlib.import_module(name)
            found = {s: hasattr(m, s) for s in symbols}
            rows.append(dict(module=name, path=getattr(m, '__file__', None), symbols=found,
                             state='FOUND import/API' if all(found.values()) else 'API mismatch'))
            if name == 'datamodel_code_generator.format':
                rows.append(dict(module=name, optional_symbol='DatetimeClassType',
                                 present=hasattr(m, 'DatetimeClassType'),
                                 state='FOUND observation; >=0.26.2 branch not selected at 0.25.7'))
        except Exception as e:
            rows.append(dict(module=name, state='IMPORT FAILED', exception=type(e).__name__, detail=str(e)))
    for name, symbols in {'anthropic.types': ['TextBlock', 'ToolUseBlock'],
                          'google.genai.errors': ['APIError']}.items():
        try:
            m = importlib.import_module(name)
            found = {s: hasattr(m, s) for s in symbols}
            rows.append(dict(module=name, symbols=found,
                             state='FOUND import/API' if all(found.values()) else 'API mismatch'))
        except Exception as e:
            rows.append(dict(module=name, state='IMPORT FAILED', exception=type(e).__name__, detail=str(e)))
    try:
        ts = importlib.import_module('tree_sitter')
        for module, language, code in [('tree_sitter_java', 'java', b'class X { int x; }'),
                                       ('tree_sitter_javascript', 'javascript', b'f(x=1);')]:
            grammar = ts.Language(importlib.import_module(module).language(), language)
            parser = ts.Parser()
            parser.set_language(grammar)
            tree = parser.parse(code)
            rows.append(dict(grammar=language, language_abi=grammar.version,
                             runtime_min=getattr(ts, 'MIN_COMPATIBLE_LANGUAGE_VERSION', 'not exported'),
                             runtime_max=getattr(ts, 'LANGUAGE_VERSION', 'not exported'), root=tree.root_node.type,
                             has_error=tree.root_node.has_error, sexp=tree.root_node.sexp(),
                             state='FOUND old Language(pointer,name)/set_language/sexp API'))
    except Exception as e:
        rows.append(dict(state='GRAMMAR FAILED', exception=type(e).__name__, detail=str(e)))
    seen = set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        parts = line.split(None, 5)
        if len(parts) == 6 and parts[5].startswith('/'):
            p = Path(parts[5])
            if p not in seen and p.is_file():
                seen.add(p)
                b = p.read_bytes()
                rows.append(dict(loaded_path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                                 state='FOUND loaded file; build provenance not inferred'))
    for row in rows:
        print(json.dumps(row, sort_keys=True))
    sys.exit(0 if all(r.get('state') not in ['IMPORT FAILED', 'GRAMMAR FAILED', 'API mismatch'] for r in rows) else 1)

roots = ['tree_sitter==0.21.3', 'tree-sitter-java==0.21.0', 'tree-sitter-javascript==0.21.4',
         'anthropic==0.53.0', 'cohere==5.13.3', 'mistralai==1.7.0', 'google-genai==1.24.0',
         'datamodel-code-generator==0.25.7', 'qwen-agent==0.0.25', 'writer-sdk==2.1.0',
         'numpy==1.26.4', 'python-dotenv==1.2.2']
with tempfile.TemporaryDirectory(prefix='bfclmem-smoke-') as temp:
    site = Path(temp) / 'site'
    env = dict(os.environ, TMPDIR=temp, PYTHONDONTWRITEBYTECODE='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    cmd = [sys.executable, '-B', '-m', 'pip', 'install', '--no-index', '--no-compile',
           '--ignore-installed', '--find-links', str(SCRATCH / 'wheels'), '--target', str(site)] + roots
    with (SCRATCH / 'smoke-install.log').open('w') as f:
        result = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
    assert result.returncode == 0, (SCRATCH / 'smoke-install.log').read_text()
    code = 'import sys, runpy; sys.path.insert(0, sys.argv[1]); sys.argv=[sys.argv[2], "--child"]; runpy.run_path(sys.argv[0], run_name="__main__")'
    cmd = [sys.executable, '-I', '-S', '-B', '-c', code, str(site), str(Path(__file__).resolve())]
    result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Keep ephemeral paths explicit; archive/member hashes allow comparison after cleanup.
    (HERE / 'w-bfclmem-smoke.jsonl').write_text(result.stdout)
    (SCRATCH / 'smoke-stderr.txt').write_text(result.stderr)
    print('offline ABI/API smoke exit:', result.returncode)
    for line in result.stdout.splitlines():
        row = json.loads(line)
        if 'loaded_path' not in row:
            print(line)
    print('temporary site removed on exit')
    sys.exit(result.returncode)
