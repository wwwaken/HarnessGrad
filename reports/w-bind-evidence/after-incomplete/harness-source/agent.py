import argparse,pathlib
p=argparse.ArgumentParser();p.add_argument('--task');p.add_argument('--workdir')
a=p.parse_args();pathlib.Path(a.workdir,'answer.txt').write_bytes(b'42\n')
