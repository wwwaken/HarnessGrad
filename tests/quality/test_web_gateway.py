"""Provider adapters and recording contract for the host web gateway."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.web_gateway import WebGateway, parse_fetched, parse_searxng, parse_serper  # noqa: E402
import eval.container as container  # noqa: E402
from eval.runner import run_one  # noqa: E402
from data import registry  # noqa: E402

DEMO_IMAGE = os.environ.get("HG_EXEC_DEMO_IMAGE", "docker.m.daocloud.io/library/python:3.11-slim")


def test_recorded_provider_fixtures_have_common_shape():
    searx = {"results": [{"title": "A", "url": "https://a", "content": "alpha"}]}
    serper = {"organic": [{"title": "B", "link": "https://b", "snippet": "beta"}]}
    assert parse_searxng(searx) == [{"title": "A", "url": "https://a", "snippet": "alpha"}]
    assert parse_serper(serper) == [{"title": "B", "url": "https://b", "snippet": "beta"}]
    assert parse_fetched(200, "https://a", b"<title>A</title>") == {
        "url": "https://a", "status": 200, "text": "<title>A</title>", "bytes": 16}


def test_web_declaration_survives_environment_normalization():
    spec = {"kind": "exec", "image": "x", "network": "services",
            "services": [], "web": {"search": True, "fetch": False}}
    assert registry._normalize_env(spec)["web"] == {"search": True, "fetch": False}


def test_gateway_records_search_and_fetch_but_not_health(tmp_path, monkeypatch):
    monkeypatch.setenv("HG_WEB_SEARCH", "none")
    monkeypatch.setenv("HG_WEB_FETCH", "http")
    record = tmp_path / "requests.jsonl"
    gateway = WebGateway(record_path=record).start()
    try:
        import urllib.request
        req = urllib.request.Request(gateway.url + "/health")
        urllib.request.urlopen(req).read()
        req = urllib.request.Request(gateway.url + "/search", data=b'{"query":"x","num":1}', method="POST")
        urllib.request.urlopen(req).read()
    finally:
        gateway.stop()
    rows = [json.loads(line) for line in record.read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["kind"] == "search" and rows[0]["provider"] == "none"


def test_fetch_rejects_non_http_urls(tmp_path, monkeypatch):
    monkeypatch.setenv("HG_WEB_SEARCH", "none")
    monkeypatch.setenv("HG_WEB_FETCH", "http")
    gateway = WebGateway(record_path=tmp_path / "requests.jsonl")
    with pytest.raises(Exception, match="http or https"):
        gateway.fetch_request("file:///etc/passwd")


def test_paid_provider_without_key_refuses_to_start():
    env = os.environ.copy()
    env["HG_WEB_SEARCH"] = "serper"
    env.pop("SERPER_API_KEY", None)
    proc = subprocess.run([sys.executable, "tools/web_gateway.py", "--port", "0"], cwd=ROOT,
                          env=env, capture_output=True, text=True, timeout=10)
    assert proc.returncode != 0
    assert "serper" in proc.stderr.lower()


def test_declared_task_gets_web_url_and_undeclared_task_does_not(tmp_path, monkeypatch):
    """The task declaration is the capability boundary, including its absence."""
    if container.available() is None:
        pytest.skip("no docker daemon")
    try:
        image = container.resolve_digest(DEMO_IMAGE)
    except container.ContainerUnavailable:
        pytest.skip("demo exec image is not available")
    monkeypatch.setenv("HG_WEB_SEARCH", "none")
    monkeypatch.setenv("HG_WEB_FETCH", "http")
    repo = tmp_path / "harness"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps({
        "name": "web-probe", "version": "1", "entrypoint": "agent.py",
        "env_kinds": ["exec"]}))
    (repo / "agent.py").write_text(
        "import argparse, os, pathlib, urllib.request\n"
        "p=argparse.ArgumentParser(); p.add_argument('--task'); p.add_argument('--workdir'); a=p.parse_args()\n"
        "w=pathlib.Path(a.workdir); base=os.environ.get('HG_SVC_WEB_URL')\n"
        "if base:\n"
        "  req=urllib.request.Request(base+'/search', data=b'{\\\"query\\\":\\\"x\\\",\\\"num\\\":1}', method='POST')\n"
        "answer='absent' if not base else ('searchable' if urllib.request.urlopen(req, timeout=5).read() else 'bad')\n"
        "(w/'answer.txt').write_text(answer); (w/'trace.jsonl').write_text('{}\\n')\n")
    common = {"kind": "exec", "image": image, "workdir": "/app",
              "placement": "inside", "services": []}
    with_web = run_one(repo, {"task_id": "with", "goal": "web"}, sandbox=True,
                       env={**common, "network": "services", "web": {"search": True, "fetch": True}},
                       run_id="web-cap", run_seed="s", recordings_root=tmp_path / "recordings")
    without_web = run_one(repo, {"task_id": "without", "goal": "offline"}, sandbox=True,
                          env={**common, "network": "none"}, run_id="web-cap",
                          run_seed="s", recordings_root=tmp_path / "recordings")
    assert with_web["answer"] == "searchable"
    assert with_web["web_gateway"]["published"] is True
    assert without_web["answer"] == "absent"
    assert without_web["web_gateway"] is None
