"""Run service/verifier unit controls without Docker or sandbox execution.

The all-zero digest is an explicitly synthetic test placeholder for metadata
validation; it makes no claim about any image's existence or content identity.
Container lifecycle tests and real sandbox execution are skipped by policy.
"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path.cwd()))
class NoContainers:
    @pytest.fixture(autouse=True)
    def prohibit_containers(self, request, monkeypatch):
        import eval.containers.container as container
        def forbidden(*args, **kwargs):
            raise AssertionError('Docker prohibited in w-taubench controls: ' + repr(args))
        monkeypatch.setattr(container, 'docker', forbidden)
        if request.module.__name__ == 'test_services':
            monkeypatch.setattr(container, 'resolve_digest',
                                lambda ref: 'synthetic-control@sha256:' + '0' * 64)
            def skip():
                pytest.skip('w-taubench: container lifecycle explicitly prohibited')
            monkeypatch.setattr(request.module, '_require_docker', skip)
        if request.node.originalname == 'test_the_same_rules_hold_inside_the_sandbox':
            pytest.skip('w-taubench: sandbox execution excluded from local controls')

raise SystemExit(pytest.main(sys.argv[1:], plugins=[NoContainers()]))
