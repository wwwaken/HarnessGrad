"""Task-local scope guard, inherited by pytest and driver subprocesses.

Do not read/import the excluded adapter. Integrity snapshots retain all other
platform files. This guard is test invocation support, not a production change.
"""
import os
from pathlib import Path
import sys

ROOT = Path('/tmp/hg-t5')
DATA = ROOT / 'data'
EXCLUDED = DATA / 'agentdojo'
EXCLUDED_MODULE = DATA / 'agentdojo.py'

def forbidden(value):
    if not isinstance(value, (str, bytes, os.PathLike)):
        return False
    path = Path(os.fsdecode(value)).absolute()
    return path == EXCLUDED_MODULE or path == EXCLUDED or EXCLUDED in path.parents

def audit(event, args):
    if event == 'open' and forbidden(args[0]):
        raise PermissionError('t5 scope excludes this adapter')
    if event == 'import' and (args[0] == 'data.agentdojo' or args[0].startswith('data.agentdojo.')):
        raise ImportError('t5 scope excludes this adapter')

sys.addaudithook(audit)
_original_rglob = Path.rglob

def scoped_rglob(self, pattern):
    if self.absolute() == DATA and pattern == '*':
        for parent, dirs, files in os.walk(self):
            if Path(parent).absolute() == DATA:
                dirs[:] = [name for name in dirs if name != 'agentdojo']
                files = [name for name in files if name != 'agentdojo.py']
            for name in dirs + files:
                yield Path(parent) / name
    else:
        yield from _original_rglob(self, pattern)

Path.rglob = scoped_rglob
