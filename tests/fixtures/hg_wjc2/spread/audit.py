#!/usr/bin/env python3
"""Read-only digest/member comparison; --check refuses changed preimages/results."""
import ast,base64,collections,hashlib,json,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sys.path.insert(0,str(REPO))
from data.datasets import spreadsheetbench as ds
ORIGINAL=Path("/tmp/hg-jc2-spread-original-all_data_912.tar.gz")
MIRROR=ds.DATASET_ROOT/"_src"/ds.TARBALL
CANONICAL=Path("/tmp/hg-jc2-spread-canonical-verified_400.tar.gz")

def sha(b): return hashlib.sha256(b).hexdigest()
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def describe(p):
 b=p.read_bytes();return {"path":str(p),"bytes":len(b),"sha256":sha(b),"git_blob_sha1":blob(b)}
def emit(name,value):
 out=json.dumps(value,indent=2,ensure_ascii=False)+"\n";path=ROOT/name
 if "--check" in sys.argv: assert path.read_text()==out,name+" differs"
 else:path.write_text(out)
 return value

def audit():
 original=describe(ORIGINAL);mirror=describe(MIRROR);canonical=describe(CANONICAL)
 canonical_api=json.loads((ROOT/"responses/github-release-archive-metadata-pinned.body").read_text())
 commit=json.loads((ROOT/"responses/github-main-commit.body").read_text())
 tree=json.loads((ROOT/"responses/github-release-tree-pinned.body").read_text())
 archive_entry=next(x for x in tree["tree"] if x["path"]==canonical_api["path"])
 assert canonical["git_blob_sha1"]==canonical_api["sha"]==archive_entry["sha"]==mirror["git_blob_sha1"]
 assert canonical["bytes"]==canonical_api["size"]==archive_entry["size"]==mirror["bytes"]
 assert canonical["sha256"]==mirror["sha256"]
 assert CANONICAL.read_bytes()==MIRROR.read_bytes()
 readme_api=json.loads((ROOT/"responses/github-release-readme-pinned.body").read_text())
 readme=(ROOT/"responses/github-release-readme-pinned.decoded.md").read_bytes()
 assert blob(readme)==readme_api["sha"]==next(x for x in tree["tree"] if x["path"]=="README.md")["sha"]
 api=json.loads((ROOT/"responses/github-original-metadata.body").read_text())
 assert original["git_blob_sha1"]==api["sha"] and original["bytes"]==api["size"]
 hub=json.loads((ROOT/"responses/hub-tree-proxy.body").read_text())
 pinned=next(r for r in hub if r["path"]==ds.TARBALL)
 assert mirror["sha256"]==ds.TARBALL_SHA256==pinned["lfs"]["oid"]
 assert mirror["bytes"]==pinned["size"]
 with tarfile.open(ORIGINAL) as ot,tarfile.open(MIRROR) as mt,tarfile.open(CANONICAL) as ct:
  mirror_members={m.name:mt.extractfile(m).read() for m in mt.getmembers() if m.isfile()}
  canonical_members={m.name:ct.extractfile(m).read() for m in ct.getmembers() if m.isfile()}
  original_files={};original_hash_to_member=collections.defaultdict(list)
  for m in ot.getmembers():
   if m.isfile() and not Path(m.name).name.startswith("._"):
    b=ot.extractfile(m).read();original_files[m.name]={"bytes":len(b),"sha256":sha(b)}
    if m.name.endswith(".xlsx"):original_hash_to_member[sha(b)].append(m.name)
  meta_b=ot.extractfile("all_data_912/dataset.json").read();original_rows=json.loads(meta_b)
  original_by_id={str(r["id"]):r for r in original_rows}
  assert len(original_by_id)==len(original_rows)
  local_meta=ds.DATASET_ROOT/ds.TASKS_JSON;local_meta_b=local_meta.read_bytes()
  assert mirror_members[ds.TASKS_JSON]==canonical_members[ds.TASKS_JSON]==local_meta_b
  local_rows=json.loads(local_meta_b);tasks=ds._tasks()
  official_api=json.loads((REPO/"reports/w-spread2-evidence/official-source-response.json").read_text())
  official_b=base64.b64decode(official_api["content"])
  current_scorer=next(x for x in tree["tree"] if x["path"]=="evaluation/evaluation.py")
  assert blob(official_b)==official_api["sha"]==current_scorer["sha"]
  code=ast.parse(official_b);selected={"parse_cell_range","col_name2num","col_num2name"}
  isolated=ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in selected],type_ignores=[])
  ns={};exec(compile(isolated,"official-parser-only","exec"),ns)
  bad=[];colon=0;single=0
  for record in local_rows:
   for position in str(record["answer_position"]).split(","):
    rng=position.split("!")[-1].lstrip("\'").rstrip("\'")
    if ":" not in rng:single+=1;continue
    colon+=1
    try:ns["parse_cell_range"](rng)
    except Exception as e:bad.append({"task_id":str(record["id"]),"range":rng,"exception":type(e).__name__+": "+str(e)})
  emit("parser-audit.json",{"scope":"official parser function only; no workbook execution or benchmark trial","canonical_pinned_scorer_blob":current_scorer["sha"],"official_source_sha256":sha(official_b),"metadata_rows":len(local_rows),"colon_components":colon,"single_cell_components":single,"rejected_components":bad,"rejected_tasks":len(set(x["task_id"] for x in bad)),"single_variant_contract":"one deterministic init/golden pair per installed task; no soft/hard aggregation"})
  by_id={r["task_id"]:r for r in tasks};rows=[]
  fields=collections.Counter();all_equal=0;workbook_matches=0;workbook_unmatched=0;first_variant_matches=0
  for i,r in enumerate(local_rows):
   id=str(r["id"]);old=original_by_id.get(id)
   changed=[] if old is None else sorted(k for k in set(r)|set(old) if r.get(k)!=old.get(k))
   fields.update(changed);all_equal+=old is not None and not changed
   row={"task_id":id,"mirror_position":i,"original_position":next((j for j,x in enumerate(original_rows) if str(x["id"])==id),None),"mirror_parsed_row_sha256":sha(canon(r)),"original_parsed_row_sha256":None if old is None else sha(canon(old)),"metadata_equal":old==r,"changed_fields":changed,"workbooks":{}}
   for kind,upstream_kind in [("init","input"),("golden","answer")]:
    path=by_id[id][kind+"_path"];b=path.read_bytes();h=sha(b)
    member=str(path.relative_to(ds.DATASET_ROOT));assert mirror_members[member]==canonical_members[member]==b
    folder="all_data_912/"+str(old["spreadsheet_path"]) if old else None
    original_candidates=[n for n in original_files if folder and n.startswith(folder+"/") and n.endswith("_"+upstream_kind+".xlsx") and not Path(n).name.startswith("._")]
    first_candidates=[n for n in original_candidates if Path(n).name.startswith("1_")]
    matched=[n for n in original_hash_to_member[h] if n in original_candidates]
    first_matched=[n for n in matched if n in first_candidates]
    workbook_matches+=bool(matched);workbook_unmatched+=not bool(matched);first_variant_matches+=bool(first_matched)
    row["workbooks"][kind]={"installed_path":str(path),"mirror_member":member,"bytes":len(b),"sha256":h,"mirror_member_equal":True,"canonical_upstream_member":member,"canonical_upstream_member_sha256":sha(canonical_members[member]),"canonical_upstream_member_equal":True,"original_first_variant_candidates":[{"member":n,**original_files[n]} for n in sorted(first_candidates)],"same_task_exact_matches":matched,"first_variant_exact_matches":first_matched,"all_archive_exact_matches":original_hash_to_member[h]}
   if id=="283-32":row["released_parser_rejected_identity"]={"mirror_answer_position":r["answer_position"],"original_answer_position":None if old is None else old["answer_position"],"answer_position_equal":old is not None and r["answer_position"]==old["answer_position"],"mirror_row":r,"original_row":old,"parser_audit":"reports/w-spread2-evidence/audit-output.txt"}
   rows.append(row)
  emit("member-mapping.json",{"rows":rows})
  summary={"canonical_verified_400_archive":canonical,"canonical_verified_400_commit":commit["sha"],"canonical_verified_400_git_blob":canonical_api["sha"],"canonical_verified_400_archive_byte_equal_to_mirror":True,"canonical_verified_400_readme":{"sha256":sha(readme),"git_blob_sha1":blob(readme)},"canonical_upstream_metadata_and_chosen_members_byte_equal":True,"original_archive":original,"canonical_github_blob_identity_matches":True,"mirror_archive":mirror,"canonical_hub_lfs_identity_matches":True,"original_metadata_member":{"member":"all_data_912/dataset.json","bytes":len(meta_b),"sha256":sha(meta_b)},"mirror_metadata":{"path":str(local_meta),"member":ds.TASKS_JSON,"bytes":len(local_meta_b),"sha256":sha(local_meta_b),"archive_equal":True},"original_rows":len(original_rows),"mirror_rows":len(local_rows),"mirror_ids_missing_from_original":[str(r["id"]) for r in local_rows if str(r["id"]) not in original_by_id],"metadata_rows_equal":all_equal,"metadata_rows_changed":len(rows)-all_equal,"changed_field_counts":dict(sorted(fields.items())),"chosen_workbook_count":sum(len(r["workbooks"]) for r in rows),"chosen_workbooks_same_task_original_exact_match":workbook_matches,"chosen_workbooks_same_task_original_unmatched":workbook_unmatched,"chosen_workbooks_first_variant_exact_match":first_variant_matches,"actual_run_fields":{"selected_manifest":None,"run_id":None,"chosen_split_mode":None,"chosen_side":None,"selected_only_export":None},"mirror_to_canonical_verified_400_mapping_authenticated":True,"historical_912_transformation_record_authenticated":False,"row_level_gradability_authenticated":False,"production_authorized":False}
  emit("summary.json",summary)
  print(json.dumps(summary,indent=2))
if __name__=="__main__":audit()
