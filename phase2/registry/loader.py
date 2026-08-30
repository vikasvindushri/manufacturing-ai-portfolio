from pathlib import Path
from .validator import validate_json_text
MAX_DEFINITION_BYTES=1_000_000
class WorkflowLoadError(ValueError):pass
def load_workflow_text(t):
 if len(t.encode())>MAX_DEFINITION_BYTES:raise WorkflowLoadError("workflow definition exceeds the 1 MB limit")
 r=validate_json_text(t)
 if not r["valid"]:raise WorkflowLoadError("; ".join(f"{x['path']}: {x['message']}" for x in r["errors"]))
 return r["workflow"]
def load_workflow(path):
 p=Path(path)
 if p.suffix.lower()!=".json":raise WorkflowLoadError("workflow definitions must use the .json extension")
 if not p.is_file():raise WorkflowLoadError(f"workflow definition not found: {p}")
 return load_workflow_text(p.read_text(encoding="utf-8"))
