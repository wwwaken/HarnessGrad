import json, sys
from execution import check_correctness
program=json.loads(open(sys.argv[1]).read())
print(json.dumps(check_correctness(program, timeout=120)))
