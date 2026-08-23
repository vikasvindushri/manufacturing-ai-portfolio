import json, uuid
from datetime import datetime,timezone
from pathlib import Path
from .config import ROOT
SENSITIVE={"description","symptoms","immediate_action","reported_by","owner","raw_json","api_key"}
def _safe(data):
    if not isinstance(data,dict): return data
    return {k:("[REDACTED]" if k.lower() in SENSITIVE else v) for k,v in data.items()}
def audit_event(event_type,product,status="success",metadata=None,path="runtime/audit_events.jsonl",enabled=True):
    event={"event_id":str(uuid.uuid4()),"timestamp_utc":datetime.now(timezone.utc).isoformat(),
           "event_type":event_type,"product":product,"status":status,"metadata":_safe(metadata or {})}
    if enabled:
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("a",encoding="utf-8") as f:f.write(json.dumps(event)+"\n")
    return event
