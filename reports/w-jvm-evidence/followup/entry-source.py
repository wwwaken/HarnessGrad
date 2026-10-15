#!/usr/bin/env python3
"""Bound an authored control, then execute its unchanged materialized check."""
import json
import os
from pathlib import Path
import resource
import runpy
import sys


def main():
    config = json.loads(Path('/tmp/control/config.json').read_text())
    for name, value in config['rlimits'].items():
        resource.setrlimit(getattr(resource, name), (value, value))
    os.sched_setaffinity(0, config['affinity'])
    # No socket connection is made: topology is read from the namespace itself.
    network = {
        'netns': os.readlink('/proc/self/ns/net'),
        'parent_netns': config['parent_netns'],
        'devices': Path('/proc/net/dev').read_text(),
        'routes': Path('/proc/net/route').read_text(),
        'ipv6_routes': Path('/proc/net/ipv6_route').read_text(),
    }
    assert network['netns'] != network['parent_netns']
    assert [line.split(':')[0].strip() for line in network['devices'].splitlines()[2:]] == ['lo']
    assert not network['routes'].splitlines()[1:]
    Path('/tmp/control/output/network.json').write_text(json.dumps(network, indent=2) + '\n')
    Path('/tmp/control/output/entry-limits.txt').write_text(Path('/proc/self/limits').read_text())
    script, *args = config['check_argv']
    sys.argv = [script, *args]
    sys.path.insert(0, str(Path(script).parent))
    runpy.run_path(script, run_name='__main__')


if __name__ == '__main__':
    main()
