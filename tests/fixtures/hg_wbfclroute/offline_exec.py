#!/usr/bin/env python3
"""Run a controlled Python scorer after kernel-level socket denial (Linux only).

This fixture guard is deliberately separate from production verifier admission.
libseccomp denies all socket entry points plus io_uring_setup; filters survive exec.
No network is required or allowed by the scorer scripts using this wrapper.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import runpy
import socket
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: offline_exec.py script.py [args ...]")
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    # Do not carry inherited sockets into a scorer, even if its caller supplied one.
    for fd_path in Path('/proc/self/fd').iterdir():
        fd = int(fd_path.name)
        try:
            if fd > 2 and os.readlink(fd_path).startswith('socket:'):
                os.close(fd)
        except FileNotFoundError:
            pass
    libname = ctypes.util.find_library("seccomp")
    if not libname:
        raise RuntimeError("libseccomp required; no weak fallback")
    lib = ctypes.CDLL(libname, use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    lib.seccomp_rule_add.restype = ctypes.c_int
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_load.restype = ctypes.c_int
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise RuntimeError("seccomp_init failed")
    denied = []
    for name in ("socket", "socketpair", "connect", "bind", "listen", "accept", "accept4",
                 "sendto", "recvfrom", "sendmsg", "recvmsg", "sendmmsg", "recvmmsg",
                 "shutdown", "getsockname", "getpeername", "setsockopt", "getsockopt",
                 "io_uring_setup"):
        number = lib.seccomp_syscall_resolve_name(name.encode())
        if number < 0:
            raise RuntimeError(f"unknown syscall {name}")
        rc = lib.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, number, 0)
        if rc:
            raise RuntimeError(f"seccomp_rule_add {name}: {rc}")
        denied.append(name)
    rc = lib.seccomp_load(ctx)
    lib.seccomp_release(ctx)
    if rc:
        raise RuntimeError(f"seccomp_load: {rc}")
    probes = {}
    for family in (socket.AF_INET, socket.AF_INET6, socket.AF_UNIX):
        try:
            sock = socket.socket(family)
        except OSError as exc:
            assert exc.errno == errno.EPERM, exc
            probes[str(family)] = {"errno": exc.errno, "result": "denied"}
        else:
            sock.close()
            raise AssertionError("socket unexpectedly permitted")
    mappings = Path('/proc/self/maps').read_text().splitlines()
    libpath = next(line.split()[-1] for line in mappings if '/libseccomp.so.' in line)
    receipt = {"guard": "kernel seccomp EPERM; no inherited socket fd > 2",
               "denied_syscalls": denied, "socket_probes": probes,
               "interpreter": str(Path(sys.executable).resolve()),
               "interpreter_sha256": sha(Path(sys.executable).resolve()),
               "python": sys.version, "machine": platform.machine(),
               "libseccomp": libpath, "libseccomp_sha256": sha(libpath),
               "cpu_limit_seconds": 120, "nofile_limit": 256,
               "production_runtime_observation": False}
    print(json.dumps(receipt, sort_keys=True), file=sys.stderr, flush=True)
    # This Python audit hook supplements controlled import-time row-loader suppression.
    # It does not intercept native extensions' open(2), e.g. PyArrow, and is not a
    # filesystem sandbox or a trusted production custody observation.
    denied_dataset_reads = []
    def deny_dataset_payload(event, args):
        if event in {"open", "os.listdir", "os.scandir"} and args:
            candidate = args[0]
            if isinstance(candidate, (str, bytes, os.PathLike)):
                path = os.fsdecode(candidate)
                if path.startswith(("/mnt/20t/xubuqiang/datasets/", "/mnt/8t/xubuqiang/datasets/")):
                    denied_dataset_reads.append({"event": event, "path": path})
                    raise PermissionError("controlled fixture excludes external dataset payload reads")
    sys.addaudithook(deny_dataset_payload)
    script = Path(sys.argv[1]).resolve()
    sys.argv = sys.argv[1:]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        print(json.dumps({"blocked_external_dataset_reads": denied_dataset_reads}, sort_keys=True),
              file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
