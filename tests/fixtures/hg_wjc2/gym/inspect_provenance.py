#!/usr/bin/env python3
"""Read provenance only: never imports reasoning_gym or executes a generator."""
import datetime, hashlib, importlib.metadata, json, pathlib, subprocess, zipfile
out = pathlib.Path(__file__).resolve().parent
repo = out.parents[3]
installed = pathlib.Path("/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl")
body = installed.read_bytes()
rows = [json.loads(line) for line in body.splitlines()]
time_rows = [{"pool_line":i,"index":r["index"],"task_type":r["entry"]["metadata"]["task_type"],"start_time":r["entry"]["metadata"]["start_time"],"end_time":r["entry"]["metadata"]["end_time"]} for i,r in enumerate(rows,1) if r["family"]=="time_intervals" and r["entry"]["metadata"]["task_type"] in ("time", "time_seconds", "time_ms")]
dist = importlib.metadata.distribution("reasoning_gym")
package = pathlib.Path(dist.locate_file("reasoning_gym"))
paths = [package / name for name in ("arithmetic/time_intervals.py", "algebra/polynomial_multiplication.py", "algorithmic/isomorphic_strings.py", "algorithmic/ransom_note.py", "games/knight_swap.py", "algorithmic/word_ladder.py")]
metadata = pathlib.Path(dist.locate_file("reasoning_gym-0.1.25.dist-info/METADATA"))
paths += [repo / "data/datasets/reasoning_gym/prepare.py", repo / "data/datasets/reasoning_gym.py", metadata, pathlib.Path("/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/dateutil/parser/_parser.py")]
files=[]
lines=[]
for path in paths:
    data=path.read_bytes()
    label = str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path)
    files.append({"path":label, "size":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    lines.append("FILE " + label)
    lines.extend(f"{label}:{i}: {json.dumps(line,ensure_ascii=False)}" for i,line in enumerate(data.decode().splitlines(),1))
out.joinpath("source-lines.txt").write_text("\n".join(lines)+"\n")
commit="0f47b1240c739fefb0472e4f73ac71a2c8b6d927"
for old in ("data/reasoning_gym/prepare.py", "data/reasoning_gym.py"):
    command=["git","show",commit+":"+old]
    result=subprocess.run(command,capture_output=True,check=True)
    filename="original-"+pathlib.Path(old).name
    out.joinpath(filename).write_bytes(result.stdout)
    files.append({"path":commit+":"+old,"captured_as":filename,"size":len(result.stdout),"sha256":hashlib.sha256(result.stdout).hexdigest(),"argv":command})
stat=installed.stat()
observation={"pool":{"path":str(installed),"size":len(body),"sha256":hashlib.sha256(body).hexdigest(),"rows":len(rows),"mtime_ns":stat.st_mtime_ns,"mtime_utc":datetime.datetime.fromtimestamp(stat.st_mtime,datetime.timezone.utc).isoformat(),"ctime_ns":stat.st_ctime_ns,"ctime_utc":datetime.datetime.fromtimestamp(stat.st_ctime,datetime.timezone.utc).isoformat()},"time_only_metadata_rows":time_rows,"time_only_metadata_rows_count":len(time_rows),"effective_start_dates":sorted({r["start_time"].split()[0] for r in time_rows}),"effective_end_dates":sorted({r["end_time"].split()[0] for r in time_rows}),"files":files,"original_generation_record_recovered":False,"original_process_hash_seed":None,"original_dependency_lock":None,"generation_rerun":False,"network_or_endpoint_contact":False}
out.joinpath("observations.json").write_text(json.dumps(observation,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(observation,indent=2,ensure_ascii=False))
