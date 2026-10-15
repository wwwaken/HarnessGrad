"""Record the exact argv, output and return code of a source-only command."""
from pathlib import Path
import shlex
import subprocess
import sys

cmd = sys.argv[1:]
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
entry = '$ ' + shlex.join(cmd) + '\n' + result.stdout.decode(errors='replace')
entry += '\nEXIT ' + str(result.returncode) + '\n\n'
with Path('registry/w-stratsplit-validation.txt').open('a') as handle:
    handle.write(entry)
print(entry, end='')
sys.exit(result.returncode)
