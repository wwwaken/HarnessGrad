"""Only exact named import statements found by the static context census."""
from gensim.models import Word2Vec
from gensim.test.utils import common_texts
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
import tensorflow as tf
import xgboost.sklearn as xgb
import importlib.metadata as md
import json
from pathlib import Path
import sys
from packaging.requirements import Requirement

selected = json.loads(Path(sys.argv[1]).read_text())['install']
checked = []
for item in selected:
    name = item['metadata']['name']
    distribution = md.distribution(name)
    assert distribution.version == item['metadata']['version'], (name, distribution.version)
    for text in distribution.requires or []:
        requirement = Requirement(text)
        if requirement.marker and not requirement.marker.evaluate({'extra': ''}):
            continue
        actual = md.version(requirement.name)
        assert actual in requirement.specifier, (name, text, actual)
        checked.append({'parent': name, 'requirement': text, 'installed_version': actual})
assert all(item is not None for item in [Word2Vec, common_texts, Dense, Sequential, tf, xgb])
print(json.dumps({'exact_import_statements_passed': [
    'from gensim.models import Word2Vec', 'from gensim.test.utils import common_texts',
    'from tensorflow.keras.layers import Dense', 'from tensorflow.keras.models import Sequential',
    'import tensorflow as tf', 'import xgboost.sklearn as xgb'],
    'selected_dependency_checks': checked, 'checked_requirement_count': len(checked),
    'scope': 'Selected added scientific dependency graph only; other DS1000 imports retain source-led --no-deps scope.',
    'prefix': sys.prefix, 'no_constructors_or_task_code_executed': True}, indent=2))
