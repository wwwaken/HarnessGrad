"""A deliberately bounded native userland pin for the BIRD stdlib/SQLite scorer.

Hash while copying into sealed memfds; execute only those snapshots in an empty
bubblewrap root. Never hash then execute a mutable source path. Missing bytes,
manifest drift, missing namespace support, and startup failure are unmeasured.
The host kernel/CPU and namespace launcher remain platform compatibility/TCB.
"""
from __future__ import annotations

from contextlib import contextmanager
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parents[2]


class NativeRuntimeUnavailable(RuntimeError):
    """The admitted native runtime cannot be established. Never fall back."""


# Linux UAPI constants; some Conda builds omit their Python bindings. Values
# independently captured from system Python and linux/{memfd,fcntl}.h in hg_whostpin.
F_ADD_SEALS, F_GET_SEALS = 1033, 1034
F_SEAL_SEAL, F_SEAL_SHRINK, F_SEAL_GROW, F_SEAL_WRITE = 1, 2, 4, 8


def _snapshot(source: Path, expected: str) -> int:
    libc = ctypes.CDLL(None, use_errno=True)
    create = libc.memfd_create
    create.argtypes, create.restype = [ctypes.c_char_p, ctypes.c_uint], ctypes.c_int
    fd = create(b'hg-native-runtime', 3)  # MFD_CLOEXEC | MFD_ALLOW_SEALING
    if fd < 0:
        raise OSError(ctypes.get_errno(), "memfd_create")
    try:
        digest = hashlib.sha256()
        with source.open('rb') as stream, os.fdopen(os.dup(fd), 'wb') as output:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                output.write(block)
                digest.update(block)
        if digest.hexdigest() != expected:
            raise NativeRuntimeUnavailable(f'native runtime payload digest mismatch: {source}')
        os.fchmod(fd, 0o555)
        os.lseek(fd, 0, os.SEEK_SET)
        fcntl.fcntl(fd, F_ADD_SEALS,
                    F_SEAL_WRITE | F_SEAL_GROW | F_SEAL_SHRINK | F_SEAL_SEAL)
        return fd
    except BaseException:
        os.close(fd)
        raise


class FrozenRuntime:
    def __init__(self, manifest: dict, digest: str, fds: dict[str, int], launcher: int):
        self.manifest, self.fds, self.launcher = manifest, fds, launcher
        self.receipt = {'dataset': 'bird_minidev', 'sha256': digest, 'verified': True,
                        'mechanism': 'sealed-memfd-private-root-v1',
                        'identity': manifest['identity'], 'files': len(fds)}

    def run(self, argv: list[str], *, workdir: Path, reward_dir: Path,
            timeout_s: int) -> subprocess.CompletedProcess:
        """Launch inside an empty root; no ambient /usr, /etc, PATH or Python site."""
        plan = [f'/proc/self/fd/{self.launcher}', '--unshare-all', '--die-with-parent',
                '--new-session', '--cap-drop', 'ALL', '--proc', '/proc', '--dev', '/dev',
                '--tmpfs', '/tmp', '--ro-bind', str(workdir), '/task',
                '--bind', str(reward_dir), '/task/verifier', '--chdir', '/task', '--clearenv']
        for name, value in self.manifest['environment'].items():
            plan += ['--setenv', name, value]
        for target, fd in self.fds.items():
            plan += ['--perms', '0555', '--ro-bind-data', str(fd), target]
        # Even the interpreter's first loader/cache resolution is explicit. Child
        # sys.executable launches use PT_INTERP in the same closed namespace.
        interpreter = self.manifest['interpreter']
        command = [self.manifest['loader'], '--inhibit-cache', '--library-path',
                   ':'.join(self.manifest['library_path']), interpreter,
                   *self.manifest['python_flags'], *argv[1:]]
        if argv[1] == 'check.py':
            command[command.index('check.py')] = '/scorer/check.py'
        plan += ['--', *command]
        return subprocess.run(plan, pass_fds=(*self.fds.values(), self.launcher),
                              capture_output=True, text=True, timeout=timeout_s,
                              env={'PATH': '/usr/bin:/bin', 'LANG': 'C'})


@contextmanager
def admit(binding: dict):
    """Authenticate the selected manifest and retain exact sealed bytes until exit."""
    fds = {}
    launcher = None
    try:
        if binding['dataset'] != 'bird_minidev':
            raise NativeRuntimeUnavailable('native runtime dataset is outside BIRD scope')
        path = Path(binding['manifest'])
        raw = (path if path.is_absolute() else ROOT / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != binding['sha256']:
            raise NativeRuntimeUnavailable('native runtime manifest digest mismatch')
        manifest = json.loads(raw)
        if manifest['schema'] != 1 or manifest['dataset'] != binding['dataset']:
            raise NativeRuntimeUnavailable('native runtime manifest schema/dataset mismatch')
        if (manifest['identity']['machine'] != platform.machine()
                or manifest['identity']['kernel'] != platform.release()):
            raise NativeRuntimeUnavailable('native runtime kernel/machine envelope mismatch')
        for target, entry in manifest['files'].items():
            p = Path(target)
            if (not p.is_absolute() or '..' in p.parts
                    or p.parts[1] in {'task', 'tmp', 'proc', 'dev', 'etc'}):
                raise NativeRuntimeUnavailable(f'unsafe native runtime destination: {target}')
            source = Path(entry['source'])
            fds[target] = _snapshot(source if source.is_absolute() else ROOT / source,
                                    entry['sha256'])
        for required in (manifest['interpreter'], manifest['loader'], '/scorer/check.py'):
            if required not in fds:
                raise NativeRuntimeUnavailable(f'native runtime missing entry: {required}')
        launcher = _snapshot(Path(manifest['launcher']['path']), manifest['launcher']['sha256'])
        yield FrozenRuntime(manifest, digest, fds, launcher)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise NativeRuntimeUnavailable(f'native runtime refused: {exc}') from exc
    finally:
        for fd in fds.values():
            os.close(fd)
        if launcher is not None:
            os.close(launcher)
