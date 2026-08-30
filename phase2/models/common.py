import re
from enum import Enum
from typing import Any
from pydantic import BaseModel,ConfigDict
ID_PATTERN=re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
SEMVER_PATTERN=r"^\d+\.\d+\.\d+$"
SECRET_KEYS={"api_key","apikey","password","secret","token","access_token","private_key","client_secret","connection_string","gemini_api_key","google_api_key"}
class StrictModel(BaseModel):model_config=ConfigDict(extra="forbid",str_strip_whitespace=True)
class LifecycleStatus(str,Enum):
 DRAFT="draft";IN_REVIEW="in_review";APPROVED="approved";PUBLISHED="published";ARCHIVED="archived"
def valid_id(v,label):
 if not ID_PATTERN.fullmatch(v):raise ValueError(f"{label} must match {ID_PATTERN.pattern}")
 return v
def find_secret_paths(v,path=""):
 out=[]
 if isinstance(v,dict):
  for k,x in v.items():
   child=f"{path}.{k}" if path else str(k)
   if str(k).lower() in SECRET_KEYS:out.append(child)
   out+=find_secret_paths(x,child)
 elif isinstance(v,list):
  for i,x in enumerate(v):out+=find_secret_paths(x,f"{path}[{i}]")
 return out
