"""Replay existing authored BIRD tests using the original check source only."""
from pathlib import Path
import subprocess
import tempfile
import pytest

root = Path(__file__).resolve().parents[3]
source = subprocess.run(['git', 'show', 'HEAD:data/datasets/bird_minidev/verify/check.py'],
                        cwd=root, capture_output=True, text=True, check=True).stdout
(Path(__file__).parent / 'baseline-bird-check.py.txt').write_text(source)
with tempfile.TemporaryDirectory(prefix='hg-hostpin-baseline-check-') as directory:
    path = Path(directory) / 'check.py'
    path.write_text(source)
    class Baseline:
        def pytest_collection_modifyitems(self, items):
            for item in items:
                item.module.CHECK = path
    raise SystemExit(pytest.main(['-q', str(root / 'tests/quality/test_bird_minidev_official_scorer.py'),
        '-k', 'transcription or ex_differential or check_scores or missing_answer or broken_environment or module_imports',
        '--basetemp=/tmp/hg-hostpin-pytest-bird-baseline'], plugins=[Baseline()]))
