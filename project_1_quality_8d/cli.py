import argparse,json
from pathlib import Path
from .engine import build_8d
p=argparse.ArgumentParser(); p.add_argument("--incident",required=True); p.add_argument("--output")
a=p.parse_args(); result=build_8d(json.loads(Path(a.incident).read_text()))
text=json.dumps(result,indent=2); print(text)
if a.output: Path(a.output).write_text(text)
