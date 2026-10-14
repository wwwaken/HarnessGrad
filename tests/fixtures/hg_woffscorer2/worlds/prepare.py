#!/usr/bin/env python3
"""Select one study ROM and recompute identities; does not execute a scorer."""
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

def identity(path):
    path = Path(path).resolve()
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    identities = {"interpreter": identity(sys.executable), "packages": {}, "local": {}}
    for name in ("jericho", "scienceworld", "py4j"):
        dist = importlib.metadata.distribution(name)
        package = Path(importlib.util.find_spec(name).origin).parent
        files = [identity(package / f) for f in sorted(p.name for p in package.iterdir())
                 if f.endswith((".py", ".so", ".jar", ".json"))]
        metadata = [identity(dist.locate_file(f)) for f in dist.files
                    if str(f).endswith(("/METADATA", "/RECORD", "/WHEEL"))]
        identities["packages"][name] = {"version": dist.version, "files": files,
                                       "metadata": metadata,
                                       "upstream_git_revision": None,
                                       "pin_kind": "installed distribution version and recomputed bytes"}
        source_dir = HERE / "official-source" / name
        source_dir.mkdir(parents=True, exist_ok=True)
        for p in package.glob("*.py"):
            if p.name != "game_info.py":
                shutil.copyfile(p, source_dir / p.name)
    for dataset, lib in (("jericho", "jer_env.py"), ("scienceworld", "scw_env.py")):
        identities["local"][dataset] = [identity(REPO / "data/datasets" / dataset / "verify/check.py"),
                                          identity(REPO / "data/datasets" / dataset / "lib" / lib)]
    rom = Path("/mnt/20t/xubuqiang/datasets/jericho/z-machine-games-master/jericho-game-suite/acorncourt.z5")
    shutil.copyfile(rom, HERE / "acorncourt.z5")
    identities["rom"] = identity(rom)
    jre = Path("/mnt/20t/xubuqiang/datasets/scienceworld/jre/jdk-17.0.20.1+1-jre")
    identities["java"] = [identity(jre / p) for p in ("bin/java", "lib/server/libjvm.so", "release")]
    identities["java_release"] = (jre / "release").read_text()
    from py4j.java_gateway import find_jar_path
    identities["py4j_java_archive"] = identity(find_jar_path())
    jar = Path(importlib.util.find_spec("scienceworld").origin).parent / "scienceworld.jar"
    with zipfile.ZipFile(jar) as archive:
        identities["jar_manifest"] = archive.read("META-INF/MANIFEST.MF").decode()
    fold = json.loads((REPO / "data/datasets/scienceworld/test_fold.json").read_text())
    identities["controlled_split"] = {
        "jericho_acorncourt_declared_hash_eval": hashlib.sha256(b"acorncourt").digest()[0] % 3 == 0,
        "scienceworld_task_3_find_non_living_thing_variation_0_in_test_fold": any(
            x["task_name"] == "task-3-find-non-living-thing" and x["variation"] == 0 for x in fold["tasks"]),
        "fold_source": identity(REPO / "data/datasets/scienceworld/test_fold.json")}
    (HERE / "identities.json").write_text(json.dumps(identities, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
