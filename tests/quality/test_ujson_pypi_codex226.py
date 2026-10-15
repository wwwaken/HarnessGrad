"""Offline package provenance checks; never import ujson or any dataset adapter."""
from __future__ import annotations

import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/ujson_pypi_codex226"
FILENAME = "ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
WHEEL_SHA256 = "f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1"
JSON_SHA256 = "a3c95fe11a39ff2db660e12cee42ff27ad0411d205320d1350fbc2924a7ab6a2"
ACQUISITION_SHA256 = "db4fbda3cada5e44af4cf3d662ba3eb565841f829ab0d1b80b47c10820f023f3"
DIST_INFO = "ujson-5.10.0.dist-info/"
MODULE = "ujson.cpython-312-x86_64-linux-gnu.so"
NEEDED = ["libstdc++.so.6", "libm.so.6", "libgcc_s.so.1", "libpthread.so.0", "libc.so.6"]
VERSIONS = {
    "libgcc_s.so.1": ["GCC_3.0"],
    "libstdc++.so.6": ["CXXABI_1.3", "GLIBCXX_3.4"],
    "libc.so.6": ["GLIBC_2.2.5", "GLIBC_2.14"],
}


def read_json(name):
    return json.loads((FIXTURE / name).read_bytes())


def checked_bytes(path, digest):
    contents = path.read_bytes()
    assert hashlib.sha256(contents).hexdigest() == digest, path.name
    return contents


def wheel_contents():
    wheel = checked_bytes(FIXTURE / "artifacts" / FILENAME, WHEEL_SHA256)
    with zipfile.ZipFile(io.BytesIO(wheel)) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names))
        return {name: archive.read(name) for name in names if not name.endswith("/")}


def test_official_json_binds_exact_wheel_url_size_hash_and_metadata():
    checked_bytes(FIXTURE / "acquisition.json", ACQUISITION_SHA256)
    metadata = json.loads(checked_bytes(FIXTURE / "pypi-release.json", JSON_SHA256))
    acquisition = read_json("acquisition.json")
    receipt = read_json("provenance.json")
    artifacts = [item for item in metadata["urls"] if item["filename"] == FILENAME]
    assert len(artifacts) == 1
    artifact = artifacts[0]
    assert artifact == acquisition["artifact"]
    assert acquisition["metadata_url"] == "https://pypi.org/pypi/ujson/5.10.0/json"
    assert acquisition["metadata_sha256"] == JSON_SHA256
    assert artifact["url"] == (
        "https://files.pythonhosted.org/packages/04/81/"
        "668707e5f2177791869b624be4c06fb2473bf97ee33296b18d1cf3092af7/" + FILENAME
    )
    assert artifact["digests"]["sha256"] == receipt["artifact"]["sha256"] == WHEEL_SHA256
    assert artifact["size"] == receipt["artifact"]["bytes"] == 53686
    assert (FIXTURE / "artifacts" / FILENAME).stat().st_size == 53686
    assert artifact["packagetype"] == "bdist_wheel" and artifact["yanked"] is False
    assert metadata["info"]["name"] == "ujson" and metadata["info"]["version"] == "5.10.0"
    assert metadata["info"]["requires_dist"] is None
    contents = wheel_contents()
    assert hashlib.sha256(contents[DIST_INFO + "METADATA"]).hexdigest() == artifact["core-metadata"]["sha256"]


@pytest.mark.parametrize("name,digest", [
    ("pypi-release.json", JSON_SHA256),
    ("artifacts/" + FILENAME, WHEEL_SHA256),
    ("acquisition.json", ACQUISITION_SHA256),
])
def test_artifact_and_origin_record_drift_rejected(name, digest, tmp_path):
    target = tmp_path / Path(name).name
    target.write_bytes((FIXTURE / name).read_bytes() + b"\nDRIFT\n")
    with pytest.raises(AssertionError, match=re.escape(target.name)):
        checked_bytes(target, digest)


def test_archive_record_and_member_manifest_cover_all_files():
    contents = wheel_contents()
    members = read_json("provenance.json")["members"]
    assert set(contents) == set(members) == {
        MODULE, *(DIST_INFO + name for name in ["LICENSE.txt", "METADATA", "RECORD", "top_level.txt", "WHEEL"])
    }
    for name, data in contents.items():
        assert members[name] == {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    rows = list(csv.reader(io.StringIO(contents[DIST_INFO + "RECORD"].decode())))
    assert len(rows) == len(contents) and {row[0] for row in rows} == set(contents)
    for name, digest, size in rows:
        if name == DIST_INFO + "RECORD":
            assert digest == size == ""
        else:
            data = contents[name]
            expected = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            assert digest == "sha256=" + expected and size == str(len(data))


def test_target_tags_and_python_dependency_metadata():
    contents = wheel_contents()
    metadata = BytesParser().parsebytes(contents[DIST_INFO + "METADATA"])
    wheel = BytesParser().parsebytes(contents[DIST_INFO + "WHEEL"])
    assert metadata["Name"] == "ujson" and metadata["Version"] == "5.10.0"
    assert metadata["Requires-Python"] == ">=3.8"
    assert metadata.get_all("Requires-Dist", []) == []
    assert metadata.get_all("License-File") == ["LICENSE.txt"]
    assert wheel["Root-Is-Purelib"] == "false"
    assert set(wheel.get_all("Tag")) == {
        "cp312-cp312-manylinux_2_17_x86_64", "cp312-cp312-manylinux2014_x86_64"
    }
    target = read_json("provenance.json")["target"]
    prior = json.loads((ROOT / "tests/fixtures/twowikimultihopqa_upstream_codex197/provenance.json").read_bytes())
    recorded = prior["dependencies"]["test_environment"]
    assert target["python"] == recorded["python"] == "3.12.4"
    assert target["implementation"] == recorded["implementation"] == "CPython"
    assert target["machine"] == recorded["machine"] == "x86_64"
    assert target["minimum_glibc_tag"] == "2.17"
    assert target["supported_image_digest"] is None


def test_all_shipped_notices_preserved_with_explicit_completeness_gap():
    contents = wheel_contents()
    license_bytes = checked_bytes(FIXTURE / "LICENSE.txt", "36866344f0a486541bd9800f1a407a056c0c214a82c658f059694daf3dc394d2")
    assert contents[DIST_INFO + "LICENSE.txt"] == license_bytes
    for text in [b"Electronic Arts", b"MODP_ASCII", b"Nick Galbreath", b"TCL library", b"Sun Microsystems"]:
        assert text in license_bytes
    assert not any("NOTICE" in name.upper() for name in contents)
    assert b"double-conversion" not in license_bytes and b"V8" not in license_bytes
    license_receipt = read_json("provenance.json")["license"]
    assert license_receipt["completeness_attested"] is False
    assert "double_conversion" in license_receipt["remaining_review"]


def test_actual_wheel_elf_dependency_contract_without_loading(tmp_path):
    readelf = shutil.which("readelf")
    assert readelf, "GNU readelf is required for the static native dependency check"
    target = tmp_path / MODULE
    target.write_bytes(wheel_contents()[MODULE])
    output = subprocess.check_output(
        [readelf, "-h", "-d", "-V", "--dyn-syms", "-W", str(target)],
        text=True, env={**os.environ, "LC_ALL": "C"}, timeout=10,
    )
    assert "ELF64" in output and "Advanced Micro Devices X86-64" in output
    assert re.findall(r"\(NEEDED\).*\[(.*?)\]", output) == NEEDED
    assert "(RPATH)" not in output and "(RUNPATH)" not in output
    requirements = {}
    library = None
    for line in output.splitlines():
        match = re.search(r"File: (\S+)\s+Cnt:", line)
        if match:
            library = match[1]
            requirements[library] = []
        match = re.search(r"Name: (\S+)\s+Flags:", line)
        if match:
            assert library is not None
            requirements[library].append(match[1])
    assert {name: set(versions) for name, versions in requirements.items()} == {
        name: set(versions) for name, versions in VERSIONS.items()
    }
    assert any("double_conversion" in line and " UND " not in line for line in output.splitlines())
    native = read_json("provenance.json")["native"]
    assert native["needed"] == NEEDED and native["required_symbol_versions"] == VERSIONS
    assert native["bundled_shared_libraries"] == []
    for name, digest in native["reports"].items():
        checked_bytes(FIXTURE / name, digest)


def test_offline_install_origin_and_file_receipt_do_not_assert_runtime_closure():
    contents = wheel_contents()
    receipt = read_json("offline-install-receipt.json")
    report = json.loads(checked_bytes(FIXTURE / "offline-install-report.json", receipt["pip_report_sha256"]))
    assert len(report["install"]) == 1
    installation = report["install"][0]
    assert installation["download_info"]["url"].endswith("/artifacts/" + FILENAME)
    assert installation["download_info"]["url"].startswith("file:///tmp/hg-codex-226/")
    assert installation["download_info"]["archive_info"]["hashes"] == {"sha256": WHEEL_SHA256}
    assert installation["metadata"]["name"] == "ujson" and installation["metadata"]["version"] == "5.10.0"
    assert report["environment"]["python_full_version"] == receipt["python"] == "3.12.4"
    assert receipt["system_site_packages"] is False and receipt["native_extension_imported"] is False
    assert receipt["pip_configuration_files_disabled"] is True
    assert set(receipt["installed_files_match_wheel"]) == set(contents) - {DIST_INFO + "RECORD"}
    for name, identity in receipt["installed_files_match_wheel"].items():
        assert identity == {"bytes": len(contents[name]), "sha256": hashlib.sha256(contents[name]).hexdigest()}
    assert (FIXTURE / "requirements-codex226.txt").read_text() == "ujson==5.10.0 --hash=sha256:" + WHEEL_SHA256 + "\n"
    closure = read_json("provenance.json")["closure"]
    assert closure["artifact_provenance_verified"] and closure["wheel_record_verified"] and closure["offline_install_verified"]
    for key in ["fresh_native_import_verified", "loader_resolution_attested", "transitive_native_closure_attested", "supported_image_attested", "runtime_closed", "production_authorized"]:
        assert closure[key] is False
    registry = json.loads((ROOT / "registry/dataset-blockers.json").read_bytes())
    assert registry["review"]["production_authorized"] is False
    # The ujson blocker was WITHDRAWN by operator decision and recorded as a limit: the pinned
    # reproducible rebuild did not reproduce (the compiled extension, WHEEL and RECORD differ) and
    # PyPI returned 404 "No provenance available". This assertion used to require the blocker to
    # still be present with status external, and went red the moment it was withdrawn. What must
    # stay pinned is the absence plus the readable failed-search evidence.
    dataset = next(item for item in registry["datasets"] if item["dataset"] == "twowikimultihopqa")
    assert "ujson-native-offline-closure" not in {item["id"] for item in dataset["blockers"]}
    withdrawal = (ROOT / "registry" / "withdrawn-requirements.md").read_text(encoding="utf-8")
    assert "### `twowikimultihopqa / ujson-native-offline-closure`" in withdrawal
    assert "the rebuild **did not reproduce**" in withdrawal
    assert "PyPI build attestation" in withdrawal
