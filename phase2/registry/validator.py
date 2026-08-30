import json
from pydantic import ValidationError
from phase2.models import WorkflowDefinition
from .compatibility import check_definition_version
def validate_payload(p):
 if not isinstance(p,dict):return {"valid":False,"errors":[{"path":"$","code":"INVALID_ROOT","message":"workflow must be an object"}],"warnings":[]}
 v=(p.get("metadata") or {}).get("definition_version") if isinstance(p.get("metadata"),dict) else None;c=check_definition_version(v)
 if not c.compatible:return {"valid":False,"errors":[{"path":"metadata.definition_version","code":c.code,"message":c.message}],"warnings":[]}
 try:model=WorkflowDefinition.model_validate(p)
 except ValidationError as e:return {"valid":False,"errors":[{"path":".".join(map(str,x["loc"])) or "$","code":x["type"].upper(),"message":x["msg"]} for x in e.errors(include_url=False)],"warnings":[]}
 return {"valid":True,"errors":[],"warnings":[],"workflow":model}
def validate_json_text(t):
 try:return validate_payload(json.loads(t))
 except json.JSONDecodeError as e:return {"valid":False,"errors":[{"path":"$","code":"INVALID_JSON","message":f"line {e.lineno}, column {e.colno}: {e.msg}"}],"warnings":[]}
