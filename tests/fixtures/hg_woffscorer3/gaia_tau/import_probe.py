import json,sys,traceback
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'source'))
try:
    import tau_bench.envs.base as base
    print(json.dumps({'full_import':True,'path':base.__file__}))
except Exception as exc:
    print(json.dumps({'full_import':False,'exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}))
