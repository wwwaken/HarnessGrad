"""Local import-only inventory; deny network and never call a scorer/task."""
import argparse
import importlib
import importlib.metadata
import importlib.util
import json
import pathlib
import socket
import sys
import sysconfig

parser = argparse.ArgumentParser()
parser.add_argument('module')
parser.add_argument('--source')
args = parser.parse_args()

def deny_network(event, values):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind'):
        raise RuntimeError('network prohibited during import-only inspection: ' + event)
sys.addaudithook(deny_network)
before = set(sys.modules)
error = None
try:
    if args.source:
        spec = importlib.util.spec_from_file_location(args.module, args.source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        importlib.import_module(args.module)
except Exception as exc:
    error = repr(exc)
modules = []
for name in sorted(set(sys.modules) - before):
    module = sys.modules[name]
    origin = getattr(module, '__file__', None)
    modules.append({'module': name, 'file': origin})
packages = {}
package_distributions = importlib.metadata.packages_distributions()
for name in sorted({m['module'].split('.')[0] for m in modules}):
    candidates = package_distributions.get(name, [])
    for distname in candidates:
        d = importlib.metadata.distribution(distname)
        packages[distname] = {'version': d.version, 'requires_dist': d.requires,
                              'metadata': str(d._path / 'METADATA')}
print(json.dumps({'inspection': 'import-only; no scorer/task called; network denied',
                  'command': sys.argv, 'python_version': sys.version,
                  'executable': sys.executable, 'soabi': sysconfig.get_config_var('SOABI'),
                  'error': error, 'modules': modules, 'packages': packages}, indent=2))
