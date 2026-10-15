"""Import-only observations; no benchmark adapters, constructors or scorers."""
import importlib
import json
from pathlib import Path
import re
import sys
import traceback

records = []
for name in sys.argv[1:]:
    try:
        importlib.import_module(name)
        records.append({'module': name, 'status': 'imported'})
    except Exception:
        records.append({'module': name, 'status': 'failed', 'traceback': traceback.format_exc()})
maps = Path('/proc/self/maps').read_text()
paths = sorted({line.split(None, 5)[-1] for line in maps.splitlines()
                if len(line.split(None, 5)) == 6 and line.split(None, 5)[-1].startswith('/')})
print(json.dumps({'requested': sys.argv[1:], 'records': records, 'maps': maps,
     'native_paths': paths,
     'module_files': sorted({str(getattr(m, '__file__')) for m in sys.modules.values()
                            if getattr(m, '__file__', None)})}, indent=2))
