"""Capture exact original installed-pair failure in a denied network namespace."""
import importlib.metadata as md
import json
from pathlib import Path
import sys
print(json.dumps({'executable': sys.executable, 'gensim': md.version('gensim'),
                  'scipy': md.version('scipy')}, indent=2), flush=True)
import gensim
