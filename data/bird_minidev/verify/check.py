import argparse,json,sqlite3
from pathlib import Path
def rows(db,sql):
 c=sqlite3.connect(db); r=c.execute(sql).fetchall(); c.close(); return set(r)
def main():
 p=argparse.ArgumentParser();p.add_argument('--db');p.add_argument('--gold');p.add_argument('--pred');p.add_argument('--reward-file');p.add_argument('--evidence-file');a=p.parse_args()
 try: score=1.0 if rows(a.db,Path(a.pred).read_text())==rows(a.db,Path(a.gold).read_text()) else 0.0; why='exact set equality (official EX)'
 except Exception as e: score=0.;why=f'query error: {e}'
 Path(a.reward_file).parent.mkdir(parents=True,exist_ok=True);Path(a.reward_file).write_text(str(score));Path(a.evidence_file).write_text(json.dumps({'measured':True,'metric':'EX','reward':score,'why':why}));print(why);return 0 if score else 1
if __name__=='__main__': raise SystemExit(main())
