from dataclasses import dataclass
import re
SUPPORTED_MAJOR=1;SUPPORTED_MINOR=1
@dataclass(frozen=True)
class CompatibilityResult:compatible:bool;code:str;message:str
def check_definition_version(v):
 if not v:return CompatibilityResult(False,"MISSING_VERSION","definition_version is required")
 m=re.fullmatch(r"(\d+)\.(\d+)",v)
 if not m:return CompatibilityResult(False,"MALFORMED_VERSION","definition_version must use major.minor format")
 major,minor=map(int,m.groups())
 if major!=SUPPORTED_MAJOR:return CompatibilityResult(False,"UNSUPPORTED_MAJOR",f"definition major {major} is unsupported")
 if minor>SUPPORTED_MINOR:return CompatibilityResult(False,"NEWER_MINOR",f"definition minor {minor} is newer than supported {SUPPORTED_MINOR}")
 return CompatibilityResult(True,"SUPPORTED","definition version is supported")
