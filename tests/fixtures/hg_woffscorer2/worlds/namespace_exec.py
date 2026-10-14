#!/usr/bin/env python3
"""Assert an isolated loopback-only network namespace before JVM scorer execution."""
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import runpy
import socket
import sys

def main():
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sys.dont_write_bytecode = True
    for fdpath in Path("/proc/self/fd").iterdir():
        try:
            if int(fdpath.name) > 2 and os.readlink(fdpath).startswith("socket:"):
                os.close(int(fdpath.name))
        except FileNotFoundError:
            pass
    netns = os.readlink("/proc/self/ns/net")
    assert netns != os.environ["HG_WOFFSCORER2_PARENT_NETNS"]
    interfaces = sorted(p.name for p in Path("/sys/class/net").iterdir())
    # sysfs can expose the host view; /proc/net is the authoritative namespace view.
    network_devices = Path("/proc/net/dev").read_text()
    dev_names = [line.split(":")[0].strip() for line in network_devices.splitlines()[2:]]
    assert dev_names == ["lo"], dev_names
    routes = Path("/proc/net/route").read_text()
    assert not routes.splitlines()[1:], routes
    with socket.socket() as probe:
        probe.settimeout(1)
        try:
            probe.connect(("198.18.0.1", 9))
        except OSError as exc:
            assert exc.errno in (errno.ENETUNREACH, errno.EHOSTUNREACH), exc
            external_probe = {"target": "198.18.0.1:9", "errno": exc.errno, "result": "no route"}
        else:
            raise AssertionError("external connection unexpectedly possible")
    receipt = {"guard": "bubblewrap fresh network namespace; only loopback and no IPv4 routes",
               "parent_netns": os.environ["HG_WOFFSCORER2_PARENT_NETNS"], "netns": netns,
               "network_devices": network_devices, "ipv4_routes": routes,
               "ipv6_routes": Path("/proc/net/ipv6_route").read_text(),
               "external_probe": external_probe, "cpu_limit_seconds": 120,
               "nofile_limit": 256, "interpreter": str(Path(sys.executable).resolve()),
               "interpreter_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
               "jvm_loopback_required": True, "production_runtime_observation": False}
    print(json.dumps(receipt, sort_keys=True), file=sys.stderr, flush=True)
    script = Path(sys.argv[1]).resolve()
    sys.argv = sys.argv[1:]
    sys.path.insert(0, str(script.parent))
    runpy.run_path(str(script), run_name="__main__")

if __name__ == "__main__":
    main()
