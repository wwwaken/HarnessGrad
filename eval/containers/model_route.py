"""Validated infrastructure mounts for the native offline model route."""
from pathlib import Path
import stat

from eval.service.modelgate import GatewayUnavailable

ROOT = Path("/run/harnessgrad-model")
FORWARDER = Path(__file__).resolve().parents[1] / "service/native_model_forwarder.py"


def mounts(socket_path: Path, *, network, exposed_paths, writable_paths):
    """Revalidate at launch; never bind a relay directory or accept a task target."""
    source = Path(socket_path)
    if (network != "none" or not source.is_absolute() or ".." in source.parts
            or any(p.is_symlink() for p in (source, *source.parents))):
        raise GatewayUnavailable("model socket requires network none and an absolute non-symlink source")
    if not stat.S_ISSOCK(source.stat().st_mode):
        raise GatewayUnavailable("model route source must be a UNIX socket")
    for path in exposed_paths:
        path = Path(path).resolve()
        if ROOT == path or ROOT in path.parents or path in ROOT.parents:
            raise GatewayUnavailable("model route target overlaps another mount")
    for path in writable_paths:
        path = Path(path).resolve()
        if source == path or path in source.parents:
            raise GatewayUnavailable("model socket source is reachable through writable storage")
    if FORWARDER.is_symlink() or not FORWARDER.is_file():
        raise GatewayUnavailable("trusted native model forwarder is unavailable")
    return ["--ro-bind", str(source), str(ROOT / "model.sock"),
            "--ro-bind", str(FORWARDER), str(ROOT / "forwarder.py")]


def bootstrap(argv, path):
    return ["/usr/bin/python3", "-I", "-S", str(ROOT / "forwarder.py"),
            str(ROOT / "model.sock"), path, "--", *argv]
