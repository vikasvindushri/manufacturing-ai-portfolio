import argparse,json
from pathlib import Path
from .agent import triage
p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--output")
a=p.parse_args();r=triage(json.loads(Path(a.input).read_text()));t=json.dumps(r,indent=2);print(t)
if a.output: Path(a.output).write_text(t)
