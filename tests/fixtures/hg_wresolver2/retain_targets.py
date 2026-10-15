"""Commit exact requested artifact bytes; retain the full corpus externally."""
import json
from pathlib import Path
import shutil

from common import HERE, ROOT, digest, save, run

assert not (HERE / 'retained-targets.json').exists(), 'Never replace retained targets'
inputs = json.loads((HERE / 'inputs.json').read_text())
directory = HERE / 'payloads'
directory.mkdir()
records = []
for record in inputs['artifacts']:
    if record['key'] in {'spacy', 'contourpy', 'et-xmlfile'}:
        target = directory / Path(record['path']).name
        shutil.copyfile(record['path'], target)
        assert digest(target) == record['sha256']
        records.append({'key': record['key'], 'version': record['version'],
                        'path': str(target.relative_to(ROOT)), 'source': record['path'],
                        'bytes': target.stat().st_size, 'sha256': digest(target)})
save(HERE / 'retained-targets.json', records)
run('retained-target-sha256sum', ['sha256sum', *[ROOT / r['path'] for r in records]])
print(json.dumps({'retained_targets': len(records), 'bytes': sum(r['bytes'] for r in records)}))
