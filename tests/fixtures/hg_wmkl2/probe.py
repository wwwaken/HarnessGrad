"""Import-only witnesses; no task, scoring, training, tensor or GPU operation."""
import importlib
import importlib.metadata as md
import json
from pathlib import Path
import sys
import traceback

names = ['mkl', 'numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib.pyplot', 'seaborn',
         'torch', 'PIL', 'yaml', 'statsmodels.api', 'gensim', 'gensim.models',
         'gensim.test.utils', 'tensorflow', 'tensorflow.keras.models',
         'tensorflow.keras.layers', 'xgboost', 'xgboost.sklearn']
results = {}
for name in names:
    try:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        assert path.is_relative_to(Path(sys.prefix)), (name, path, sys.prefix)
        results[name] = {'ok': True, 'path': str(path), 'version': getattr(module, '__version__', None)}
    except Exception as exc:
        results[name] = {'ok': False, 'exception': repr(exc), 'traceback': traceback.format_exc()}
# Verify named attributes from context imports without constructing models or data.
if results['gensim.models']['ok']:
    from gensim.models import Word2Vec
    from gensim.test.utils import common_texts
    assert Word2Vec is not None and common_texts is not None
versions = {name: md.version(name) for name in ['gensim', 'scipy', 'numpy', 'tensorflow-cpu', 'xgboost']}
assert versions == {'gensim': '4.3.2', 'scipy': '1.12.0', 'numpy': '1.26.4',
                    'tensorflow-cpu': '2.16.1', 'xgboost': '2.0.3'}, versions
maps = Path('/proc/self/maps').read_text().splitlines()
providers = sorted({line.split()[-1] for line in maps if any(x in line for x in ['libmkl', 'libiomp', 'libtbb'])})
assert providers and all(Path(path).is_relative_to(Path(sys.prefix)) for path in providers), providers
assert not any(str(Path(sys.base_prefix) / 'lib/python3.12/site-packages') in line for line in maps)
print(json.dumps({'imports': results, 'versions': versions, 'prefix': sys.prefix,
                  'base_prefix': sys.base_prefix, 'sys_path': sys.path, 'native_providers': providers,
                  'scope': 'Import and attribute presence only; no released task code or model construction.'}, indent=2))
raise SystemExit(any(not r['ok'] for r in results.values()))
