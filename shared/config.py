import json, os
from dataclasses import dataclass
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
@dataclass(frozen=True)
class AppConfig:
    profile:str="local"; gemini_enabled:bool=False; gemini_model:str="gemini-3.6-flash"
    telemetry_enabled:bool=True; audit_log_path:str="runtime/audit_events.jsonl"
    history_limit:int=25; allow_advanced_json:bool=True

def load_config(profile=None):
    name=profile or os.getenv("APP_PROFILE","local")
    path=ROOT/"config"/"profiles"/f"{name}.json"
    if not path.exists(): raise ValueError(f"Unknown APP_PROFILE '{name}'. Use local, gemini, or demo.")
    data=json.loads(path.read_text(encoding="utf-8"))
    if os.getenv("ENABLE_GEMINI") is not None:
        data["gemini_enabled"]=os.getenv("ENABLE_GEMINI","false").lower()=="true"
    data["gemini_model"]=os.getenv("GEMINI_MODEL",data["gemini_model"])
    return AppConfig(**data)
