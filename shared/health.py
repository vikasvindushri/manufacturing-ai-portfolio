from pathlib import Path
from .config import ROOT

def system_health(cfg,gemini_enabled=False):
    kb=ROOT/"project_2_rag"/"knowledge_base";docs=list(kb.glob("*.md")) if kb.exists() else []
    checks=[
      {"component":"Quality local engine","status":"Available","core":True},
      {"component":"Knowledge retrieval engine","status":"Available" if docs else "Unavailable","core":True},
      {"component":"Fault local engine","status":"Available","core":True},
      {"component":"Knowledge base","status":f"{len(docs)} document(s)","core":True},
      {"component":"Gemini configuration","status":"Enabled" if cfg.gemini_enabled else "Disabled","core":False},
      {"component":"Gemini credentials","status":"Detected" if gemini_enabled else "Not active","core":False},
      {"component":"Audit logging","status":"Enabled" if cfg.telemetry_enabled else "Disabled","core":False},
      {"component":"Environment profile","status":cfg.profile,"core":False},
    ]
    return checks
