"""Read installed bytes/metadata, never import adapters, score, or contact a service.

Historical import observations select a conservative dependency surface. Their
hashes are recomputed, as are current package payload hashes; old digests are
never promoted to current pins. Default metadata dependencies are a superset of
imports, not evidence that every dependency executes during scoring.
"""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig

from packaging.requirements import Requirement

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / "tests/fixtures/hg_wtbdep"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path):
    p = Path(path)
    label = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    if not p.is_file():
        return {"path": label, "exists": False}
    return {"path": label, "resolved_path": str(p.resolve()),
            "size": p.stat().st_size, "sha256": sha(p)}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


# Audit the old manifest without changing or repairing any historical evidence.
prior = []
for line in (OLD / "SHA256SUMS").read_text().splitlines():
    expected, rel = line.split("  ", 1)
    rec = file_record(OLD / rel)
    rec["historical_manifest_match"] = rec.get("sha256") == expected
    prior.append(rec)
save("prior-evidence-audit.json", {
    "manifest": file_record(OLD / "SHA256SUMS"),
    "note": "Historical checksum strings only used for comparison; sha256 fields were recomputed from present bytes.",
    "listed": len(prior), "missing": sum(not r["exists"] for r in prior if "exists" in r),
    "records": prior,
})

# Rehash the present interpreter and standard-library payload, excluding third-party paths.
stdlib = Path(sysconfig.get_path("stdlib"))
stdlib_rows = []
for p in sorted(stdlib.rglob("*")):
    rel = p.relative_to(stdlib)
    if any(x in rel.parts for x in ("site-packages", "__pycache__", "test", "tests")):
        continue
    if p.is_file() and p.suffix in (".py", ".so"):
        stdlib_rows.append({"path": str(rel), "sha256": sha(p)})
stdlib_payload = "".join(f'{r["sha256"]}  {r["path"]}\n' for r in stdlib_rows)
interpreter = {"executable": file_record(sys.executable), "version": sys.version,
               "version_info": list(sys.version_info), "SOABI": sysconfig.get_config_var("SOABI"),
               "stdlib_root": str(stdlib), "stdlib_members": stdlib_rows,
               "stdlib_manifest_sha256": hashlib.sha256(stdlib_payload.encode()).hexdigest(),
               "binding": "Inspection host only; verifier python3 resolves inherited PATH and is not bound by these manifests."}

# Reuse prior import-only module observations to select installed distributions.
observations = [OLD / "scope/reasoning-gym-import-only.json", OLD / "scope/jericho-import-only.json"]
observations += sorted((OLD / "native").glob("import-*.json"))
module_rows = []
for p in observations:
    data = json.loads(p.read_text())
    if not isinstance(data, dict) or "modules" not in data:
        continue
    modules = data["modules"]
    modules = ([{"module": k, "file": v} for k, v in modules.items()]
               if isinstance(modules, dict) else modules)
    module_rows.append({"observation": file_record(p), "historical_status": data.get("status", data.get("error")),
                        "current_files": [{"module": r["module"], **file_record(r["file"])}
                                          for r in modules if r.get("file")]})
save("import-byte-pins.json", {"note": "Selection comes from prior import-only observations; current files rehashed without reimporting. No proof of complete scorer import coverage.", "observations": module_rows})

mapping = metadata.packages_distributions()
names = {"numpy", "pandas", "scipy", "scikit-learn", "torch", "tensorflow", "matplotlib", "seaborn",
         "statsmodels", "gensim", "PyYAML", "pyext", "sympy", "mpmath", "openpyxl", "et-xmlfile", "lxml", "Pillow", "defusedxml",
         "chess", "python-chess", "reasoning-gym", "pyarrow", "scienceworld", "py4j", "jericho",
         "alfworld", "textworld", "pytest", "pytest-timeout", "pytest-json-ctrf", "packaging"}
for observation in module_rows:
    for row in observation["current_files"]:
        # Ignore stdlib modules; map top-level package to installed distributions.
        if "site-packages" in row["path"]:
            names.update(mapping.get(row["module"].split(".")[0], []))

packages = []
queue = sorted(names)
seen = set()
while queue:
    requested = queue.pop(0)
    key = re.sub(r"[-_.]+", "-", requested).lower()
    if key in seen:
        continue
    seen.add(key)
    try:
        d = metadata.distribution(requested)
    except metadata.PackageNotFoundError:
        packages.append({"requested": requested, "installed": False})
        continue
    requirements = []
    for raw in d.requires or []:
        req = Requirement(raw)
        contexts = ("", "pddl") if key == "textworld" else ("",)
        active = not req.marker or any(req.marker.evaluate({"extra": extra}) for extra in contexts)
        requirements.append({"requirement": raw, "active_default_or_textworld_pddl": bool(active)})
        if active:
            queue.append(req.name)
    # Bind every available RECORD-listed installed member except mutable bytecode.
    # The digest algorithm is SHA256 over sorted UTF-8 'hash  RECORD-relative-path\n'.
    members = []
    missing = []
    total = 0
    for member in sorted(d.files or [], key=str):
        if "__pycache__" in member.parts or str(member).endswith((".pyc", ".pyo")):
            continue
        f = Path(d.locate_file(member))
        if not f.is_file():
            missing.append(str(member))
            continue
        members.append(f"{sha(f)}  {member}\n")
        total += f.stat().st_size
    distpath = Path(d._path)
    packages.append({"requested": requested, "installed": True, "name": d.metadata["Name"], "version": d.version,
                     "location": str(d.locate_file("")), "metadata": file_record(distpath / "METADATA"),
                     "record": file_record(distpath / "RECORD"), "direct_url": file_record(distpath / "direct_url.json"),
                     "requirements": requirements, "payload_files": len(members), "payload_bytes": total,
                     "payload_manifest_sha256": hashlib.sha256("".join(members).encode()).hexdigest(),
                     "unavailable_members": missing, "record_available": d.files is not None})
save("host-runtime.json", {"schema": "harnessgrad.w-clo-runtime.host.v1", "interpreter": interpreter,
                           "packages": packages,
                           "payload_hash_algorithm": "SHA256 of concatenated sorted UTF-8 '<computed member sha256>  <RECORD-relative path>\\n'; exclude __pycache__, .pyc, .pyo; absent members separately reported. No copied RECORD digests used.",
                           "not_pinned": ["Distribution payload identities describe installed host bytes, not archived wheels or an offline installation bundle.",
                                          "Metadata dependency graph is a superset, prior import observations are an incomplete subset; task-conditional/dynamic imports require runtime evidence.",
                                          "Host catalog cannot identify Python/packages inside any container or actor snapshot.",
                                          "Future PATH, loader environment, import shadowing, actor mutation and trusted lifecycle/resource/cleanup remain unbound."]})

# Static ELF inspection only: rehash native files named in prior observations and resolve
# their NEEDED edges through the current ldconfig cache. Never execute ldd or a scorer binary.
elf_files = {str(Path(sys.executable).resolve())}
elf_files.update(str(stdlib / row["path"]) for row in stdlib_rows if row["path"].endswith(".so"))
for binary in ("/usr/lib/libreoffice/program/soffice.bin", "/usr/lib/libreoffice/program/libscfiltlo.so"):
    if Path(binary).is_file():
        elf_files.add(binary)
for observation in module_rows:
    for row in observation["current_files"]:
        if ".so" in Path(row["path"]).name and Path(row["path"]).is_file():
            elf_files.add(row["path"])
libpython = Path(sysconfig.get_config_var("LIBDIR")) / sysconfig.get_config_var("LDLIBRARY")
if libpython.is_file():
    elf_files.add(str(libpython))
cache = subprocess.run(["/sbin/ldconfig", "-p"], capture_output=True, text=True, check=True).stdout
locations = {}
for name, path in re.findall(r"^\s*(\S+)\s+\(.*\)\s+=>\s+(\S+)", cache, re.M):
    if "/x86_64-linux-gnu/" in path:
        locations.setdefault(name, path)
rows = []
pending = sorted(elf_files)
seen = set()
while pending:
    name = pending.pop(0)
    p = Path(name)
    if not p.is_file() or str(p.resolve()) in seen:
        continue
    seen.add(str(p.resolve()))
    probe = subprocess.run([shutil.which("readelf"), "-d", str(p)], capture_output=True, text=True)
    needed = re.findall(r"\(NEEDED\).*?\[(.*?)\]", probe.stdout)
    runpaths = re.findall(r"\((?:RUNPATH|RPATH)\).*?\[(.*?)\]", probe.stdout)
    edges = []
    for dep in needed:
        candidates = []
        for group in runpaths:
            for entry in group.split(":"):
                candidates.append(Path(entry.replace("${ORIGIN}", str(p.parent)).replace("$ORIGIN", str(p.parent))) / dep)
        candidates += [Path(sys.prefix) / "lib" / dep, Path(locations[dep])] if dep in locations else [Path(sys.prefix) / "lib" / dep]
        resolved = next((c for c in candidates if c.is_file()), None)
        edges.append({"soname": dep, "candidate": str(resolved) if resolved else None})
        if resolved:
            pending.append(str(resolved))
    rows.append({**file_record(p), "readelf_returncode": probe.returncode, "needed": edges, "runpaths": runpaths})
save("native-abi-byte-pins.json", {"note": "Static dependency candidates, not observed dynamic-loader resolution. dlopen, LD_LIBRARY_PATH, CPU/driver, task child processes and full system closure remain unverified.", "files": rows})
print(json.dumps({"host_distributions": len(packages), "installed": sum(r["installed"] for r in packages),
                  "historical_missing": sum(not r["exists"] for r in prior if "exists" in r),
                  "static_elf_files": len(rows), "benchmark_executions": 0}))
