"""Build the diagnostic's local scratch image and seal its explicit file graph.

Run once in a fresh fixture; refuses to overwrite its bundle or independent pins.
No pull, network, model, dataset or production source modification is required.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))
from eval.admission.scorer_bundle import seal_bundle, require_contract_bundle


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)


def main():
    if (ROOT / "bundle.json").exists() or (ROOT / "trusted-pins.json").exists():
        raise SystemExit("Refusing to replace existing sealed control")
    capture = ROOT / "build-evidence"
    capture.mkdir()
    commands = []

    def run(*argv):
        result = subprocess.run(argv, capture_output=True, text=True, check=False)
        commands.append(dict(argv=list(argv), returncode=result.returncode,
                             stdout=result.stdout, stderr=result.stderr))
        (capture / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        result.check_returncode()
        return result.stdout

    run("docker", "version")
    run("docker", "build", "--pull=false", "--network=none", "--iidfile",
        str(capture / "image-id.txt"), str(ROOT / "image"))
    image = (capture / "image-id.txt").read_text().strip()
    write(capture / "image-inspect.json", run("docker", "image", "inspect", image).encode())
    run("docker", "image", "save", "--output", str(capture / "image.tar"), image)
    runtime = ROOT / "closure/sh"
    shutil.copyfile("/usr/bin/busybox", runtime)
    runtime.chmod(0o555)
    run("file", str(runtime))
    run("readelf", "-l", str(runtime))
    run("dpkg-query", "-W", "busybox-static")
    shutil.copyfile("/usr/share/doc/busybox-static/copyright", ROOT / "busybox-copyright.txt")
    scorer = dict(entrypoint="check.sh", argv=["/control-scorer/sh", "/control-scorer/check.sh"],
                  files=[])
    for name, role, requires in [("check.sh", "scorer", ["sh", "expected.txt"]),
                                 ("sh", "runtime", []), ("expected.txt", "dependency", [])]:
        raw = (ROOT / "closure" / name).read_bytes()
        scorer["files"].append(dict(path=name, role=role, requires=requires,
                                    sha256=sha(raw), bytes=len(raw)))
    identity = dict(source_sha256=sha((ROOT / "task-source.json").read_bytes()),
                    runtime_image_id=image, scorer=scorer)
    bundle_raw, bundle_pin = seal_bundle(dict(schema="harnessgrad.scorer-bundle.v2",
        isolation_class="pristine-offline", network="none", **identity))
    contract = dict(schema="harnessgrad.artifact-scorer.v1", task_id="w-pristine-addition-control",
                    **identity, export=dict(files=[dict(path="answer.txt", max_bytes=16)],
                        max_bytes=16, max_inodes=2),
                    quota={"/tmp": dict(bytes=1048576, inodes=64),
                           "/control-output": dict(bytes=65536, inodes=16)})
    contract_raw = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()
    contract_pin = sha(contract_raw)
    require_contract_bundle(contract_raw, contract_pin, bundle_raw, bundle_pin)
    write(ROOT / "bundle.json", bundle_raw)
    write(ROOT / "task-contract.json", contract_raw)
    write(ROOT / "trusted-pins.json", (json.dumps(dict(manifest_sha256=bundle_pin,
        artifact_contract_sha256=contract_pin, runtime_image_id=image,
        source_sha256=identity["source_sha256"]), indent=2) + "\n").encode())
    print(json.dumps(dict(manifest_sha256=bundle_pin, artifact_contract_sha256=contract_pin,
                          runtime_image_id=image)))


if __name__ == "__main__":
    main()
