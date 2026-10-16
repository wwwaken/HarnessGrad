"""Read-only CLI/docs checks; never execute H0, a model, or a task payload."""
import argparse
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _cli_only(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("CLI/docs check attempted runtime or payload access")

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    # Patch `connect`, NOT `socket.socket`: replacing the class makes a later
    # `import ssl` fail while it builds `class SSLSocket(socket)`, which is an
    # order-dependent failure that has nothing to do with what this guards.
    monkeypatch.setattr(socket.socket, "connect", refuse)
    import driver

    for name in ("load", "load_split", "published", "kind_of"):
        monkeypatch.setattr(driver.datasets, name, refuse)
    for name in ("load_env", "evaluate", "_run_mode_a", "_run_eval_side"):
        monkeypatch.setattr(driver, name, refuse)
    for name in ("read_text", "read_bytes", "write_text", "write_bytes", "mkdir"):
        monkeypatch.setattr(Path, name, refuse)
    monkeypatch.setattr(tempfile, "mkdtemp", refuse)
    return driver


def test_help_explains_local_prerequisites_and_preserves_authorization_boundary(
        monkeypatch, capsys):
    driver = _cli_only(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["driver.py", "--help"])
    with pytest.raises(SystemExit) as result:
        driver.main()
    assert result.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert "no sudo, dedicated quota volume, root Docker access, or strict runtime mode" in help_text
    assert "Sandboxed runs still require working bubblewrap/user namespaces" in help_text
    assert "Local/demo success grants no production/H0 authorization" in help_text
    assert "still fail closed without trusted backend observations" in help_text
    assert "invalid/unmeasured, never an ordinary zero score" in help_text
    assert "required for diagnostic/pilot_10pct" in help_text


def test_readme_demo_commands_parse_without_entering_staged_or_runtime_paths(monkeypatch):
    readme = (ROOT / "README.md").read_text()
    # Locate the section by its subject, not by its exact heading text. The heading carries
    # an icon, and pinning the whole line would make a cosmetic rename break this test --
    # or worse, silently widen it, because `str.split` on a missing separator returns the
    # whole document and `[0]` is still valid.
    match = re.search(r"^## [^\n]*Run it\n(.*?)(?=\n## )", readme, re.S | re.M)
    assert match, "README.md has no 'Run it' section"
    section = match.group(1)
    assert "export HG_AGENT_BACKEND=mock" in section
    assert "grants no production/H0 authorization" in section
    commands = [shlex.split(line) for line in section.replace("\\\n", " ").splitlines()
                if line.startswith("python3 driver.py ")]
    assert len(commands) == 3
    driver = _cli_only(monkeypatch)
    parse_args = argparse.ArgumentParser.parse_args
    parsed = []

    class ParsedOnly(Exception):
        pass

    def stop_after_parse(parser, *args, **kwargs):
        parsed.append(parse_args(parser, *args, **kwargs))
        raise ParsedOnly

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", stop_after_parse)
    for command in commands:
        monkeypatch.setattr(sys, "argv", command[1:])
        with pytest.raises(ParsedOnly):
            driver.main()
        args = parsed[-1]
        assert (args.dataset, args.sampling, args.sandbox) == ("demo", "all", True)
        assert args.policy_evidence is None
    assert len({args.run_id for args in parsed}) == len(commands)


def test_installer_next_command_is_an_explicit_non_authorized_mock_demo():
    # Execute only the report with authored success facts, never installer checks,
    # dependency installation, host inspection or sandbox execution.
    report = (ROOT / "install.sh").read_text().split('step "Summary"\n', 1)[1]
    result = subprocess.run(
        ["/bin/bash", "-c", report], cwd=ROOT, capture_output=True, text=True, timeout=5,
        env={"FAILED": "0", "GREEN": "", "BOLD": "", "OFF": "", "ROOT": str(ROOT)},
    )
    assert result.returncode == 0, result.stderr
    assert "No production/H0 authorization" in result.stdout
    assert "no model credentials needed" in result.stdout
    command = next(line.strip() for line in result.stdout.replace("\\\n", " ").splitlines()
                   if line.strip().startswith("HG_AGENT_BACKEND="))
    argv = shlex.split(command)
    assert argv[:3] == ["HG_AGENT_BACKEND=mock", "python3", "driver.py"]
    assert argv[argv.index("--dataset") + 1] == "demo"
    assert argv[argv.index("--sampling") + 1] == "all"
    assert "--no-sandbox" not in argv and "--policy-evidence" not in argv
