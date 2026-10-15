#!/usr/bin/env python3
import subprocess
import sys
raise SystemExit(subprocess.call([sys.executable, '-m', 'pip', 'download', '--no-index',
    '--no-cache-dir', '--no-deps', '--find-links=/tmp/hg-wwheelhouse-payloads-e5uywviu',
    '--dest', sys.argv[2], sys.argv[1]]))
