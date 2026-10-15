#!/usr/bin/env python3
"""Offline validation only; never execute generators or scorers."""
import hashlib, json, pathlib
root=pathlib.Path(__file__).resolve().parent
repo=root.parents[3]
commands=list(root.glob("*.command.json"))
for command in commands:
    record=json.loads(command.read_text())
    name=command.name.removesuffix(".command.json")
    for stream in ("stdout", "stderr"):
        body=root.joinpath(name+"."+stream+".txt").read_bytes()
        if record.get(stream+"_storage")=="json-quoted-lines":
            body="".join(json.loads(line) for line in body.decode().splitlines()).encode()
        assert hashlib.sha256(body).hexdigest()==record[stream+"_sha256"], (name,stream)
observation=json.loads(root.joinpath("observations.json").read_text())
pool=pathlib.Path(observation["pool"]["path"]).read_bytes()
assert hashlib.sha256(pool).hexdigest()==observation["pool"]["sha256"]
rows=[json.loads(line) for line in pool.splitlines()]
assert len(pool)==observation["pool"]["size"] and len(rows)==observation["pool"]["rows"]
selected=[]
for i,row in enumerate(rows,1):
    if row["family"]=="time_intervals" and row["entry"]["metadata"]["task_type"] in ("time", "time_seconds", "time_ms"):
        m=row["entry"]["metadata"]
        selected.append({"pool_line":i,"index":row["index"],"task_type":m["task_type"],"start_time":m["start_time"],"end_time":m["end_time"]})
assert selected==observation["time_only_metadata_rows"]
assert len(selected)==observation["time_only_metadata_rows_count"]
for key,prefix in (("effective_start_dates","start_time"),("effective_end_dates","end_time")):
    assert sorted({row[prefix].split()[0] for row in selected})==observation[key]
for file in observation["files"]:
    path=root/file["captured_as"] if "captured_as" in file else pathlib.Path(file["path"])
    if not path.is_absolute(): path=repo/path
    body=path.read_bytes()
    assert len(body)==file["size"] and hashlib.sha256(body).hexdigest()==file["sha256"], path
assert observation["original_generation_record_recovered"] is False
assert observation["original_process_hash_seed"] is None and observation["original_dependency_lock"] is None
assert observation["generation_rerun"] is False and observation["network_or_endpoint_contact"] is False
print(json.dumps({"command_receipts_verified":len(commands),"pool_sha256":hashlib.sha256(pool).hexdigest(),"pool_rows":len(rows),"effective_time_only_rows":len(selected),"effective_start_dates":observation["effective_start_dates"],"source_or_historical_files_verified":len(observation["files"]),"original_generation_record_recovered":False},sort_keys=True))
