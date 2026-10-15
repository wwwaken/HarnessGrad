"""Render the optional local explainer under the inherited socket-denial filter."""
import subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[3]
raise SystemExit(subprocess.run([
    'node', '/home/xubuqiang/.agents/skills/answer-me-with-html/scripts/am.mjs',
    'render', str(root / 'tests/fixtures/hg_wwal/overview.md'),
    '-o', str(root / 'reports/w-wal-overview.html'), '--no-open'
], cwd=root, timeout=30).returncode)
